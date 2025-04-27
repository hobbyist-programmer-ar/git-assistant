# git_assist/modules/snyk_checker.py
import os
import json
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any
from utils.logger import Logger
from utils.shell_utils import ShellUtils

class SnykChecker:
    def __init__(self, logger: Logger, report_dir: str = "git-assist/sonar-report"):
        self.logger = logger
        self.report_dir = Path(report_dir)
        self.report_file = self.report_dir / "snyk_report.md"

    def run(self):
        self.logger.highlight("🔍 Running Snyk security check...")
        try:
            # Run snyk and capture JSON output (even on non-zero exit codes)
            snyk_output = ShellUtils.run_command("snyk test --json", check=False, capture_output=True)
            snyk_data = json.loads(snyk_output)
            vulnerabilities = snyk_data.get("vulnerabilities", [])

            # Generate markdown report
            self._generate_markdown_report(vulnerabilities)

            # Check severity levels
            severities = [v["severity"] for v in vulnerabilities]
            if "critical" in severities:
                self.logger.error("⛔ Critical vulnerabilities found! Aborting.")
                raise Exception("Critical vulnerabilities found.")
            elif "high" in severities:
                self.logger.warn("⚠️ High severity vulnerabilities found.")
                user_input = input("Do you want to continue anyway? (y/n): ")
                if user_input.lower() != "y":
                    self.logger.error("⛔ Aborting due to high vulnerabilities.")
                    raise Exception("Aborted due to high severity vulnerabilities.")
                else:
                    self.logger.warn("⚠️ Continuing despite high vulnerabilities.")
            else:
                self.logger.success("✅ Snyk test passed (no critical/high vulnerabilities found).")

        except json.JSONDecodeError:
            self.logger.error("❌ Failed to parse Snyk output.")
            raise
        except Exception as e:
            raise e

    def _generate_markdown_report(self, vulnerabilities: list[dict[str, Any]]):
        if not self.report_dir.exists():
            self.report_dir.mkdir(parents=True)

        with self.report_file.open("w") as f:
            f.write("# 🔐 Snyk Vulnerability Report\n\n")
            if not vulnerabilities:
                f.write("✅ No vulnerabilities found.\n")
                return

            # Write table headers
            f.write("| Title | Severity | Package | Version | Fixed In | Maturity | More Info |\n")
            f.write("|-------|----------|---------|---------|----------|----------|-----------|\n")

            # Fill in table rows
            for vuln in vulnerabilities:
                title = vuln.get("title", "Unknown")
                severity = vuln.get("severity", "unknown").capitalize()
                package = vuln.get("packageName", "N/A")
                version = vuln.get("version", "N/A")
                fixed_in = ", ".join(vuln.get("fixedIn", [])) or "Not specified"
                maturity = vuln.get("maturity", "N/A").capitalize()
                url = vuln.get("url", "N/A")

                f.write(f"| {title} | {severity} | {package} | {version} | {fixed_in} | {maturity} | [Link]({url}) |\n")