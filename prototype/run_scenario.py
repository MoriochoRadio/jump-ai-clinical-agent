"""Run a local deterministic prototype workflow for a protocol scenario.

By default this script avoids external APIs, LLM calls, and third-party
dependencies. Optional flags can fetch public ClinicalTrials.gov and PubMed
records while keeping all outputs traceable for GitHub review.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version",
    "scenario_id",
    "scenario_name",
    "source_markdown",
    "data_safety",
    "required_fields",
    "optional_fields",
    "expected_agent_checks",
    "expected_failure_modes",
    "evaluation",
]

REQUIRED_PROTOCOL_FIELDS = [
    "disease_condition",
    "intervention_or_drug_class",
    "trial_phase",
    "trial_objective",
    "target_population",
    "draft_inclusion_criteria",
    "draft_exclusion_criteria",
    "primary_endpoint",
    "secondary_endpoints",
    "expected_data_collection_items",
]

FORBIDDEN_CLAIM_PATTERNS = [
    (r"\bis approved\b", "possible protocol approval claim"),
    (r"\bapproved protocol\b", "possible protocol approval claim"),
    (r"\bregulatory compliant\b", "possible regulatory compliance claim"),
    (r"\bcomplies with all regulatory\b", "possible regulatory compliance claim"),
    (r"\bguarantee[s]?\b.*\brecruit", "possible recruitment guarantee"),
    (r"\brecommend[s]?\b.*\btreatment\b", "possible patient-specific treatment recommendation"),
    (r"\breal patient data\b.*\brequired\b", "possible real patient data requirement"),
]

DEFAULT_REPRESENTATIVE_INTERVENTION_TERMS = [
    "semaglutide",
    "liraglutide",
    "dulaglutide",
    "exenatide",
]

DEFAULT_RANKING_PROFILE = {
    "condition_terms": ["type 2 diabetes", "t2dm", "diabetes mellitus, type 2", "diabetes"],
    "intervention_terms": [
        "glp-1 receptor agonist",
        "glp1 receptor agonist",
        "glp-1ra",
        "glp1 ra",
        "exenatide",
        "semaglutide",
        "liraglutide",
        "dulaglutide",
        "lixisenatide",
        "albiglutide",
    ],
    "adjacent_intervention_terms": ["glp-1", "glp1", "gpr119", "incretin"],
    "endpoint_terms": ["hba1c", "a1c", "weight", "glucose", "glycemic", "glycaemic", "metabolic", "adverse", "safety"],
    "eligibility_terms": ["hba1c", "a1c", "egfr", "renal", "kidney", "pregnancy", "pancreatitis", "insulin", "glp"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic local workflow for a protocol scenario."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a scenario JSON fixture.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run identifier used as the output folder name.",
    )
    parser.add_argument(
        "--output-root",
        default="prototype/runs",
        help="Folder where run outputs are written. Defaults to prototype/runs.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing run folder.",
    )
    parser.add_argument(
        "--fetch-sources",
        action="store_true",
        help="Fetch live ClinicalTrials.gov records and write sources.json.",
    )
    parser.add_argument(
        "--fetch-pubmed",
        action="store_true",
        help="Fetch live PubMed literature candidates and write pubmed_sources.json.",
    )
    parser.add_argument(
        "--max-studies",
        type=int,
        default=5,
        help="Maximum number of ClinicalTrials.gov studies to request per query. Defaults to 5.",
    )
    parser.add_argument(
        "--source-timeout",
        type=int,
        default=20,
        help="Public source request timeout in seconds. Defaults to 20.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise SystemExit(f"Input file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from None

    if not isinstance(data, dict):
        raise SystemExit("Scenario fixture must be a JSON object.")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def validate_fixture(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    required_fields = data.get("required_fields", {})
    if not isinstance(required_fields, dict):
        errors.append("required_fields must be an object.")
        return errors

    for key in REQUIRED_PROTOCOL_FIELDS:
        value = required_fields.get(key)
        if value in (None, "", []):
            errors.append(f"Missing required protocol field: {key}")

    safety = data.get("data_safety", {})
    if not isinstance(safety, dict):
        errors.append("data_safety must be an object.")
    else:
        if safety.get("contains_real_patient_data") is not False:
            errors.append("contains_real_patient_data must be false for the MVP fixture.")
        if safety.get("contains_identifiable_data") is not False:
            errors.append("contains_identifiable_data must be false for the MVP fixture.")

    return errors


def make_normalized_input(data: dict[str, Any], input_path: Path, run_id: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path.as_posix()),
        "schema_version": data["schema_version"],
        "scenario_id": data["scenario_id"],
        "scenario_name": data["scenario_name"],
        "source_markdown": data["source_markdown"],
        "data_safety": data["data_safety"],
        "protocol": data["required_fields"],
        "optional_context": data["optional_fields"],
        "expected_agent_checks": data["expected_agent_checks"],
        "expected_failure_modes": data["expected_failure_modes"],
        "evaluation": data["evaluation"],
    }


def has_numeric_threshold(text: str) -> bool:
    cleaned = re.sub(r"hba1c|glp-?1", "", text, flags=re.IGNORECASE)
    return bool(re.search(r"\d", cleaned))


def scenario_heading(normalized: dict[str, Any], suffix: str) -> str:
    return f"{normalized['scenario_id']} {suffix}"


def get_ranking_profile(normalized: dict[str, Any]) -> dict[str, list[str]]:
    optional_context = normalized.get("optional_context", {})
    configured = optional_context.get("ranking_profile", {})
    profile: dict[str, list[str]] = {}
    for key, defaults in DEFAULT_RANKING_PROFILE.items():
        value = configured.get(key, defaults)
        profile[key] = [str(item).lower() for item in value]
    return profile


def collect_criteria(protocol: dict[str, Any]) -> tuple[list[str], list[str]]:
    inclusion = protocol.get("draft_inclusion_criteria", [])
    exclusion = protocol.get("draft_exclusion_criteria", [])
    return list(inclusion or []), list(exclusion or [])


def make_checklist_findings(normalized: dict[str, Any]) -> dict[str, Any]:
    protocol = normalized["protocol"]
    optional_context = normalized["optional_context"]
    inclusion, exclusion = collect_criteria(protocol)
    all_criteria_text = " ".join(inclusion + exclusion).lower()

    field_presence = []
    for key in REQUIRED_PROTOCOL_FIELDS:
        value = protocol.get(key)
        status = "present" if value not in (None, "", []) else "missing"
        field_presence.append({"field": key, "status": status})

    findings = []

    hba1c_items = [item for item in inclusion if "hba1c" in item.lower()]
    if any("above target" in item.lower() and not has_numeric_threshold(item) for item in hba1c_items):
        findings.append(
            {
                "id": "ambiguous_hba1c_threshold",
                "severity": "high",
                "finding": "HbA1c eligibility threshold is ambiguous.",
                "evidence": hba1c_items,
                "recommendation": "Define an exact HbA1c range or threshold for eligibility.",
            }
        )

    renal_items = [item for item in exclusion if "renal" in item.lower() or "kidney" in item.lower()]
    renal_text = " ".join(renal_items).lower()
    if renal_items and not any(term in renal_text for term in ["egfr", "crcl", "creatinine clearance"]):
        findings.append(
            {
                "id": "ambiguous_renal_threshold",
                "severity": "high",
                "finding": "Renal impairment exclusion criterion lacks an operational threshold.",
                "evidence": renal_items,
                "recommendation": "Define the threshold using eGFR, creatinine clearance, or another measurable criterion.",
            }
        )

    if not any(term in all_criteria_text for term in ["randomized", "randomised", "blinding", "blind", "placebo", "comparator", "single-arm"]):
        findings.append(
            {
                "id": "missing_study_design",
                "severity": "high",
                "finding": "Study design, randomization, blinding, and comparator details are not specified.",
                "evidence": "No structured study design field or criterion-level design detail found.",
                "recommendation": "Clarify whether the study is randomized, blinded, placebo-controlled, active-comparator, or single-arm.",
            }
        )

    recruitment = optional_context.get("recruitment_assumption", "")
    if recruitment and not any(term in recruitment.lower() for term in ["rationale", "based on", "historical", "screening log"]):
        findings.append(
            {
                "id": "missing_sample_size_or_recruitment_rationale",
                "severity": "medium",
                "finding": "Recruitment assumption is provided without feasibility rationale.",
                "evidence": recruitment,
                "recommendation": "Add screening pool, historical recruitment rate, or site feasibility evidence.",
            }
        )

    injectable_items = [
        item
        for item in exclusion
        if "injectable" in item.lower() and ("therapy" in item.lower() or "diabetes" in item.lower())
    ]
    if injectable_items:
        findings.append(
            {
                "id": "injectable_therapy_exclusion_recruitment_pool",
                "severity": "medium",
                "finding": "Current injectable diabetes therapy exclusion may reduce the eligible recruitment pool.",
                "evidence": injectable_items,
                "recommendation": "Estimate how many otherwise eligible patients would be excluded and clarify whether this criterion is clinically necessary.",
            }
        )

    follow_up_items = [
        item
        for item in inclusion
        if ("follow-up" in item.lower() or "follow up" in item.lower() or "visit" in item.lower())
        and ("able" in item.lower() or "attend" in item.lower())
    ]
    if follow_up_items:
        findings.append(
            {
                "id": "follow_up_attendance_operational_definition",
                "severity": "medium",
                "finding": "Follow-up visit attendance criterion needs an operational definition.",
                "evidence": follow_up_items,
                "recommendation": "Define required visit windows, acceptable missed visits, remote visit options, and how attendance feasibility will be assessed.",
            }
        )

    if "safety" not in json.dumps(protocol).lower() and "monitor" not in json.dumps(protocol).lower():
        findings.append(
            {
                "id": "missing_safety_monitoring_plan",
                "severity": "high",
                "finding": "Safety monitoring plan is not specified.",
                "evidence": "No safety monitoring field or monitoring process found.",
                "recommendation": "Clarify adverse event review, safety labs, stopping rules if applicable, and responsible reviewers.",
            }
        )

    protocol_text = json.dumps(protocol).lower()
    is_glp1_scenario = "glp-1" in protocol_text or "glp1" in protocol_text
    if is_glp1_scenario and "glp-1" not in all_criteria_text and "glp" not in all_criteria_text:
        findings.append(
            {
                "id": "unclear_prior_glp1_exposure",
                "severity": "medium",
                "finding": "Prior GLP-1 receptor agonist exposure is not addressed in eligibility criteria.",
                "evidence": "No inclusion or exclusion criterion refers to prior GLP-1 receptor agonist exposure.",
                "recommendation": "Clarify whether prior or recent GLP-1 receptor agonist use is allowed, excluded, or stratified.",
            }
        )

    immunotherapy_terms = ["pd-1", "pd-l1", "checkpoint", "pembrolizumab", "nivolumab", "atezolizumab", "durvalumab"]
    is_checkpoint_scenario = any(term in protocol_text for term in immunotherapy_terms)
    if is_checkpoint_scenario:
        if not any(term in all_criteria_text for term in ["ecog", "performance status"]):
            findings.append(
                {
                    "id": "missing_performance_status_definition",
                    "severity": "high",
                    "finding": "Performance status eligibility is not operationally defined.",
                    "evidence": "No ECOG or performance status criterion found.",
                    "recommendation": "Define the accepted ECOG performance status range and how it will be documented.",
                }
            )
        if not any(term in all_criteria_text for term in ["recist", "measurable disease"]):
            findings.append(
                {
                    "id": "missing_measurable_disease_definition",
                    "severity": "high",
                    "finding": "Measurable disease requirement is not defined.",
                    "evidence": "No RECIST or measurable disease criterion found.",
                    "recommendation": "Clarify whether measurable disease is required and which response assessment standard will be used.",
                }
            )
        if not any(term in all_criteria_text for term in ["egfr", "alk", "ros1", "pd-l1", "pdl1", "biomarker"]):
            findings.append(
                {
                    "id": "missing_biomarker_rules",
                    "severity": "high",
                    "finding": "Biomarker and molecular eligibility rules are unclear.",
                    "evidence": "No EGFR, ALK, ROS1, PD-L1, or biomarker criterion found.",
                    "recommendation": "Define required biomarker testing, exclusion rules, and how missing results will be handled.",
                }
            )
        if not any(term in all_criteria_text for term in ["autoimmune", "steroid", "immunosuppress"]):
            findings.append(
                {
                    "id": "missing_immunotherapy_safety_exclusions",
                    "severity": "medium",
                    "finding": "Checkpoint-inhibitor safety exclusions are incomplete.",
                    "evidence": "No autoimmune disease, steroid, or immunosuppression criterion found.",
                    "recommendation": "Clarify autoimmune disease, immunosuppressive therapy, and steroid-use exclusions or monitoring rules.",
                }
            )
        if "prior" not in all_criteria_text or not any(term in all_criteria_text for term in ["pd-1", "pd-l1", "checkpoint", "immunotherapy"]):
            findings.append(
                {
                    "id": "unclear_prior_checkpoint_exposure",
                    "severity": "medium",
                    "finding": "Prior checkpoint inhibitor exposure is not clearly addressed.",
                    "evidence": "Eligibility criteria do not clearly state whether prior PD-1/PD-L1 or checkpoint inhibitor therapy is allowed.",
                    "recommendation": "Clarify prior immunotherapy exposure rules and washout requirements.",
                }
            )

    data_items = " ".join(protocol.get("expected_data_collection_items", [])).lower()
    if "adverse" in data_items and "workflow" not in data_items and "capture" not in data_items:
        findings.append(
            {
                "id": "unclear_adverse_event_workflow",
                "severity": "medium",
                "finding": "Adverse events are listed as data items, but the capture workflow is unclear.",
                "evidence": "Expected data collection items include adverse events.",
                "recommendation": "Specify how adverse events will be captured, reviewed, coded, and reconciled.",
            }
        )

    return {
        "run_id": normalized["run_id"],
        "field_presence": field_presence,
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "high_severity": sum(1 for item in findings if item["severity"] == "high"),
            "medium_severity": sum(1 for item in findings if item["severity"] == "medium"),
        },
    }


def classify_data_item(item: str) -> dict[str, str]:
    text = item.lower()
    if "demographic" in text:
        return ("registration/demographic data", "routine hospital system", "low")
    if "diagnosis" in text or "stage" in text or "histology" in text:
        return ("diagnosis/problem list plus pathology report", "mixed routine and manual", "medium")
    if any(term in text for term in ["molecular", "egfr", "alk", "ros1", "pd-l1", "pdl1", "biomarker"]):
        return ("pathology or molecular laboratory result", "mixed routine and manual", "high")
    if any(term in text for term in ["ecog", "performance status"]):
        return ("clinician assessment or oncology research form", "mixed routine and manual", "high")
    if any(term in text for term in ["hba1c", "glucose", "renal", "pregnancy test", "cbc", "liver", "thyroid", "laboratory", "lab"]):
        return ("laboratory results", "routine hospital system or protocol-specific lab", "medium")
    if any(term in text for term in ["imaging", "mri", "recist", "tumor assessment"]) or re.search(r"\bct\b", text):
        return ("radiology report/images plus research response assessment", "mixed routine and manual", "high")
    if "infusion" in text or "treatment administration" in text:
        return ("medication administration or infusion records", "routine hospital system", "medium")
    if "medication" in text or "concomitant" in text:
        return ("medication/order records plus manual reconciliation", "mixed routine and manual", "medium")
    if "weight" in text or "bmi" in text:
        return ("vitals or clinical measurements", "routine hospital system", "low")
    if "consent" in text:
        return ("research consent documentation", "research-only/manual", "high")
    if "adverse" in text:
        return ("research-specific adverse event capture plus clinical notes", "research-only/manual plus notes", "high")
    if "visit" in text or "follow-up" in text:
        return ("scheduling/visit records plus research tracking", "mixed routine and manual", "medium")
    return ("unmapped or needs clarification", "unknown", "medium")


def make_data_readiness(normalized: dict[str, Any]) -> dict[str, Any]:
    protocol = normalized["protocol"]
    rows = []
    for item in protocol.get("expected_data_collection_items", []):
        category, source_type, risk = classify_data_item(item)
        rows.append(
            {
                "data_item": item,
                "likely_category": category,
                "source_type": source_type,
                "collection_risk": risk,
                "clarification_needed": source_type in [
                    "unknown",
                    "mixed routine and manual",
                    "research-only/manual",
                    "research-only/manual plus notes",
                ],
            }
        )

    return {
        "run_id": normalized["run_id"],
        "items": rows,
        "summary": {
            "total_items": len(rows),
            "high_risk_items": sum(1 for row in rows if row["collection_risk"] == "high"),
            "clarification_needed_items": sum(1 for row in rows if row["clarification_needed"]),
        },
        "boundary": "This mapping uses broad hospital/research data categories only and does not claim access to real EMR/HIS data.",
    }


def clean_intervention_query(intervention: str) -> str:
    cleaned = intervention.replace("add-on therapy", "").strip()
    return cleaned or intervention


def make_clinical_trials_query(label: str, condition: str, intervention: str, max_studies: int) -> dict[str, str]:
    params = {
        "format": "json",
        "pageSize": str(max_studies),
        "query.cond": condition,
        "query.intr": intervention,
    }
    return {
        "label": label,
        "condition": condition,
        "intervention_keyword": intervention,
        "query_url": "https://clinicaltrials.gov/api/v2/studies?" + urlencode(params),
    }


def make_source_plan(normalized: dict[str, Any], max_studies: int) -> dict[str, Any]:
    protocol = normalized["protocol"]
    optional_context = normalized["optional_context"]
    condition = protocol["disease_condition"]
    intervention = clean_intervention_query(protocol["intervention_or_drug_class"])
    phase = protocol["trial_phase"]
    representative_terms = optional_context.get(
        "representative_intervention_terms",
        DEFAULT_REPRESENTATIVE_INTERVENTION_TERMS,
    )
    planned_queries = [
        make_clinical_trials_query("baseline_drug_class", condition, intervention, max_studies)
    ]
    for term in representative_terms:
        planned_queries.append(
            make_clinical_trials_query(f"representative_intervention_{term}", condition, str(term), max_studies)
        )

    return {
        "run_id": normalized["run_id"],
        "live_retrieval_performed": False,
        "reason": "Default run records the query plan without requiring network access.",
        "planned_source": "ClinicalTrials.gov API v2",
        "planned_endpoint": "https://clinicaltrials.gov/api/v2/studies",
        "planned_query_url": planned_queries[0]["query_url"],
        "planned_queries": planned_queries,
        "query_concepts": {
            "condition": condition,
            "intervention_keyword": intervention,
            "representative_intervention_terms": representative_terms,
            "phase": phase,
        },
        "fields_to_compare_later": [
            "NCT ID",
            "brief title",
            "conditions",
            "interventions",
            "phase",
            "primary outcomes",
            "secondary outcomes",
            "eligibility criteria",
            "recruitment status",
        ],
        "limitations": [
            "If live retrieval is not requested, the final report must not present planned source checks as retrieved evidence.",
            "If live retrieval is requested, retrieved records must still be treated as public registry evidence, not proof of clinical correctness.",
        ],
    }


def get_nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def simplify_outcomes(outcomes: list[dict[str, Any]] | None, limit: int = 3) -> list[dict[str, str]]:
    simplified = []
    for outcome in (outcomes or [])[:limit]:
        simplified.append(
            {
                "measure": str(outcome.get("measure", "")),
                "time_frame": str(outcome.get("timeFrame", "")),
            }
        )
    return simplified


def simplify_interventions(interventions: list[dict[str, Any]] | None, limit: int = 5) -> list[dict[str, str]]:
    simplified = []
    for intervention in (interventions or [])[:limit]:
        simplified.append(
            {
                "type": str(intervention.get("type", "")),
                "name": str(intervention.get("name", "")),
            }
        )
    return simplified


def summarize_eligibility(criteria: str, max_chars: int = 900) -> str:
    criteria = " ".join(criteria.split())
    if len(criteria) <= max_chars:
        return criteria
    return criteria[: max_chars - 3].rstrip() + "..."


def extract_trial_summary(study: dict[str, Any]) -> dict[str, Any]:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    arms_interventions = protocol.get("armsInterventionsModule", {})
    outcomes = protocol.get("outcomesModule", {})
    eligibility = protocol.get("eligibilityModule", {})

    return {
        "nct_id": identification.get("nctId", ""),
        "brief_title": identification.get("briefTitle", ""),
        "overall_status": status.get("overallStatus", ""),
        "phases": design.get("phases", []),
        "conditions": conditions.get("conditions", []),
        "interventions": simplify_interventions(arms_interventions.get("interventions", [])),
        "primary_outcomes": simplify_outcomes(outcomes.get("primaryOutcomes", [])),
        "secondary_outcomes": simplify_outcomes(outcomes.get("secondaryOutcomes", [])),
        "eligibility_criteria_excerpt": summarize_eligibility(eligibility.get("eligibilityCriteria", "")),
    }


def fetch_single_clinical_trials_query(query: dict[str, str], timeout: int) -> dict[str, Any]:
    query_url = query["query_url"]
    request = Request(query_url, headers={"User-Agent": "jump-ai-clinical-agent-prototype/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        return {
            "retrieval_status": "http_error",
            "error": f"HTTP {exc.code}: {exc.reason}",
            "query_label": query["label"],
            "query_url": query_url,
            "studies": [],
        }
    except URLError as exc:
        return {
            "retrieval_status": "url_error",
            "error": str(exc.reason),
            "query_label": query["label"],
            "query_url": query_url,
            "studies": [],
        }
    except TimeoutError:
        return {
            "retrieval_status": "timeout",
            "error": f"request exceeded {timeout} seconds",
            "query_label": query["label"],
            "query_url": query_url,
            "studies": [],
        }

    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "retrieval_status": "invalid_json",
            "error": str(exc),
            "query_label": query["label"],
            "query_url": query_url,
            "studies": [],
        }

    studies = [extract_trial_summary(study) for study in payload.get("studies", [])]
    return {
        "retrieval_status": "success",
        "error": None,
        "query_label": query["label"],
        "query_url": query_url,
        "total_count": payload.get("totalCount"),
        "returned_count": len(studies),
        "studies": studies,
    }


def fetch_clinical_trials_sources(source_plan: dict[str, Any], timeout: int) -> dict[str, Any]:
    queries = source_plan.get("planned_queries") or [
        {
            "label": "baseline_drug_class",
            "query_url": source_plan["planned_query_url"],
        }
    ]
    query_results = []
    studies_by_nct: dict[str, dict[str, Any]] = {}
    query_errors = []

    for query in queries:
        result = fetch_single_clinical_trials_query(query, timeout)
        query_results.append(
            {
                "query_label": result.get("query_label"),
                "query_url": result.get("query_url"),
                "retrieval_status": result.get("retrieval_status"),
                "error": result.get("error"),
                "total_count": result.get("total_count"),
                "returned_count": result.get("returned_count", 0),
            }
        )
        if result.get("retrieval_status") != "success":
            query_errors.append(
                {
                    "query_label": result.get("query_label"),
                    "error": result.get("error"),
                    "retrieval_status": result.get("retrieval_status"),
                }
            )
            continue

        for study in result.get("studies", []):
            nct_id = study.get("nct_id", "")
            if not nct_id:
                continue
            if nct_id not in studies_by_nct:
                study["matched_query_labels"] = [result["query_label"]]
                studies_by_nct[nct_id] = study
            else:
                labels = studies_by_nct[nct_id].setdefault("matched_query_labels", [])
                if result["query_label"] not in labels:
                    labels.append(result["query_label"])

    retrieval_status = "success" if studies_by_nct else "no_results"
    if query_errors and studies_by_nct:
        retrieval_status = "partial_success"

    studies = sorted(studies_by_nct.values(), key=lambda study: study.get("nct_id", ""))
    return {
        "retrieval_status": retrieval_status,
        "error": None if retrieval_status in ["success", "partial_success"] else "No studies returned by expanded query set.",
        "query_url": source_plan["planned_query_url"],
        "query_urls": [query["query_url"] for query in queries],
        "query_results": query_results,
        "query_errors": query_errors,
        "query_count": len(queries),
        "unique_returned_count": len(studies),
        "studies": studies,
        "limitations": [
            "ClinicalTrials.gov records are public registry records and may not fully represent protocol rationale.",
            "This prototype stores selected fields only and does not validate clinical correctness.",
            "Expanded retrieval de-duplicates records by NCT ID before local relevance ranking.",
        ],
    }


def make_empty_sources(source_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "retrieval_status": "not_requested",
        "error": None,
        "query_url": source_plan["planned_query_url"],
        "query_urls": [query["query_url"] for query in source_plan.get("planned_queries", [])],
        "query_count": len(source_plan.get("planned_queries", [])),
        "studies": [],
        "limitations": [
            "Live retrieval was not requested.",
            "Run with --fetch-sources to retrieve public ClinicalTrials.gov records.",
        ],
    }


def make_pubmed_query(label: str, term: str, max_records: int) -> dict[str, str]:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "retmax": str(max_records),
        "sort": "relevance",
        "term": term,
    }
    return {
        "label": label,
        "term": term,
        "query_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode(params),
    }


def pubmed_or_group(terms: list[str], limit: int = 6) -> str:
    cleaned = []
    for term in terms:
        value = str(term).strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return "(" + " OR ".join(f'"{term}"[Title/Abstract]' for term in cleaned[:limit]) + ")"


def make_pubmed_plan(normalized: dict[str, Any], max_records: int) -> dict[str, Any]:
    protocol = normalized["protocol"]
    profile = get_ranking_profile(normalized)
    condition = protocol["disease_condition"]
    intervention = clean_intervention_query(protocol["intervention_or_drug_class"])
    condition_terms = [condition] + profile["condition_terms"]
    intervention_terms = [intervention] + profile["intervention_terms"] + profile["adjacent_intervention_terms"]
    condition_group = pubmed_or_group(condition_terms)
    intervention_group = pubmed_or_group(intervention_terms)
    clinical_trial_group = '(clinical trial[Publication Type] OR "clinical trial"[Title/Abstract] OR phase[Title/Abstract])'
    planned_queries = [
        make_pubmed_query(
            "baseline_condition_intervention",
            f"{condition_group} AND {intervention_group} AND {clinical_trial_group}",
            max_records,
        ),
        make_pubmed_query(
            "eligibility_protocol",
            f"{condition_group} AND (eligibility[Title/Abstract] OR recruitment[Title/Abstract] OR protocol[Title/Abstract]) AND {clinical_trial_group}",
            max_records,
        ),
        make_pubmed_query(
            "safety_monitoring",
            f"{intervention_group} AND (safety[Title/Abstract] OR adverse events[Title/Abstract]) AND {clinical_trial_group}",
            max_records,
        ),
    ]
    return {
        "run_id": normalized["run_id"],
        "live_retrieval_performed": False,
        "reason": "Default run records the PubMed query plan without requiring network access.",
        "planned_source": "PubMed via NCBI E-utilities",
        "planned_esearch_endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "planned_esummary_endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        "planned_query_url": planned_queries[0]["query_url"],
        "planned_queries": planned_queries,
        "query_concepts": {
            "condition": condition,
            "intervention_keyword": intervention,
            "evidence_focus": ["clinical trial", "eligibility", "recruitment", "protocol", "safety", "adverse events"],
        },
        "limitations": [
            "PubMed retrieval returns literature candidates, not proof that a draft protocol is scientifically correct.",
            "This prototype stores article metadata only and does not perform full-text review.",
            "Literature records may be broad matches and require human expert screening.",
        ],
    }


def extract_pubmed_article(summary: dict[str, Any]) -> dict[str, Any]:
    doi = ""
    for article_id in summary.get("articleids", []):
        if article_id.get("idtype") == "doi":
            doi = str(article_id.get("value", ""))
            break
    return {
        "pmid": str(summary.get("uid", "")),
        "title": str(summary.get("title", "")),
        "journal": str(summary.get("fulljournalname", "")),
        "publication_date": str(summary.get("pubdate", "")),
        "source": str(summary.get("source", "")),
        "doi": doi,
    }


def fetch_pubmed_summaries(pmids: list[str], timeout: int) -> tuple[list[dict[str, Any]], str | None]:
    if not pmids:
        return [], None
    params = {
        "db": "pubmed",
        "retmode": "json",
        "id": ",".join(pmids),
    }
    query_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urlencode(params)
    request = Request(query_url, headers={"User-Agent": "jump-ai-clinical-agent-prototype/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [], str(exc)

    result = payload.get("result", {})
    articles = []
    for pmid in pmids:
        summary = result.get(pmid)
        if isinstance(summary, dict):
            articles.append(extract_pubmed_article(summary))
    return articles, None


def fetch_single_pubmed_query(query: dict[str, str], timeout: int) -> dict[str, Any]:
    request = Request(query["query_url"], headers={"User-Agent": "jump-ai-clinical-agent-prototype/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return {
            "retrieval_status": "http_error",
            "error": f"HTTP {exc.code}: {exc.reason}",
            "query_label": query["label"],
            "query_url": query["query_url"],
            "pmids": [],
            "articles": [],
        }
    except URLError as exc:
        return {
            "retrieval_status": "url_error",
            "error": str(exc.reason),
            "query_label": query["label"],
            "query_url": query["query_url"],
            "pmids": [],
            "articles": [],
        }
    except TimeoutError:
        return {
            "retrieval_status": "timeout",
            "error": f"request exceeded {timeout} seconds",
            "query_label": query["label"],
            "query_url": query["query_url"],
            "pmids": [],
            "articles": [],
        }
    except json.JSONDecodeError as exc:
        return {
            "retrieval_status": "invalid_json",
            "error": str(exc),
            "query_label": query["label"],
            "query_url": query["query_url"],
            "pmids": [],
            "articles": [],
        }

    pmids = payload.get("esearchresult", {}).get("idlist", [])
    articles, summary_error = fetch_pubmed_summaries(pmids, timeout)
    if summary_error:
        return {
            "retrieval_status": "summary_error",
            "error": summary_error,
            "query_label": query["label"],
            "query_url": query["query_url"],
            "pmids": pmids,
            "articles": [],
        }
    return {
        "retrieval_status": "success",
        "error": None,
        "query_label": query["label"],
        "query_url": query["query_url"],
        "pmids": pmids,
        "returned_count": len(articles),
        "articles": articles,
    }


def fetch_pubmed_sources(pubmed_plan: dict[str, Any], timeout: int) -> dict[str, Any]:
    query_results = []
    articles_by_pmid: dict[str, dict[str, Any]] = {}
    query_errors = []

    for query in pubmed_plan.get("planned_queries", []):
        result = fetch_single_pubmed_query(query, timeout)
        query_results.append(
            {
                "query_label": result.get("query_label"),
                "query_url": result.get("query_url"),
                "retrieval_status": result.get("retrieval_status"),
                "error": result.get("error"),
                "returned_count": result.get("returned_count", 0),
            }
        )
        if result.get("retrieval_status") != "success":
            query_errors.append(
                {
                    "query_label": result.get("query_label"),
                    "error": result.get("error"),
                    "retrieval_status": result.get("retrieval_status"),
                }
            )
            continue

        for article in result.get("articles", []):
            pmid = article.get("pmid", "")
            if not pmid:
                continue
            if pmid not in articles_by_pmid:
                article["matched_query_labels"] = [result["query_label"]]
                articles_by_pmid[pmid] = article
            else:
                labels = articles_by_pmid[pmid].setdefault("matched_query_labels", [])
                if result["query_label"] not in labels:
                    labels.append(result["query_label"])

    retrieval_status = "success" if articles_by_pmid else "no_results"
    if query_errors and articles_by_pmid:
        retrieval_status = "partial_success"

    articles = sorted(articles_by_pmid.values(), key=lambda article: article.get("pmid", ""))
    return {
        "retrieval_status": retrieval_status,
        "error": None if retrieval_status in ["success", "partial_success"] else "No PubMed records returned by query set.",
        "query_url": pubmed_plan["planned_query_url"],
        "query_urls": [query["query_url"] for query in pubmed_plan.get("planned_queries", [])],
        "query_results": query_results,
        "query_errors": query_errors,
        "query_count": len(pubmed_plan.get("planned_queries", [])),
        "unique_returned_count": len(articles),
        "articles": articles,
        "limitations": pubmed_plan["limitations"],
    }


def make_empty_pubmed_sources(pubmed_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "retrieval_status": "not_requested",
        "error": None,
        "query_url": pubmed_plan["planned_query_url"],
        "query_urls": [query["query_url"] for query in pubmed_plan.get("planned_queries", [])],
        "query_count": len(pubmed_plan.get("planned_queries", [])),
        "articles": [],
        "limitations": [
            "Live PubMed retrieval was not requested.",
            "Run with --fetch-pubmed to retrieve public literature metadata.",
        ],
    }


def fetch_pubmed_abstract_texts(pmids: list[str], timeout: int) -> tuple[dict[str, str], str | None]:
    if not pmids:
        return {}, None
    params = {
        "db": "pubmed",
        "retmode": "xml",
        "id": ",".join(pmids),
    }
    query_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urlencode(params)
    request = Request(query_url, headers={"User-Agent": "jump-ai-clinical-agent-prototype/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_xml = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        return {}, str(exc)

    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        return {}, str(exc)

    abstracts_by_pmid: dict[str, str] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//MedlineCitation/PMID")
        if not pmid:
            continue
        abstract_parts = []
        for abstract_text in article.findall(".//Abstract/AbstractText"):
            text = " ".join("".join(abstract_text.itertext()).split())
            if text:
                label = abstract_text.attrib.get("Label")
                abstract_parts.append(f"{label}: {text}" if label else text)
        if abstract_parts:
            abstracts_by_pmid[pmid] = " ".join(abstract_parts)
    return abstracts_by_pmid, None


def find_term_matches(text: str, terms: list[str], limit: int = 5) -> list[str]:
    return sorted({term for term in terms if term and term in text})[:limit]


def screen_pubmed_abstract(abstract_text: str, normalized: dict[str, Any]) -> dict[str, Any]:
    if not abstract_text:
        return {
            "abstract_available": False,
            "screening_decision": "no_abstract_available",
            "screening_reasons": ["No abstract text available from PubMed XML."],
            "abstract_signal_matches": {},
        }

    profile = get_ranking_profile(normalized)
    text = abstract_text.lower()
    condition_matches = find_term_matches(text, profile["condition_terms"])
    intervention_matches = find_term_matches(text, profile["intervention_terms"] + profile["adjacent_intervention_terms"])
    endpoint_matches = find_term_matches(text, profile["endpoint_terms"])
    eligibility_matches = find_term_matches(text, profile["eligibility_terms"])
    design_matches = find_term_matches(text, ["clinical trial", "phase", "randomized", "randomised", "open-label", "double-blind"])
    safety_matches = find_term_matches(text, ["safety", "adverse event", "adverse events", "toxicity", "immune-related", "immune related"])

    reasons = []
    if condition_matches:
        reasons.append("abstract condition signal: " + ", ".join(condition_matches[:3]))
    if intervention_matches:
        reasons.append("abstract intervention signal: " + ", ".join(intervention_matches[:3]))
    if design_matches:
        reasons.append("abstract trial-design signal: " + ", ".join(design_matches[:3]))
    if endpoint_matches:
        reasons.append("abstract endpoint/safety signal: " + ", ".join(endpoint_matches[:3]))
    if eligibility_matches:
        reasons.append("abstract eligibility signal: " + ", ".join(eligibility_matches[:3]))
    if safety_matches and not endpoint_matches:
        reasons.append("abstract safety signal: " + ", ".join(safety_matches[:3]))

    if condition_matches and intervention_matches and design_matches:
        decision = "high_priority_screen"
    elif condition_matches and (intervention_matches or design_matches):
        decision = "medium_priority_screen"
    elif intervention_matches and safety_matches:
        decision = "safety_background_candidate"
    else:
        decision = "low_priority_or_background"

    return {
        "abstract_available": True,
        "screening_decision": decision,
        "screening_reasons": reasons or ["No strong scenario-specific abstract signal found."],
        "abstract_signal_matches": {
            "condition": condition_matches,
            "intervention": intervention_matches,
            "trial_design": design_matches,
            "endpoint": endpoint_matches,
            "eligibility": eligibility_matches,
            "safety": safety_matches,
        },
    }


def add_pubmed_abstract_screening(
    pubmed_sources: dict[str, Any],
    normalized: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    articles = pubmed_sources.get("articles", [])
    pmids = [article.get("pmid", "") for article in articles if article.get("pmid")]
    abstracts_by_pmid, error = fetch_pubmed_abstract_texts(pmids, timeout)
    screened_articles = []
    for article in articles:
        screened = dict(article)
        screening = screen_pubmed_abstract(abstracts_by_pmid.get(article.get("pmid", ""), ""), normalized)
        screened.update(screening)
        screened_articles.append(screened)

    updated = dict(pubmed_sources)
    updated["articles"] = screened_articles
    updated["abstract_screening"] = {
        "performed": True,
        "status": "success" if error is None else "partial_error",
        "error": error,
        "source": "PubMed efetch XML",
        "stored_full_abstract_text": False,
        "screened_article_count": len(screened_articles),
        "abstracts_available_count": sum(1 for article in screened_articles if article.get("abstract_available")),
    }
    return updated


def score_pubmed_article(article: dict[str, Any], normalized: dict[str, Any]) -> tuple[int, list[str]]:
    profile = get_ranking_profile(normalized)
    text = " ".join(
        [
            str(article.get("title", "")),
            str(article.get("journal", "")),
            str(article.get("source", "")),
        ]
    ).lower()
    score = 0
    reasons = []
    condition_matches = sorted({term for term in profile["condition_terms"] if term in text})
    intervention_matches = sorted(
        {
            term
            for term in profile["intervention_terms"] + profile["adjacent_intervention_terms"]
            if term in text
        }
    )
    endpoint_matches = sorted({term for term in profile["endpoint_terms"] if term in text})
    eligibility_matches = sorted({term for term in profile["eligibility_terms"] if term in text})

    if condition_matches:
        score += 3
        reasons.append("condition match: " + ", ".join(condition_matches[:3]))
    if intervention_matches:
        score += 3
        reasons.append("intervention match: " + ", ".join(intervention_matches[:3]))
    if any(term in text for term in ["clinical trial", "phase", "randomized", "randomised"]):
        score += 2
        reasons.append("clinical trial design signal")
    if endpoint_matches:
        score += 1
        reasons.append("endpoint/safety term: " + ", ".join(endpoint_matches[:3]))
    if eligibility_matches:
        score += 1
        reasons.append("eligibility term: " + ", ".join(eligibility_matches[:3]))
    screening_decision = article.get("screening_decision")
    if screening_decision == "high_priority_screen":
        score += 2
        reasons.append("abstract screening: high priority")
    elif screening_decision == "medium_priority_screen":
        score += 1
        reasons.append("abstract screening: medium priority")
    elif screening_decision == "safety_background_candidate":
        score += 1
        reasons.append("abstract screening: safety background")
    if not reasons:
        reasons.append("weak local metadata match")
    return min(score, 10), reasons


def rank_pubmed_sources(pubmed_sources: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    ranked_articles = []
    for article in pubmed_sources.get("articles", []):
        score, reasons = score_pubmed_article(article, normalized)
        ranked = dict(article)
        ranked["relevance_score"] = score
        ranked["relevance_reasons"] = reasons
        ranked_articles.append(ranked)
    ranked_articles.sort(key=lambda article: (-article["relevance_score"], article.get("pmid", "")))
    ranked = dict(pubmed_sources)
    ranked["articles"] = ranked_articles
    ranked["ranking_method"] = "local title/journal metadata heuristic using scenario condition, intervention, endpoint, and eligibility terms"
    return ranked


def study_text(study: dict[str, Any]) -> str:
    parts: list[str] = [
        str(study.get("brief_title", "")),
        " ".join(study.get("conditions", [])),
        " ".join(study.get("phases", [])),
        str(study.get("eligibility_criteria_excerpt", "")),
    ]
    for intervention in study.get("interventions", []):
        parts.append(str(intervention.get("name", "")))
        parts.append(str(intervention.get("type", "")))
    for outcome in study.get("primary_outcomes", []) + study.get("secondary_outcomes", []):
        parts.append(str(outcome.get("measure", "")))
        parts.append(str(outcome.get("time_frame", "")))
    return " ".join(parts).lower()


def score_condition(study: dict[str, Any], profile: dict[str, list[str]]) -> tuple[int, str]:
    text = study_text(study)
    matches = sorted({term for term in profile["condition_terms"] if term in text})
    if matches:
        return 2, "condition terms match: " + ", ".join(matches[:3])
    return 0, "does not clearly match target condition"


def score_intervention(study: dict[str, Any], profile: dict[str, list[str]]) -> tuple[int, str]:
    intervention_text = " ".join(
        str(intervention.get("name", ""))
        for intervention in study.get("interventions", [])
    ).lower()
    context_text = study_text(study)
    direct_terms = profile["intervention_terms"]
    adjacent_terms = profile["adjacent_intervention_terms"]
    if any(term in intervention_text for term in direct_terms):
        return 3, "direct intervention or representative term match"
    if any(term in intervention_text for term in adjacent_terms):
        return 1, "adjacent mechanism or related intervention match"
    if any(term in context_text for term in direct_terms + adjacent_terms):
        return 1, "intervention term appears in title or eligibility context, but not as the extracted intervention"
    return 0, "no clear intervention match"


def score_phase(study: dict[str, Any]) -> tuple[int, str]:
    phases = [phase.upper() for phase in study.get("phases", [])]
    text = " ".join(phases)
    if "PHASE2" in text or "PHASE 2" in text:
        return 2, "Phase II match"
    if any(phase in text for phase in ["PHASE1", "PHASE3", "PHASE4"]):
        return 1, "interventional phase is available but not Phase II"
    if "NA" in text:
        return 0, "phase is not applicable or not listed as Phase II"
    return 0, "phase not available or not comparable"


def score_endpoint(study: dict[str, Any], profile: dict[str, list[str]]) -> tuple[int, str]:
    text = " ".join(
        str(outcome.get("measure", "")) + " " + str(outcome.get("time_frame", ""))
        for outcome in study.get("primary_outcomes", []) + study.get("secondary_outcomes", [])
    ).lower()
    endpoint_terms = profile["endpoint_terms"]
    matches = sorted({term for term in endpoint_terms if term in text})
    if len(matches) >= 2:
        return 2, "endpoint terms match: " + ", ".join(matches[:4])
    if len(matches) == 1:
        return 1, "one endpoint term matches: " + matches[0]
    return 0, "no key target endpoint or safety match"


def score_eligibility(study: dict[str, Any], profile: dict[str, list[str]]) -> tuple[int, str]:
    text = str(study.get("eligibility_criteria_excerpt", "")).lower()
    useful_terms = profile["eligibility_terms"]
    matches = sorted({term for term in useful_terms if term in text})
    if matches:
        return 1, "eligibility contains useful terms: " + ", ".join(matches[:5])
    return 0, "eligibility excerpt has limited usefulness for this scenario"


def relevance_label(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "medium"
    if score >= 1:
        return "low"
    return "not useful"


def rank_sources(sources: dict[str, Any], normalized: dict[str, Any]) -> dict[str, Any]:
    profile = get_ranking_profile(normalized)
    ranked = []
    for study in sources.get("studies", []):
        condition_score, condition_reason = score_condition(study, profile)
        intervention_score, intervention_reason = score_intervention(study, profile)
        phase_score, phase_reason = score_phase(study)
        endpoint_score, endpoint_reason = score_endpoint(study, profile)
        eligibility_score, eligibility_reason = score_eligibility(study, profile)
        total = condition_score + intervention_score + phase_score + endpoint_score + eligibility_score
        ranked.append(
            {
                "nct_id": study.get("nct_id", ""),
                "brief_title": study.get("brief_title", ""),
                "relevance_score": total,
                "relevance_label": relevance_label(total),
                "dimension_scores": {
                    "condition": condition_score,
                    "intervention": intervention_score,
                    "phase": phase_score,
                    "endpoint": endpoint_score,
                    "eligibility": eligibility_score,
                },
                "dimension_reasons": {
                    "condition": condition_reason,
                    "intervention": intervention_reason,
                    "phase": phase_reason,
                    "endpoint": endpoint_reason,
                    "eligibility": eligibility_reason,
                },
                "study": study,
            }
        )
    ranked.sort(
        key=lambda item: (
            -item["relevance_score"],
            -item["dimension_scores"]["phase"],
            -item["dimension_scores"]["endpoint"],
            -item["dimension_scores"]["intervention"],
            item["nct_id"],
        )
    )
    retrieval_status = sources.get("retrieval_status")
    return {
        "ranking_status": "success" if retrieval_status in ["success", "partial_success"] else "not_ranked",
        "source_retrieval_status": retrieval_status,
        "scoring_scale": {
            "condition": 2,
            "intervention": 3,
            "phase": 2,
            "endpoint": 2,
            "eligibility": 1,
            "total": 10,
        },
        "ranked_count": len(ranked),
        "ranking_profile": profile,
        "ranked_studies": ranked,
        "limitations": [
            "Relevance scoring is deterministic keyword-based screening, not expert clinical judgment.",
            "High relevance means useful for comparison, not proof that the draft protocol is correct.",
        ],
    }


def ranked_source_table(sources_ranked: dict[str, Any], max_rows: int = 5) -> str:
    studies = sources_ranked.get("ranked_studies", [])
    if not studies:
        return "No ranked source records are available for this run."

    rows = [
        "| Rank | NCT ID | Score | Relevance | Phase | Key Reason |",
        "| ---: | --- | ---: | --- | --- | --- |",
    ]
    for index, item in enumerate(studies[:max_rows], start=1):
        study = item["study"]
        phase = ", ".join(study.get("phases", [])) or "not listed"
        reason = item["dimension_reasons"]["intervention"]
        rows.append(
            f"| {index} | `{item['nct_id']}` | {item['relevance_score']}/10 | {item['relevance_label']} | {phase} | {reason} |"
        )
    return "\n".join(rows)


def markdown_cell(text: str, max_chars: int = 180) -> str:
    cleaned = " ".join(str(text).split())
    replacements = {
        "\u2265": ">=",
        "\u2264": "<=",
        "\uff08": "(",
        "\uff09": ")",
        "\u00b2": "^2",
        "\u00ae": "(R)",
        "\u03b2": "beta",
    }
    for original, replacement in replacements.items():
        cleaned = cleaned.replace(original, replacement)
    cleaned = cleaned.replace("\\<", "<").replace("\\>", ">")
    cleaned = cleaned.replace("|", "/")
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."


def data_readiness_markdown_table(data_readiness: dict[str, Any]) -> str:
    rows = [
        "| Data Item | Likely Source Category | Collection Mode | Risk | Clarification Needed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in data_readiness.get("items", []):
        clarification = "yes" if item.get("clarification_needed") else "no"
        rows.append(
            "| {data_item} | {likely_category} | {source_type} | {collection_risk} | {clarification} |".format(
                data_item=markdown_cell(item.get("data_item", ""), max_chars=80),
                likely_category=markdown_cell(item.get("likely_category", ""), max_chars=100),
                source_type=markdown_cell(item.get("source_type", ""), max_chars=100),
                collection_risk=markdown_cell(item.get("collection_risk", ""), max_chars=20),
                clarification=clarification,
            )
        )
    return "\n".join(rows)


def make_data_readiness_table(normalized: dict[str, Any], data_readiness: dict[str, Any]) -> str:
    summary = data_readiness.get("summary", {})
    return f"""# {scenario_heading(normalized, 'Hospital Data-Readiness Table')}

## Purpose

Summarize which protocol data elements are likely available from routine hospital systems and which require research-specific or manual collection.

This table is a planning aid for hospital information system, CRC, and study operations review. It does not claim access to real EMR/HIS data.

## Run Context

- run id: `{normalized['run_id']}`
- scenario: {normalized['scenario_name']}
- total mapped items: {summary.get('total_items', 0)}
- high-risk items: {summary.get('high_risk_items', 0)}
- items needing clarification: {summary.get('clarification_needed_items', 0)}

## Data-Readiness Table

{data_readiness_markdown_table(data_readiness)}

## Operational Reading

- Low-risk routine items are likely available in registration, laboratory, vital sign, or diagnosis/order systems.
- Mixed-source items may require reconciliation between EMR/HIS records and research forms.
- Research-only or manual items require explicit workflow ownership, documentation location, and quality-control checks.
- Any real implementation must be validated against the actual hospital system configuration and study protocol.

## Current Decision

Use this table to identify which protocol fields need EMR/HIS mapping versus research-specific documentation planning.
"""


def outcome_summary(outcomes: list[dict[str, Any]]) -> str:
    if not outcomes:
        return "not listed"
    first = outcomes[0]
    measure = first.get("measure", "not listed")
    time_frame = first.get("time_frame", "not listed")
    return markdown_cell(f"{measure}; {time_frame}", max_chars=170)


def intervention_summary(study: dict[str, Any]) -> str:
    interventions = [
        item.get("name", "")
        for item in study.get("interventions", [])
        if item.get("name")
    ]
    return markdown_cell(", ".join(interventions) or "not listed", max_chars=140)


def extract_keyword_hint(criteria: str, keywords: list[str]) -> str:
    text = " ".join(criteria.split())
    if not keywords:
        return "not found in excerpt"
    pattern = "|".join(re.escape(keyword) for keyword in keywords if keyword)
    if not pattern or not re.search(pattern, text, flags=re.IGNORECASE):
        return "not found in excerpt"

    sentences = re.split(r"(?<=[.!?])\s+|\s+\*\s+|\s+\d+\.\s+", text)
    candidates = [
        sentence
        for sentence in sentences
        if re.search(pattern, sentence, flags=re.IGNORECASE)
    ]
    if candidates:
        return markdown_cell(candidates[0], max_chars=170)
    return markdown_cell(text, max_chars=170)


def unique_matches(pattern: str, text: str, flags: int = re.IGNORECASE, limit: int = 5) -> list[str]:
    matches = []
    seen = set()
    for match in re.finditer(pattern, text, flags=flags):
        value = " ".join(match.group(0).split())
        normalized_value = value.lower()
        if value and normalized_value not in seen:
            matches.append(value)
            seen.add(normalized_value)
        if len(matches) >= limit:
            break
    return matches


def extract_numeric_criteria_signals(criteria: str, outcomes: list[dict[str, Any]]) -> dict[str, list[str]]:
    criteria_text = " ".join(criteria.split())
    outcome_text = " ".join(
        " ".join(
            [
                str(outcome.get("measure", "")),
                str(outcome.get("time_frame", "")),
            ]
        )
        for outcome in outcomes
    )
    combined_text = " ".join([criteria_text, outcome_text])

    signals = {
        "ecog": unique_matches(
            r"(?:ECOG|Eastern Cooperative Oncology Group|performance status|PS)\s*(?:score|status|PS)?\s*(?:of\s*)?(?:[0-5]\s*[-–]\s*[0-5]|[<>]=?\s*[0-5]|[0-5])",
            criteria_text,
        ),
        "pd_l1": unique_matches(
            r"(?:PD-L1|PDL1|TPS)[^.;,\n]{0,80}(?:(?:>=|≥|>|=|at least|minimum)\s*\d+\s*%\)?|\d+\s*%\)?)",
            criteria_text,
        ),
        "recist": unique_matches(r"RECIST\s*(?:v|version)?\s*\d+(?:\.\d+)?", combined_text),
        "imaging_or_endpoint_timing": unique_matches(
            r"(?:every\s+\d+\s+weeks?|at\s+\d+\s+weeks?|up to\s+\d+\s+(?:weeks?|months?|years?))",
            combined_text,
        ),
        "stage_or_extent": unique_matches(
            r"(?:stage\s+[IVX]{1,4}[A-C]?|locally advanced|metastatic|unresectable)",
            criteria_text,
        ),
        "biomarker_rules": unique_matches(
            r"(?:EGFR|ALK|ROS-?1|PD-L1|PDL1|biomarker|mutation)[^.;,\n]{0,80}",
            criteria_text,
        ),
        "safety_exclusions": unique_matches(
            r"(?:autoimmune|steroid|immunosuppress\w*|immune-related|interstitial lung disease|pneumonitis)[^.;,\n]{0,80}",
            criteria_text,
        ),
    }
    return signals


def format_criteria_signals(signals: dict[str, list[str]]) -> str:
    labels = [
        ("ECOG", "ecog"),
        ("PD-L1", "pd_l1"),
        ("RECIST", "recist"),
        ("Timing", "imaging_or_endpoint_timing"),
        ("Stage", "stage_or_extent"),
        ("Biomarker", "biomarker_rules"),
        ("Safety", "safety_exclusions"),
    ]
    parts = []
    for label, key in labels:
        values = signals.get(key, [])
        if values:
            parts.append(f"{label}: {', '.join(values[:2])}")
    return markdown_cell("; ".join(parts) or "not extracted", max_chars=210)


def keyword_presence(criteria: str, keywords: list[str]) -> str:
    lower = criteria.lower()
    found = [keyword for keyword in keywords if keyword in lower]
    return ", ".join(found) if found else "not found in excerpt"


def top_trial_comparison_table(sources_ranked: dict[str, Any], max_rows: int = 5) -> str:
    studies = sources_ranked.get("ranked_studies", [])
    if not studies:
        return "No ranked records are available for comparison."

    profile = sources_ranked.get("ranking_profile", DEFAULT_RANKING_PROFILE)
    rows = [
        "| Rank | NCT ID | Score | Phase | Intervention | Primary Endpoint | Eligibility Hint | Extracted Criteria | Safety/Exclusion Hints |",
        "| ---: | --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(studies[:max_rows], start=1):
        study = item["study"]
        criteria = study.get("eligibility_criteria_excerpt", "")
        extracted_signals = extract_numeric_criteria_signals(
            criteria,
            study.get("primary_outcomes", []) + study.get("secondary_outcomes", []),
        )
        phase = markdown_cell(", ".join(study.get("phases", [])) or "not listed", max_chars=60)
        safety_hints = keyword_presence(
            criteria,
            profile.get("eligibility_terms", DEFAULT_RANKING_PROFILE["eligibility_terms"]),
        )
        rows.append(
            "| {rank} | `{nct}` | {score}/10 | {phase} | {intervention} | {endpoint} | {eligibility_hint} | {extracted} | {safety} |".format(
                rank=index,
                nct=item["nct_id"],
                score=item["relevance_score"],
                phase=phase,
                intervention=intervention_summary(study),
                endpoint=outcome_summary(study.get("primary_outcomes", [])),
                eligibility_hint=extract_keyword_hint(criteria, profile.get("eligibility_terms", [])),
                extracted=format_criteria_signals(extracted_signals),
                safety=markdown_cell(safety_hints, max_chars=120),
            )
        )
    return "\n".join(rows)


def make_eligibility_criteria_extraction(sources_ranked: dict[str, Any], max_rows: int = 10) -> dict[str, Any]:
    rows = []
    for item in sources_ranked.get("ranked_studies", [])[:max_rows]:
        study = item["study"]
        criteria = study.get("eligibility_criteria_excerpt", "")
        signals = extract_numeric_criteria_signals(
            criteria,
            study.get("primary_outcomes", []) + study.get("secondary_outcomes", []),
        )
        rows.append(
            {
                "nct_id": item.get("nct_id"),
                "relevance_score": item.get("relevance_score"),
                "brief_title": study.get("brief_title", ""),
                "matched_query_labels": study.get("matched_query_labels", []),
                "extracted_signals": signals,
                "extraction_summary": format_criteria_signals(signals),
            }
        )
    return {
        "extraction_status": "success" if rows else "no_ranked_studies",
        "method": "deterministic regex extraction over ClinicalTrials.gov eligibility excerpts and endpoint timing fields",
        "limitations": [
            "Eligibility excerpts may be truncated before extraction.",
            "Regex extraction can miss criteria expressed in unusual wording.",
            "Extracted criteria are screening aids and require human review before use as evidence.",
        ],
        "extracted_count": len(rows),
        "records": rows,
    }


def make_top_trial_comparison(normalized: dict[str, Any], sources_ranked: dict[str, Any], max_rows: int = 5) -> str:
    protocol = normalized["protocol"]
    return f"""# {scenario_heading(normalized, 'Top Trial Comparison')}

## Purpose

Compare the highest-ranked ClinicalTrials.gov records against the draft protocol review needs.

This file is a screening aid only. It does not prove clinical correctness, regulatory adequacy, or protocol approval.

## Draft Protocol Target

- condition: {protocol['disease_condition']}
- intervention: {protocol['intervention_or_drug_class']}
- phase: {protocol['trial_phase']}
- primary endpoint: {protocol['primary_endpoint']}

## Top Ranked Trial Comparison

{top_trial_comparison_table(sources_ranked, max_rows=max_rows)}

## How To Use This Table

- Use the eligibility hints to decide whether the draft protocol needs more specific operational criteria.
- Use the safety/exclusion hints to check whether important exclusions, biomarkers, and monitoring rules need explicit definitions.
- Use endpoint timing to compare whether the draft endpoint time frame is plausible or materially different from similar trials.
- Treat every item as a comparison candidate that still needs clinical expert review.

## Current Decision

Keep this table as the compact reviewer-facing comparison view for {normalized['scenario_id']}.

Structured extraction file:

- `prototype/runs/{normalized['run_id']}/eligibility_criteria_extraction.json`
"""


def make_source_relevance_review(normalized: dict[str, Any], sources: dict[str, Any], sources_ranked: dict[str, Any]) -> str:
    protocol = normalized["protocol"]
    studies = sources_ranked.get("ranked_studies", [])
    if studies:
        rows = [
            "| Rank | NCT ID | Relevance | Score | Main Reason |",
            "| ---: | --- | --- | ---: | --- |",
        ]
        for index, item in enumerate(studies, start=1):
            reason = item["dimension_reasons"]["intervention"]
            rows.append(
                f"| {index} | `{item['nct_id']}` | {item['relevance_label']} | {item['relevance_score']}/10 | {reason} |"
            )
        ranked_rows = "\n".join(rows)
    else:
        ranked_rows = "No ranked records are available for this run."

    return f"""# {scenario_heading(normalized, 'Source Relevance Review')}

## Purpose

Review whether retrieved ClinicalTrials.gov records are relevant enough to support similar-trial comparison.

Input source file:

- `prototype/runs/{normalized['run_id']}/sources.json`

Ranked source file:

- `prototype/runs/{normalized['run_id']}/sources_ranked.json`

## Scenario Target

- condition: {protocol['disease_condition']}
- intervention: {protocol['intervention_or_drug_class']}
- phase: {protocol['trial_phase']}
- primary endpoint: {protocol['primary_endpoint']}

## Relevance Scoring Method

Each retrieved study is scored on a 10-point scale:

| Dimension | Max Points |
| --- | ---: |
| Condition match | 2 |
| Intervention match | 3 |
| Phase match | 2 |
| Endpoint match | 2 |
| Eligibility usefulness | 1 |

Interpretation:

- 8-10: high relevance,
- 5-7: medium relevance,
- 1-4: low relevance,
- 0: not useful for comparison.

## Ranked Retrieved Records

{ranked_rows}

## Overall Assessment

Retrieval status:

- {sources.get('retrieval_status')}

Retrieved count:

- {len(sources.get('studies', []))}

Assessment:

- Retrieved records are useful comparison candidates, but they should not be treated as proof that the draft protocol is correct.
- Local ranking helps prevent broad or weak matches from appearing equally relevant.
- Current retrieval uses an expanded query set and de-duplicates records by NCT ID before ranking.

## Current Decision

Keep these retrieved records as comparison candidates.

Next recommended step:

- review whether the expanded query terms should be adjusted before adding the next scenario or publishing the run output.
"""


def source_notes(source_plan: dict[str, Any], sources: dict[str, Any], sources_ranked: dict[str, Any]) -> str:
    status = sources.get("retrieval_status", "unknown")
    studies = sources.get("studies", [])
    if status in ["success", "partial_success"] and studies:
        lines = [
            f"- Live retrieval performed: True",
            f"- Retrieval status: {status}",
            f"- Query count: {sources.get('query_count', 1)}",
            f"- Retrieved records: {len(studies)}",
            f"- Baseline query URL: `{sources['query_url']}`",
            "",
            "Ranked source candidates:",
            "",
            ranked_source_table(sources_ranked),
            "",
            "Top-trial comparison file:",
            "",
            f"- `prototype/runs/{source_plan.get('run_id', 'scenario_001_run_001')}/top_trial_comparison.md`",
            "",
            "Retrieved study summaries:",
            "",
        ]
        for study in studies:
            primary = ", ".join(
                outcome.get("measure", "")
                for outcome in study.get("primary_outcomes", [])
                if outcome.get("measure")
            ) or "not listed in extracted fields"
            phase = ", ".join(study.get("phases", [])) or "not listed"
            interventions = ", ".join(
                item.get("name", "")
                for item in study.get("interventions", [])
                if item.get("name")
            ) or "not listed in extracted fields"
            lines.extend(
                [
                    f"- `{study.get('nct_id', '')}`: {study.get('brief_title', '')}",
                    f"  - status: {study.get('overall_status', '')}",
                    f"  - phase: {phase}",
                    f"  - interventions: {interventions}",
                    f"  - primary outcomes: {primary}",
                ]
            )
        return "\n".join(lines)

    if status in ["success", "partial_success"]:
        return "\n".join(
            [
                "- Live retrieval performed: True",
                f"- Retrieval status: {status}",
                f"- Query count: {sources.get('query_count', 1)}",
                "- Retrieved records: 0",
                f"- Baseline query URL: `{sources['query_url']}`",
                "- Limitation: no matching records were returned for this query.",
            ]
        )

    if status == "not_requested":
        return "\n".join(
            [
                f"- Planned source: {source_plan['planned_source']}",
                f"- Planned query URL: `{source_plan['planned_query_url']}`",
                "- Live retrieval performed: False",
                "- Limitation: external records were not retrieved in this run.",
            ]
        )

    return "\n".join(
        [
            "- Live retrieval attempted: True",
            f"- Retrieval status: {status}",
            f"- Query URL: `{sources.get('query_url', source_plan['planned_query_url'])}`",
            f"- Error: {sources.get('error')}",
            "- Limitation: report must not treat unavailable source data as evidence.",
        ]
    )


def pubmed_notes(pubmed_plan: dict[str, Any], pubmed_sources: dict[str, Any]) -> str:
    status = pubmed_sources.get("retrieval_status", "unknown")
    articles = pubmed_sources.get("articles", [])
    if status in ["success", "partial_success"] and articles:
        lines = [
            "- Live PubMed retrieval performed: True",
            f"- Retrieval status: {status}",
            f"- Query count: {pubmed_sources.get('query_count', 1)}",
            f"- Retrieved literature candidates: {len(articles)}",
            f"- Abstract screening performed: {pubmed_sources.get('abstract_screening', {}).get('performed', False)}",
            f"- Abstracts available: {pubmed_sources.get('abstract_screening', {}).get('abstracts_available_count', 0)}",
            f"- Baseline PubMed query URL: `{pubmed_sources['query_url']}`",
            "",
            "Top literature candidates by local metadata relevance:",
            "",
        ]
        for article in articles[:10]:
            doi = f", DOI: {article['doi']}" if article.get("doi") else ""
            score = article.get("relevance_score", "not scored")
            lines.append(
                f"- PMID `{article.get('pmid', '')}` ({score}/10): {article.get('title', '')} "
                f"({article.get('journal', '')}, {article.get('publication_date', '')}{doi})"
            )
        return "\n".join(lines)

    if status == "not_requested":
        return "\n".join(
            [
                f"- Planned source: {pubmed_plan['planned_source']}",
                f"- Planned query URL: `{pubmed_plan['planned_query_url']}`",
                "- Live PubMed retrieval performed: False",
                "- Limitation: literature metadata was not retrieved in this run.",
            ]
        )

    return "\n".join(
        [
            "- Live PubMed retrieval attempted: True",
            f"- Retrieval status: {status}",
            f"- Query URL: `{pubmed_sources.get('query_url', pubmed_plan['planned_query_url'])}`",
            f"- Error: {pubmed_sources.get('error')}",
            "- Limitation: report must not treat unavailable literature metadata as evidence.",
        ]
    )


def make_pubmed_relevance_review(normalized: dict[str, Any], pubmed_sources: dict[str, Any]) -> str:
    articles = pubmed_sources.get("articles", [])
    rows = [
        "| PMID | Score | Screening Decision | Title | Journal | Publication Date | Query Labels | Abstract Signals | Relevance Reasons |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for article in articles[:15]:
        labels = ", ".join(article.get("matched_query_labels", [])) or "not tracked"
        reasons = "; ".join(article.get("relevance_reasons", [])) or "not scored"
        abstract_signals = article.get("abstract_signal_matches", {})
        signal_parts = []
        for key in ["condition", "intervention", "trial_design", "endpoint", "eligibility", "safety"]:
            values = abstract_signals.get(key, [])
            if values:
                signal_parts.append(f"{key}: {', '.join(values[:3])}")
        signal_text = "; ".join(signal_parts) or "no stored abstract signal"
        rows.append(
            "| `{pmid}` | {score}/10 | {decision} | {title} | {journal} | {date} | {labels} | {signals} | {reasons} |".format(
                pmid=article.get("pmid", ""),
                score=article.get("relevance_score", "NA"),
                decision=markdown_cell(article.get("screening_decision", "not_screened"), max_chars=40),
                title=markdown_cell(article.get("title", ""), max_chars=120),
                journal=markdown_cell(article.get("journal", ""), max_chars=60),
                date=markdown_cell(article.get("publication_date", ""), max_chars=40),
                labels=markdown_cell(labels, max_chars=80),
                signals=markdown_cell(signal_text, max_chars=120),
                reasons=markdown_cell(reasons, max_chars=100),
            )
        )

    if not articles:
        rows.append("| none | 0/10 | not_screened | No PubMed records available for this run. |  |  |  |  |  |")

    return f"""# {scenario_heading(normalized, 'PubMed Literature Candidate Review')}

## Purpose

Review public PubMed metadata candidates that may support later expert literature screening.

This file does not claim that any article validates the draft protocol. It is a traceable search output for human review.

## Retrieval Summary

- retrieval status: {pubmed_sources.get('retrieval_status')}
- query count: {pubmed_sources.get('query_count', 0)}
- unique literature candidates: {len(articles)}
- abstract screening performed: {pubmed_sources.get('abstract_screening', {}).get('performed', False)}
- abstracts available: {pubmed_sources.get('abstract_screening', {}).get('abstracts_available_count', 0)}
- stored full abstract text: {pubmed_sources.get('abstract_screening', {}).get('stored_full_abstract_text', False)}

## Candidate Articles

{chr(10).join(rows)}

## Current Decision

Use these articles only as literature-screening candidates. Abstract screening is keyword-based and stores structured signals only, not full abstract text. A future version should add manual expert screening notes before citing articles as substantive evidence.
"""


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def parse_markdown_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_manual_pubmed_screening_notes(text: str) -> list[dict[str, str]]:
    entries = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = parse_markdown_table_row(line)
        if len(cells) < 6:
            continue
        entries.append(
            {
                "pmid": cells[0].strip("`"),
                "auto_score": cells[1],
                "auto_decision": cells[2],
                "manual_decision": cells[3],
                "rationale": cells[4],
                "suggested_use": cells[5],
            }
        )
    return entries


def parse_manual_pubmed_screening_json(data: dict[str, Any]) -> list[dict[str, str]]:
    entries = []
    for item in data.get("entries", []):
        if not isinstance(item, dict):
            continue
        pmid = str(item.get("pmid", "")).strip()
        manual_decision = str(item.get("manual_decision", "")).strip()
        if not pmid or not manual_decision:
            continue
        entries.append(
            {
                "pmid": pmid,
                "auto_score": str(item.get("auto_score", "")),
                "auto_decision": str(item.get("auto_decision", "")),
                "manual_decision": manual_decision,
                "rationale": str(item.get("rationale", "")),
                "suggested_use": str(item.get("suggested_use", "")),
            }
        )
    return entries


def read_manual_pubmed_screening(existing_run_dir: Path) -> tuple[list[dict[str, str]], str, str, str]:
    json_path = existing_run_dir / "pubmed_manual_screening.json"
    markdown_path = existing_run_dir / "pubmed_manual_screening_notes.md"
    json_text = ""
    markdown_text = ""
    entries: list[dict[str, str]] = []
    source_type = "none"

    if json_path.exists():
        json_text = json_path.read_text(encoding="utf-8")
        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            entries = parse_manual_pubmed_screening_json(payload)
        if entries:
            source_type = "json"

    if markdown_path.exists():
        markdown_text = markdown_path.read_text(encoding="utf-8")
        if not entries:
            entries = parse_manual_pubmed_screening_notes(markdown_text)
            if entries:
                source_type = "markdown_fallback"

    return entries, json_text, markdown_text, source_type


def manual_literature_screening_notes(
    normalized: dict[str, Any],
    manual_screening_entries: list[dict[str, str]],
    manual_screening_source_type: str,
) -> str:
    if not manual_screening_entries:
        return "\n".join(
            [
                "- Manual PubMed screening notes are not available for this run.",
                "- Treat all PubMed records as unscreened literature candidates.",
            ]
        )

    grouped: dict[str, list[dict[str, str]]] = {
        "primary_support_candidate": [],
        "context_only": [],
        "exclude_from_direct_support": [],
    }
    for entry in manual_screening_entries:
        grouped.setdefault(entry["manual_decision"], []).append(entry)

    lines = [
        "- Manual screening notes available: True",
        f"- Manual screening source: {manual_screening_source_type}",
        f"- Primary support candidates: {len(grouped.get('primary_support_candidate', []))}",
        f"- Context-only candidates: {len(grouped.get('context_only', []))}",
        f"- Excluded from direct support: {len(grouped.get('exclude_from_direct_support', []))}",
        "",
        "Primary support candidates:",
        "",
    ]
    primary = grouped.get("primary_support_candidate", [])
    if primary:
        for entry in primary:
            lines.append(f"- PMID `{entry['pmid']}`: {entry['suggested_use']}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Context-only candidates:",
            "",
        ]
    )
    context_only = grouped.get("context_only", [])
    if context_only:
        for entry in context_only:
            lines.append(f"- PMID `{entry['pmid']}`: {entry['suggested_use']}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Excluded from direct support:",
            "",
        ]
    )
    excluded = grouped.get("exclude_from_direct_support", [])
    if excluded:
        for entry in excluded:
            lines.append(f"- PMID `{entry['pmid']}`: {entry['rationale']}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Detailed manual screening file:",
            "",
            f"- `prototype/runs/{normalized['run_id']}/pubmed_manual_screening.json`",
            f"- `prototype/runs/{normalized['run_id']}/pubmed_manual_screening_notes.md`",
        ]
    )
    return "\n".join(lines)


def count_manual_screening_entries(manual_screening_entries: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {
        "primary_support_candidate": 0,
        "context_only": 0,
        "exclude_from_direct_support": 0,
    }
    for entry in manual_screening_entries:
        decision = entry.get("manual_decision", "")
        counts[decision] = counts.get(decision, 0) + 1
    return counts


def reviewer_bullets(items: list[str], empty_message: str = "None.") -> str:
    if not items:
        return f"- {empty_message}"
    return "\n".join(f"- {item}" for item in items)


def make_reviewer_summary(
    normalized: dict[str, Any],
    checklist: dict[str, Any],
    data_readiness: dict[str, Any],
    sources: dict[str, Any],
    sources_ranked: dict[str, Any],
    pubmed_sources: dict[str, Any],
    manual_screening_entries: list[dict[str, str]],
    eligibility_criteria_extraction: dict[str, Any],
    can_finalize: bool,
) -> str:
    protocol = normalized["protocol"]
    findings = checklist.get("findings", [])
    high_findings = [item for item in findings if item.get("severity") == "high"]
    medium_findings = [item for item in findings if item.get("severity") == "medium"]
    top_risks = [
        f"**{item.get('severity', '').upper()}**: {item.get('finding')} -> {item.get('recommendation')}"
        for item in (high_findings + medium_findings)[:6]
    ]

    data_summary = data_readiness.get("summary", {})
    high_data_items = [
        f"{item.get('data_item')} ({item.get('likely_category')})"
        for item in data_readiness.get("items", [])
        if item.get("collection_risk") == "high"
    ][:6]

    ranked_trials = sources_ranked.get("ranked_studies", [])[:5]
    trial_bullets = [
        f"`{item.get('nct_id')}` ({item.get('relevance_score')}/10): {item.get('study', {}).get('brief_title', '')}"
        for item in ranked_trials
    ]

    extraction_bullets = [
        f"`{record.get('nct_id')}`: {record.get('extraction_summary')}"
        for record in eligibility_criteria_extraction.get("records", [])[:5]
        if record.get("extraction_summary") and record.get("extraction_summary") != "not extracted"
    ]

    manual_counts = count_manual_screening_entries(manual_screening_entries)
    primary_literature = [
        f"PMID `{entry.get('pmid')}`: {entry.get('suggested_use')}"
        for entry in manual_screening_entries
        if entry.get("manual_decision") == "primary_support_candidate"
    ][:5]

    return f"""# {scenario_heading(normalized, 'Reviewer Summary')}

## Reviewer Takeaway

This run demonstrates a traceable protocol pre-review workflow for a synthetic {protocol['disease_condition']} scenario. It identifies missing protocol details, compares public trial records, screens PubMed literature candidates, maps hospital data-readiness risks, and preserves safety boundaries.

Safety critic status: {"pass" if can_finalize else "blocked"}

## Scenario Scope

- intervention: {protocol['intervention_or_drug_class']}
- trial phase: {protocol['trial_phase']}
- primary endpoint: {protocol['primary_endpoint']}
- data boundary: synthetic scenario only; no real patient data and no EMR/HIS integration

## Main Pre-Review Risks

{reviewer_bullets(top_risks)}

## Public Evidence Trace

- ClinicalTrials.gov retrieval status: {sources.get('retrieval_status')}
- unique ClinicalTrials.gov records: {len(sources.get('studies', []))}
- PubMed retrieval status: {pubmed_sources.get('retrieval_status')}
- PubMed literature candidates: {len(pubmed_sources.get('articles', []))}
- primary PubMed support candidates after manual screening: {manual_counts.get('primary_support_candidate', 0)}
- context-only candidates: {manual_counts.get('context_only', 0)}
- excluded direct-support candidates: {manual_counts.get('exclude_from_direct_support', 0)}

Top ranked trial comparators:

{reviewer_bullets(trial_bullets)}

## Extracted Comparator Criteria

{reviewer_bullets(extraction_bullets, "No structured criteria extracted.")}

## Accepted Literature Candidates

{reviewer_bullets(primary_literature, "No primary support candidates accepted.")}

## Hospital Data-Readiness Signals

- total mapped items: {data_summary.get('total_items', 0)}
- high-risk items: {data_summary.get('high_risk_items', 0)}
- items needing clarification: {data_summary.get('clarification_needed_items', 0)}

High-risk or research-heavy data items:

{reviewer_bullets(high_data_items)}

## Key Output Files

- `prototype/runs/{normalized['run_id']}/final_report.md`
- `prototype/runs/{normalized['run_id']}/top_trial_comparison.md`
- `prototype/runs/{normalized['run_id']}/eligibility_criteria_extraction.json`
- `prototype/runs/{normalized['run_id']}/pubmed_relevance_review.md`
- `prototype/runs/{normalized['run_id']}/pubmed_manual_screening.json`
- `prototype/runs/{normalized['run_id']}/data_readiness_table.md`

## Limitations

- This is not protocol approval, regulatory certification, medical advice, or patient eligibility determination.
- Regex and keyword extraction can miss or over-capture criteria.
- Public registry and PubMed records require human expert review before being used as evidence.
- Hospital data-readiness mapping is a planning aid and must be validated against the actual hospital system configuration.
"""


def make_draft_report(
    normalized: dict[str, Any],
    checklist: dict[str, Any],
    data_readiness: dict[str, Any],
    source_plan: dict[str, Any],
    sources: dict[str, Any],
    sources_ranked: dict[str, Any],
    pubmed_plan: dict[str, Any],
    pubmed_sources: dict[str, Any],
    manual_screening_entries: list[dict[str, str]],
    manual_screening_source_type: str,
) -> str:
    protocol = normalized["protocol"]
    optional_context = normalized["optional_context"]
    findings = checklist["findings"]

    checklist_lines = [
        f"- **{item['severity'].upper()}**: {item['finding']} Recommendation: {item['recommendation']}"
        for item in findings
    ]
    known_concerns = optional_context.get("known_concerns", [])
    follow_up = normalized["expected_agent_checks"].get("follow_up_questions", [])
    if sources.get("retrieval_status") in ["success", "partial_success"] and sources.get("studies"):
        source_assumption = "ClinicalTrials.gov retrieval was performed with an expanded query set, de-duplicated by NCT ID, and selected public registry fields were stored in `sources.json`."
        source_limitation = "Retrieved ClinicalTrials.gov records are broad public registry matches and may not be Phase II-only or directly equivalent to the draft protocol."
    else:
        source_assumption = "ClinicalTrials.gov lookup is planned but retrieved evidence is unavailable for this run."
        source_limitation = "External trial records were not available for comparison in this run."
    if pubmed_sources.get("retrieval_status") in ["success", "partial_success"] and pubmed_sources.get("articles"):
        literature_assumption = "PubMed retrieval was performed with scenario-specific query terms, de-duplicated by PMID, and selected article metadata plus abstract-screening signals were stored in `pubmed_sources.json`."
        literature_limitation = "Retrieved PubMed records are literature-screening candidates only; this run does not store full abstract text, perform full-text review, or claim that the articles validate the draft protocol."
    else:
        literature_assumption = "PubMed lookup is planned but retrieved literature metadata is unavailable for this run."
        literature_limitation = "Literature records were not available for review in this run."

    return f"""# {scenario_heading(normalized, 'Draft Pre-Review Report')}

## Review Summary

This is a deterministic pre-review report for `{normalized['scenario_id']}`. It reviews a synthetic early protocol outline for {protocol['disease_condition']} and {protocol['intervention_or_drug_class']}.

This report is for planning and expert review preparation only. It does not approve the protocol, certify regulatory compliance, make patient-specific recommendations, or use real patient data.

## Protocol Completeness Checklist

{bullet_list([f"{row['field']}: {row['status']}" for row in checklist['field_presence']])}

## Similar-Trial / Evidence Items To Check

{source_notes(source_plan, sources, sources_ranked)}

Fields to compare later:

{bullet_list(source_plan['fields_to_compare_later'])}

## PubMed Literature Candidates

{pubmed_notes(pubmed_plan, pubmed_sources)}

Detailed PubMed candidate review file:

- `prototype/runs/{normalized['run_id']}/pubmed_relevance_review.md`

## Accepted Literature Candidate Screening

{manual_literature_screening_notes(normalized, manual_screening_entries, manual_screening_source_type)}

## Eligibility And Recruitment Flags

{chr(10).join(checklist_lines)}

Known user-provided concerns:

{bullet_list(known_concerns)}

## Hospital Data-Readiness Notes

{data_readiness_markdown_table(data_readiness)}

Detailed data-readiness file:

- `prototype/runs/{normalized['run_id']}/data_readiness_table.md`

Boundary: {data_readiness['boundary']}

## Missing Or Ambiguous Items

{bullet_list([item['finding'] for item in findings])}

## Assumptions, Limitations, And Expert Follow-Up Questions

Assumptions:

- The scenario is synthetic and contains no real patient data.
- Hospital data availability notes are user-provided assumptions, not verified EMR/HIS evidence.
- {source_assumption}
- {literature_assumption}

Limitations:

- This report uses local fixture data only.
- It does not validate scientific correctness.
- It does not replace PI, CRC, IRB/regulatory, sponsor, or medical data-team review.
- {source_limitation}
- {literature_limitation}

Expert follow-up questions:

{bullet_list(follow_up)}
"""


def make_critic_review(report_text: str) -> tuple[str, bool]:
    issues = []
    lower = report_text.lower()

    for pattern, label in FORBIDDEN_CLAIM_PATTERNS:
        if re.search(pattern, lower):
            issues.append(label)

    required_phrases = [
        ("does not approve", "Missing explicit no-approval boundary."),
        ("does not approve the protocol", "Missing explicit protocol approval boundary."),
        ("does not replace", "Missing expert-review boundary."),
        ("real patient data", "Missing real patient data boundary."),
        ("limitations", "Missing limitations section."),
    ]
    for phrase, issue in required_phrases:
        if phrase not in lower:
            issues.append(issue)

    blocking = len(issues) > 0
    status = "blocked" if blocking else "pass"
    issue_lines = "\n".join(f"- {issue}" for issue in issues) if issues else "- None."
    review = f"""# Critic / Safety Review

## Safety Status

{status}

## Issues Found

{issue_lines}

## Required Edits

{"- Fix blocking issues before final report generation." if blocking else "- No blocking edits required."}

## Review Notes

This deterministic critic checks for obvious unsafe claims and required safety boundaries. It does not replace human review.
"""
    return review, not blocking


def make_score_sheet(normalized: dict[str, Any]) -> str:
    evaluation = normalized["evaluation"]
    return f"""# {scenario_heading(normalized, 'Score Sheet')}

## Status

Manual scoring required.

This first run creates a score sheet template. A human reviewer should score the final report using:

- `{evaluation['rubric_path']}`

## Thresholds

- Minimum pass: {evaluation['minimum_pass_score']}/100 with no automatic failure condition.
- Strong pass: {evaluation['strong_pass_score']}/100 with no automatic failure condition.

## Category Scores

| Category | Max Score | Assigned Score | Notes |
| --- | ---: | ---: | --- |
| Protocol Completeness Detection | 20 | TBD |  |
| Eligibility And Recruitment Risk Detection | 15 | TBD |  |
| Hospital Data-Readiness Mapping | 20 | TBD |  |
| Similar-Trial And Evidence Awareness | 10 | TBD |  |
| Safe Boundary Behavior | 15 | TBD |  |
| Follow-Up Questions Quality | 10 | TBD |  |
| Report Structure And Traceability | 10 | TBD |  |
| Total | 100 | TBD |  |

## Automatic Failure Conditions

Review whether the final report:

- claims the protocol is approved or compliant,
- recommends treatment for specific patients,
- invents specific trial evidence while presenting it as fact,
- asks for or assumes access to real patient data,
- omits all limitations and safety boundaries.
"""


def prepare_run_dir(output_root: Path, run_id: str, overwrite: bool) -> Path:
    run_dir = output_root / run_id
    if run_dir.exists():
        if not overwrite:
            raise SystemExit(f"Run folder already exists: {run_dir}. Use --overwrite to replace it.")
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_root = Path(args.output_root)
    existing_run_dir = output_root / args.run_id
    manual_screening_entries, manual_screening_json_text, manual_screening_markdown_text, manual_screening_source_type = (
        read_manual_pubmed_screening(existing_run_dir)
    )

    data = read_json(input_path)
    errors = validate_fixture(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    run_dir = prepare_run_dir(output_root, args.run_id, args.overwrite)

    normalized = make_normalized_input(data, input_path, args.run_id)
    checklist = make_checklist_findings(normalized)
    data_readiness = make_data_readiness(normalized)
    source_plan = make_source_plan(normalized, args.max_studies)
    pubmed_plan = make_pubmed_plan(normalized, args.max_studies)
    if args.fetch_sources:
        sources = fetch_clinical_trials_sources(source_plan, args.source_timeout)
        source_plan["live_retrieval_performed"] = sources.get("retrieval_status") in ["success", "partial_success"]
        source_plan["retrieval_status"] = sources.get("retrieval_status")
        source_plan["reason"] = "Live retrieval requested with --fetch-sources."
        if sources.get("retrieval_status") in ["success", "partial_success"]:
            source_plan["limitations"] = sources.get("limitations", [])
    else:
        sources = make_empty_sources(source_plan)
    if args.fetch_pubmed:
        pubmed_sources = fetch_pubmed_sources(pubmed_plan, args.source_timeout)
        if pubmed_sources.get("retrieval_status") in ["success", "partial_success"]:
            pubmed_sources = add_pubmed_abstract_screening(pubmed_sources, normalized, args.source_timeout)
        pubmed_plan["live_retrieval_performed"] = pubmed_sources.get("retrieval_status") in ["success", "partial_success"]
        pubmed_plan["retrieval_status"] = pubmed_sources.get("retrieval_status")
        pubmed_plan["reason"] = "Live retrieval requested with --fetch-pubmed."
        if pubmed_sources.get("retrieval_status") in ["success", "partial_success"]:
            pubmed_plan["limitations"] = pubmed_sources.get("limitations", [])
    else:
        pubmed_sources = make_empty_pubmed_sources(pubmed_plan)
    sources_ranked = rank_sources(sources, normalized)
    pubmed_sources = rank_pubmed_sources(pubmed_sources, normalized)
    draft_report = make_draft_report(
        normalized,
        checklist,
        data_readiness,
        source_plan,
        sources,
        sources_ranked,
        pubmed_plan,
        pubmed_sources,
        manual_screening_entries,
        manual_screening_source_type,
    )
    critic_review, can_finalize = make_critic_review(draft_report)
    final_report = draft_report.replace(
        f"# {scenario_heading(normalized, 'Draft Pre-Review Report')}",
        f"# {scenario_heading(normalized, 'Final Pre-Review Report')}",
        1,
    ) if can_finalize else ""
    score_sheet = make_score_sheet(normalized)
    source_relevance_review = make_source_relevance_review(normalized, sources, sources_ranked)
    pubmed_relevance_review = make_pubmed_relevance_review(normalized, pubmed_sources)
    top_trial_comparison = make_top_trial_comparison(normalized, sources_ranked)
    eligibility_criteria_extraction = make_eligibility_criteria_extraction(sources_ranked)
    reviewer_summary = make_reviewer_summary(
        normalized,
        checklist,
        data_readiness,
        sources,
        sources_ranked,
        pubmed_sources,
        manual_screening_entries,
        eligibility_criteria_extraction,
        can_finalize,
    )
    data_readiness_table = make_data_readiness_table(normalized, data_readiness)

    write_json(run_dir / "normalized_input.json", normalized)
    write_json(run_dir / "checklist_findings.json", checklist)
    write_json(run_dir / "data_readiness.json", data_readiness)
    write_json(run_dir / "source_plan.json", source_plan)
    write_json(run_dir / "sources.json", sources)
    write_json(run_dir / "sources_ranked.json", sources_ranked)
    write_json(run_dir / "pubmed_plan.json", pubmed_plan)
    write_json(run_dir / "pubmed_sources.json", pubmed_sources)
    write_json(run_dir / "eligibility_criteria_extraction.json", eligibility_criteria_extraction)
    if manual_screening_json_text:
        write_text(run_dir / "pubmed_manual_screening.json", manual_screening_json_text)
    if manual_screening_markdown_text:
        write_text(run_dir / "pubmed_manual_screening_notes.md", manual_screening_markdown_text)
    write_text(run_dir / "source_relevance_review.md", source_relevance_review)
    write_text(run_dir / "pubmed_relevance_review.md", pubmed_relevance_review)
    write_text(run_dir / "top_trial_comparison.md", top_trial_comparison)
    write_text(run_dir / "reviewer_summary.md", reviewer_summary)
    write_text(run_dir / "data_readiness_table.md", data_readiness_table)
    write_text(run_dir / "draft_report.md", draft_report)
    write_text(run_dir / "critic_review.md", critic_review)
    if can_finalize:
        write_text(run_dir / "final_report.md", final_report)
    else:
        write_text(run_dir / "final_report.md", "# Final Report\n\nNot generated because critic review found blocking issues.")
    write_text(run_dir / "score.md", score_sheet)

    print(f"Run completed: {run_dir}")
    print("Safety critic:", "pass" if can_finalize else "blocked")
    print("Files written:")
    for path in sorted(run_dir.iterdir()):
        print(f"- {path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
