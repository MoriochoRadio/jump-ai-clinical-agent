from pathlib import Path
import unittest


class ReviewerDashboardArtifactTests(unittest.TestCase):
    def test_scenario_002_dashboard_preserves_scope_and_trace_links(self):
        dashboard_path = Path("dashboard/scenario_002_review.html")
        html = dashboard_path.read_text(encoding="utf-8")

        self.assertIn("Scenario 002 Reviewer Dashboard", html)
        self.assertIn("No real patient data", html)
        self.assertIn("no EMR/HIS integration", html)
        self.assertIn("no protocol approval", html)
        self.assertIn("../prototype/runs/scenario_002_run_001/reviewer_summary.md", html)
        self.assertIn("../prototype/runs/scenario_002_run_001/final_report.md", html)
        self.assertIn("../prototype/runs/scenario_002_run_001/score.md", html)
        self.assertIn("Source of truth: committed CLI outputs", html)

        linked_outputs = [
            "prototype/runs/scenario_002_run_001/reviewer_summary.md",
            "prototype/runs/scenario_002_run_001/final_report.md",
            "prototype/runs/scenario_002_run_001/top_trial_comparison.md",
            "prototype/runs/scenario_002_run_001/eligibility_criteria_extraction.json",
            "prototype/runs/scenario_002_run_001/pubmed_manual_screening.json",
            "prototype/runs/scenario_002_run_001/score.md",
        ]
        for output_path in linked_outputs:
            self.assertTrue(Path(output_path).exists(), output_path)


if __name__ == "__main__":
    unittest.main()
