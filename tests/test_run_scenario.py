import unittest

from prototype.run_scenario import (
    make_eligibility_criteria_extraction,
    make_reviewer_summary,
)


def sample_ranked_sources():
    return {
        "ranked_studies": [
            {
                "nct_id": "NCT00000001",
                "relevance_score": 9,
                "study": {
                    "brief_title": "PD-L1 Immunotherapy in Metastatic NSCLC",
                    "matched_query_labels": ["drug_class"],
                    "eligibility_criteria_excerpt": (
                        "Inclusion Criteria: ECOG performance status 0\u20131. "
                        "Measurable disease by RECIST v1.1. "
                        "Stage IV or metastatic NSCLC. "
                        "PD-L1 TPS \u2265 50%. "
                        "EGFR mutation and ALK translocation negative. "
                        "Exclusion Criteria: active autoimmune disease, pneumonitis, "
                        "or systemic steroid therapy."
                    ),
                    "primary_outcomes": [
                        {
                            "measure": "Progression-free survival by RECIST v1.1",
                            "time_frame": "up to 12 months; imaging every 8 weeks",
                        }
                    ],
                    "secondary_outcomes": [],
                },
            }
        ]
    }


class EligibilityCriteriaExtractionTests(unittest.TestCase):
    def test_extracts_oncology_criteria_without_tps_false_ecog_match(self):
        extraction = make_eligibility_criteria_extraction(sample_ranked_sources())

        self.assertEqual(extraction["extraction_status"], "success")
        self.assertEqual(extraction["extracted_count"], 1)

        record = extraction["records"][0]
        signals = record["extracted_signals"]

        self.assertIn("performance status 0\u20131", signals["ecog"])
        self.assertFalse(any("TPS" in value for value in signals["ecog"]))
        self.assertIn("PD-L1 TPS \u2265 50%", signals["pd_l1"])
        self.assertIn("RECIST v1.1", signals["recist"])
        self.assertIn("up to 12 months", signals["imaging_or_endpoint_timing"])
        self.assertIn("Stage IV", signals["stage_or_extent"])
        self.assertIn("EGFR mutation and ALK translocation negative", signals["biomarker_rules"])
        self.assertIn("pneumonitis", signals["safety_exclusions"])
        self.assertIn("PD-L1", record["extraction_summary"])


class ReviewerSummaryTests(unittest.TestCase):
    def test_reviewer_summary_preserves_traceability_and_safety_boundary(self):
        normalized = {
            "run_id": "scenario_test_run",
            "scenario_id": "scenario_test",
            "protocol": {
                "disease_condition": "Advanced or metastatic non-small cell lung cancer",
                "intervention_or_drug_class": "PD-1/PD-L1 immune checkpoint inhibitor",
                "trial_phase": "Phase II",
                "primary_endpoint": "Progression-free survival.",
            },
        }
        checklist = {
            "findings": [
                {
                    "severity": "high",
                    "finding": "Performance status eligibility is not operationally defined.",
                    "recommendation": "Define the accepted ECOG range.",
                },
                {
                    "severity": "medium",
                    "finding": "Recruitment assumption is provided without feasibility rationale.",
                    "recommendation": "Add screening pool evidence.",
                },
            ]
        }
        data_readiness = {
            "summary": {
                "total_items": 3,
                "high_risk_items": 1,
                "clarification_needed_items": 2,
            },
            "items": [
                {
                    "data_item": "RECIST or tumor response assessment.",
                    "likely_category": "radiology report/images plus research response assessment",
                    "collection_risk": "high",
                }
            ],
        }
        sources = {
            "retrieval_status": "success",
            "studies": [{"nct_id": "NCT00000001"}],
        }
        sources_ranked = sample_ranked_sources()
        pubmed_sources = {
            "retrieval_status": "success",
            "articles": [{"pmid": "123"}, {"pmid": "456"}],
        }
        manual_screening_entries = [
            {
                "pmid": "123",
                "manual_decision": "primary_support_candidate",
                "suggested_use": "Compare endpoint and safety monitoring language.",
            },
            {
                "pmid": "456",
                "manual_decision": "context_only",
                "suggested_use": "Use only as background context.",
            },
        ]
        extraction = make_eligibility_criteria_extraction(sources_ranked)

        summary = make_reviewer_summary(
            normalized,
            checklist,
            data_readiness,
            sources,
            sources_ranked,
            pubmed_sources,
            manual_screening_entries,
            extraction,
            can_finalize=True,
        )

        self.assertIn("# scenario_test Reviewer Summary", summary)
        self.assertIn("Safety critic status: pass", summary)
        self.assertIn("no real patient data and no EMR/HIS integration", summary)
        self.assertIn("primary PubMed support candidates after manual screening: 1", summary)
        self.assertIn("context-only candidates: 1", summary)
        self.assertIn("`NCT00000001` (9/10)", summary)
        self.assertIn("PMID `123`", summary)
        self.assertIn("RECIST or tumor response assessment.", summary)
        self.assertIn("This is not protocol approval", summary)


if __name__ == "__main__":
    unittest.main()
