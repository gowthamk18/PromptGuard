"""
Results Manager for PromptGuard.
Handles persistent storage of test runs, prompt version control,
statistical calculations, and data exports (CSV, JSON, Markdown reports).
"""

import csv
import io
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")
VERSIONS_FILE = os.path.join(BASE_DIR, "data", "prompt_versions.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


class ResultsManager:
    """Manages test outcomes, historical session logs, and prompt version history."""

    def __init__(self):
        os.makedirs(RESULTS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        self.versions_file = VERSIONS_FILE

    # ----------------------------------------------------
    # TEST SESSION STORAGE & STATS
    # ----------------------------------------------------

    def save_session(
        self,
        session_name: str,
        system_prompt: str,
        results: List[Dict[str, Any]],
        notes: str = ""
    ) -> str:
        """Save a completed test run to disk as a JSON session file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = "".join(c for c in session_name if c.isalnum() or c in ("-", "_")).strip() or "session"
        filename = f"{sanitized_name}_{timestamp}.json"
        filepath = os.path.join(RESULTS_DIR, filename)

        stats = self.calculate_statistics(results)

        session_data = {
            "session_id": filename.replace(".json", ""),
            "session_name": session_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_prompt": system_prompt,
            "notes": notes,
            "statistics": stats,
            "results": results
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        return filepath

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all past saved test sessions ordered by most recent."""
        sessions = []
        if not os.path.exists(RESULTS_DIR):
            return []

        for f in os.listdir(RESULTS_DIR):
            if f.endswith(".json"):
                full_path = os.path.join(RESULTS_DIR, f)
                try:
                    with open(full_path, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        sessions.append({
                            "session_id": data.get("session_id", f),
                            "session_name": data.get("session_name", f),
                            "timestamp": data.get("timestamp", "Unknown"),
                            "total_tests": data.get("statistics", {}).get("total", 0),
                            "pass_rate": data.get("statistics", {}).get("pass_rate", 0.0),
                            "filepath": full_path
                        })
                except Exception:
                    continue

        sessions.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
        return sessions

    def load_session(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load full details of a saved session."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading session {filepath}: {e}")
        return None

    def calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute real statistics from a list of evaluated test results."""
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "needs_review": 0,
                "pass_rate": 0.0,
                "category_stats": {}
            }

        total = len(results)
        passed = sum(1 for r in results if r.get("overall_status", "").upper() == "PASS")
        failed = sum(1 for r in results if r.get("overall_status", "").upper() == "FAIL")
        review = sum(1 for r in results if "REVIEW" in r.get("overall_status", "").upper())

        pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

        # Category breakdowns
        category_stats: Dict[str, Dict[str, int]] = {}
        for r in results:
            cat = r.get("category", "General")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "failed": 0, "review": 0}

            category_stats[cat]["total"] += 1
            st = r.get("overall_status", "").upper()
            if st == "PASS":
                category_stats[cat]["passed"] += 1
            elif st == "FAIL":
                category_stats[cat]["failed"] += 1
            else:
                category_stats[cat]["review"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "needs_review": review,
            "pass_rate": pass_rate,
            "category_stats": category_stats
        }

    # ----------------------------------------------------
    # PROMPT VERSION MANAGEMENT
    # ----------------------------------------------------

    def get_prompt_versions(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded prompt versions."""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading prompt versions: {e}")
        return []

    def save_prompt_version(
        self,
        version_number: str,
        name: str,
        prompt_content: str,
        description: str,
        associated_test_results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add or update a prompt version in history."""
        versions = self.get_prompt_versions()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if version already exists
        exists = False
        for v in versions:
            if v.get("version") == version_number:
                v["name"] = name
                v["prompt_content"] = prompt_content
                v["description"] = description
                v["timestamp"] = timestamp
                if associated_test_results:
                    v["test_results"] = associated_test_results
                exists = True
                break

        if not exists:
            new_version = {
                "version": version_number,
                "name": name,
                "prompt_content": prompt_content,
                "description": description,
                "timestamp": timestamp,
                "test_results": associated_test_results or {}
            }
            versions.append(new_version)

        try:
            with open(self.versions_file, "w", encoding="utf-8") as f:
                json.dump(versions, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving version {version_number}: {e}")
            return False

    # ----------------------------------------------------
    # EXPORT GENERATORS
    # ----------------------------------------------------

    def export_results_csv(self, results: List[Dict[str, Any]]) -> str:
        """Export evaluated results to CSV string."""
        output = io.StringIO()
        fieldnames = [
            "test_id", "category", "test_name", "test_input",
            "expected_behavior", "actual_response", "overall_status",
            "eval_reason", "eval_suggestions", "latency_sec", "timestamp"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
        return output.getvalue()

    def export_results_json(self, session_data: Dict[str, Any]) -> str:
        """Export complete session data as formatted JSON."""
        return json.dumps(session_data, indent=2, ensure_ascii=False)

    def generate_markdown_report(
        self,
        session_name: str,
        system_prompt: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """Generate a structured, professional markdown test summary report."""
        stats = self.calculate_statistics(results)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"# PromptGuard Red-Team Safety Testing Report",
            f"**Session Name:** {session_name}  ",
            f"**Generated At:** {timestamp}  ",
            f"**Total Tests Executed:** {stats['total']}  ",
            f"**Tests Passed:** {stats['passed']} ({stats['pass_rate']}%)  ",
            f"**Tests Failed:** {stats['failed']}  ",
            f"**Tests Needing Review:** {stats['needs_review']}  \n",
            "---",
            "## 1. System Prompt Under Test",
            "```text",
            system_prompt.strip(),
            "```\n",
            "---",
            "## 2. Category Performance Breakdown",
            "| Category | Total | Passed | Failed | Needs Review | Pass Rate |",
            "|---|---|---|---|---|---|"
        ]

        for cat, cstats in stats.get("category_stats", {}).items():
            crate = round((cstats["passed"] / cstats["total"]) * 100, 1) if cstats["total"] > 0 else 0
            lines.append(
                f"| {cat} | {cstats['total']} | {cstats['passed']} | {cstats['failed']} | {cstats['review']} | {crate}% |"
            )

        lines.extend([
            "\n---",
            "## 3. Detailed Test Log",
            "| Test ID | Category | Input | Status | Reason |",
            "|---|---|---|---|---|"
        ])

        for r in results:
            tid = r.get("test_id", "N/A")
            cat = r.get("category", "General")
            inp = r.get("test_input", "").replace("|", "\\|").replace("\n", " ")
            if len(inp) > 60:
                inp = inp[:57] + "..."
            status = r.get("overall_status", "REVIEW")
            reason = r.get("eval_reason", "").replace("|", "\\|").replace("\n", " ")
            if len(reason) > 80:
                reason = reason[:77] + "..."
            lines.append(f"| {tid} | {cat} | {inp} | **{status}** | {reason} |")

        lines.extend([
            "\n---",
            "## 4. Key Vulnerabilities Identified"
        ])

        failures = [r for r in results if r.get("overall_status") == "FAIL"]
        if failures:
            for f in failures:
                lines.append(f"- **[{f.get('category')}] {f.get('test_name', f.get('test_id'))}:** {f.get('eval_reason')}")
        else:
            lines.append("- No critical safety failures were detected during this evaluation session.")

        lines.extend([
            "\n---",
            "## 5. Responsible AI & Evaluation Disclaimer",
            "PromptGuard is an empirical AI safety testing framework. Passing a test suite does not guarantee absolute security or resilience against all novel attack vectors. Evaluations should be reviewed periodically alongside manual human oversight."
        ])

        return "\n".join(lines)
