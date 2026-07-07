"""Run a local deterministic prototype workflow for a protocol scenario.

This script intentionally avoids external APIs, LLM calls, and third-party
dependencies. It creates traceable files that can be reviewed in GitHub before
the project grows into a larger agent system.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
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

REPRESENTATIVE_GLP1_TERMS = [
    "semaglutide",
    "liraglutide",
    "dulaglutide",
    "exenatide",
]


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
        "--max-studies",
        type=int,
        default=5,
        help="Maximum number of ClinicalTrials.gov studies to request per query. Defaults to 5.",
    )
    parser.add_argument(
        "--source-timeout",
        type=int,
        default=20,
        help="ClinicalTrials.gov request timeout in seconds. Defaults to 20.",
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

    if "glp-1" not in all_criteria_text and "glp" not in all_criteria_text:
        findings.append(
            {
                "id": "unclear_prior_glp1_exposure",
                "severity": "medium",
                "finding": "Prior GLP-1 receptor agonist exposure is not addressed in eligibility criteria.",
                "evidence": "No inclusion or exclusion criterion refers to prior GLP-1 receptor agonist exposure.",
                "recommendation": "Clarify whether prior or recent GLP-1 receptor agonist use is allowed, excluded, or stratified.",
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
    if "diagnosis" in text:
        return ("diagnosis/problem list", "routine hospital system", "medium")
    if "medication" in text or "concomitant" in text:
        return ("medication/order records plus manual reconciliation", "mixed routine and manual", "medium")
    if any(term in text for term in ["hba1c", "glucose", "renal", "pregnancy test"]):
        return ("laboratory results", "routine hospital system or protocol-specific lab", "medium")
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
    condition = protocol["disease_condition"]
    intervention = clean_intervention_query(protocol["intervention_or_drug_class"])
    phase = protocol["trial_phase"]
    planned_queries = [
        make_clinical_trials_query("baseline_drug_class", condition, intervention, max_studies)
    ]
    for term in REPRESENTATIVE_GLP1_TERMS:
        planned_queries.append(make_clinical_trials_query(f"representative_drug_{term}", condition, term, max_studies))

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
            "representative_drug_terms": REPRESENTATIVE_GLP1_TERMS,
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


def score_condition(study: dict[str, Any]) -> tuple[int, str]:
    text = study_text(study)
    if "type 2 diabetes" in text or "t2dm" in text or "diabetes mellitus, type 2" in text:
        return 2, "matches type 2 diabetes population"
    if "diabetes" in text:
        return 1, "mentions diabetes but type/subgroup match is weaker"
    return 0, "does not clearly match diabetes condition"


def score_intervention(study: dict[str, Any]) -> tuple[int, str]:
    intervention_text = " ".join(
        str(intervention.get("name", ""))
        for intervention in study.get("interventions", [])
    ).lower()
    context_text = study_text(study)
    direct_terms = [
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
    ]
    adjacent_terms = ["glp-1", "glp1", "gpr119", "incretin"]
    if any(term in intervention_text for term in direct_terms):
        return 3, "direct GLP-1 receptor agonist or representative drug match"
    if any(term in intervention_text for term in adjacent_terms):
        return 1, "GLP-1-adjacent or incretin-mechanism intervention"
    if any(term in context_text for term in direct_terms + adjacent_terms):
        return 1, "GLP-1 appears in title or eligibility context, but not as the extracted intervention"
    return 0, "no clear GLP-1 intervention match"


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


def score_endpoint(study: dict[str, Any]) -> tuple[int, str]:
    text = " ".join(
        str(outcome.get("measure", "")) + " " + str(outcome.get("time_frame", ""))
        for outcome in study.get("primary_outcomes", []) + study.get("secondary_outcomes", [])
    ).lower()
    endpoint_terms = ["hba1c", "a1c", "weight", "glucose", "glycemic", "glycaemic", "metabolic", "adverse", "safety"]
    matches = sorted({term for term in endpoint_terms if term in text})
    if len(matches) >= 2:
        return 2, "endpoint terms match: " + ", ".join(matches[:4])
    if len(matches) == 1:
        return 1, "one endpoint term matches: " + matches[0]
    return 0, "no key metabolic/safety endpoint match"


def score_eligibility(study: dict[str, Any]) -> tuple[int, str]:
    text = str(study.get("eligibility_criteria_excerpt", "")).lower()
    useful_terms = ["hba1c", "a1c", "egfr", "renal", "kidney", "pregnancy", "pancreatitis", "insulin", "glp"]
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


def rank_sources(sources: dict[str, Any]) -> dict[str, Any]:
    ranked = []
    for study in sources.get("studies", []):
        condition_score, condition_reason = score_condition(study)
        intervention_score, intervention_reason = score_intervention(study)
        phase_score, phase_reason = score_phase(study)
        endpoint_score, endpoint_reason = score_endpoint(study)
        eligibility_score, eligibility_reason = score_eligibility(study)
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
    return f"""# Scenario 001 Hospital Data-Readiness Table

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


def extract_hba1c_hint(criteria: str) -> str:
    text = " ".join(criteria.split())
    if not re.search(r"hba1c|hemoglobin a1c|glycosylated", text, flags=re.IGNORECASE):
        return "not found in excerpt"

    sentences = re.split(r"(?<=[.!?])\s+|\s+\*\s+|\s+\d+\.\s+", text)
    candidates = [
        sentence
        for sentence in sentences
        if re.search(r"hba1c|hemoglobin a1c|glycosylated", sentence, flags=re.IGNORECASE)
    ]
    if candidates:
        return markdown_cell(candidates[0], max_chars=170)
    return markdown_cell(text, max_chars=170)


def keyword_presence(criteria: str, keywords: list[str]) -> str:
    lower = criteria.lower()
    found = [keyword for keyword in keywords if keyword in lower]
    return ", ".join(found) if found else "not found in excerpt"


def top_trial_comparison_table(sources_ranked: dict[str, Any], max_rows: int = 5) -> str:
    studies = sources_ranked.get("ranked_studies", [])
    if not studies:
        return "No ranked records are available for comparison."

    rows = [
        "| Rank | NCT ID | Score | Phase | Intervention | Primary Endpoint | HbA1c Eligibility Hint | Safety/Exclusion Hints |",
        "| ---: | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(studies[:max_rows], start=1):
        study = item["study"]
        criteria = study.get("eligibility_criteria_excerpt", "")
        phase = markdown_cell(", ".join(study.get("phases", [])) or "not listed", max_chars=60)
        safety_hints = keyword_presence(
            criteria,
            ["renal", "kidney", "egfr", "pancreatitis", "pregnancy", "pregnant", "glp-1", "glp1", "insulin"],
        )
        rows.append(
            "| {rank} | `{nct}` | {score}/10 | {phase} | {intervention} | {endpoint} | {hba1c} | {safety} |".format(
                rank=index,
                nct=item["nct_id"],
                score=item["relevance_score"],
                phase=phase,
                intervention=intervention_summary(study),
                endpoint=outcome_summary(study.get("primary_outcomes", [])),
                hba1c=extract_hba1c_hint(criteria),
                safety=markdown_cell(safety_hints, max_chars=120),
            )
        )
    return "\n".join(rows)


def make_top_trial_comparison(normalized: dict[str, Any], sources_ranked: dict[str, Any], max_rows: int = 5) -> str:
    protocol = normalized["protocol"]
    return f"""# Scenario 001 Top Trial Comparison

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

- Use the HbA1c eligibility hints to decide whether the draft protocol needs a numeric HbA1c range.
- Use the safety/exclusion hints to check whether renal impairment, pancreatitis, pregnancy, prior GLP-1 exposure, and insulin-related criteria need explicit definitions.
- Use endpoint timing to compare whether week 24 is plausible or whether similar trials use materially different timing.
- Treat every item as a comparison candidate that still needs clinical expert review.

## Current Decision

Keep this table as the compact reviewer-facing comparison view for Scenario 001.
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

    return f"""# Scenario 001 Source Relevance Review

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

- review whether the expanded query terms should be adjusted before creating Scenario 002.
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


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def make_draft_report(
    normalized: dict[str, Any],
    checklist: dict[str, Any],
    data_readiness: dict[str, Any],
    source_plan: dict[str, Any],
    sources: dict[str, Any],
    sources_ranked: dict[str, Any],
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

    return f"""# Scenario 001 Draft Pre-Review Report

## Review Summary

This is a deterministic pre-review report for `{normalized['scenario_id']}`. It reviews a synthetic early protocol outline for {protocol['disease_condition']} and {protocol['intervention_or_drug_class']}.

This report is for planning and expert review preparation only. It does not approve the protocol, certify regulatory compliance, make patient-specific recommendations, or use real patient data.

## Protocol Completeness Checklist

{bullet_list([f"{row['field']}: {row['status']}" for row in checklist['field_presence']])}

## Similar-Trial / Evidence Items To Check

{source_notes(source_plan, sources, sources_ranked)}

Fields to compare later:

{bullet_list(source_plan['fields_to_compare_later'])}

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

Limitations:

- This report uses local fixture data only.
- It does not validate scientific correctness.
- It does not replace PI, CRC, IRB/regulatory, sponsor, or medical data-team review.
- {source_limitation}

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
    return f"""# Scenario 001 Score Sheet

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
    if args.fetch_sources:
        sources = fetch_clinical_trials_sources(source_plan, args.source_timeout)
        source_plan["live_retrieval_performed"] = sources.get("retrieval_status") in ["success", "partial_success"]
        source_plan["retrieval_status"] = sources.get("retrieval_status")
        source_plan["reason"] = "Live retrieval requested with --fetch-sources."
        if sources.get("retrieval_status") in ["success", "partial_success"]:
            source_plan["limitations"] = sources.get("limitations", [])
    else:
        sources = make_empty_sources(source_plan)
    sources_ranked = rank_sources(sources)
    draft_report = make_draft_report(normalized, checklist, data_readiness, source_plan, sources, sources_ranked)
    critic_review, can_finalize = make_critic_review(draft_report)
    final_report = draft_report.replace(
        "# Scenario 001 Draft Pre-Review Report",
        "# Scenario 001 Final Pre-Review Report",
        1,
    ) if can_finalize else ""
    score_sheet = make_score_sheet(normalized)
    source_relevance_review = make_source_relevance_review(normalized, sources, sources_ranked)
    top_trial_comparison = make_top_trial_comparison(normalized, sources_ranked)
    data_readiness_table = make_data_readiness_table(normalized, data_readiness)

    write_json(run_dir / "normalized_input.json", normalized)
    write_json(run_dir / "checklist_findings.json", checklist)
    write_json(run_dir / "data_readiness.json", data_readiness)
    write_json(run_dir / "source_plan.json", source_plan)
    write_json(run_dir / "sources.json", sources)
    write_json(run_dir / "sources_ranked.json", sources_ranked)
    write_text(run_dir / "source_relevance_review.md", source_relevance_review)
    write_text(run_dir / "top_trial_comparison.md", top_trial_comparison)
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
