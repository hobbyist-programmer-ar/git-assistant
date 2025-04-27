# git_assist/modules/sonar_checker.py

import os
import re
from pathlib import Path
from datetime import datetime
from utils.logger import Logger
from utils.shell_utils import ShellUtils


class SonarChecker:
    def __init__(self, logger: Logger, report_dir: str = "git-assist/sonar-report"):
        self.logger = logger
        self.report_dir = Path(report_dir)
        self.jacoco_xml_path = self.report_dir / "jacoco.xml"
        self.summary_report_path = self.report_dir / "sonar_summary.md"
        self.sonar_log_path = self.report_dir / "sonar_verbose.log"
        self._prepare_report_directory()

    def _prepare_report_directory(self):
        if not self.report_dir.exists():
            self.logger.highlight(f"📂 Creating report directory at {self.report_dir}")
            self.report_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        self.logger.highlight("🧪 Running SonarQube and Jacoco checks...")

        self._check_prerequisites()

        # Run SonarQube and capture verbose output
        sonar_output = ShellUtils.run_command(
            "sonar-scanner -Dsonar.verbose=true -Dproject.settings=sonar-project.properties",
            check=True,
            capture_output=True
        )

        # Save log
        with self.sonar_log_path.open("w") as log_file:
            log_file.write(sonar_output)

        # Copy Jacoco report if it exists
        if os.path.exists("target/site/jacoco/jacoco.xml"):
            ShellUtils.run_command(f"cp target/site/jacoco/jacoco.xml {self.jacoco_xml_path}")

        coverage = self._parse_coverage()
        critical, blocker, major = self._parse_issues_from_log(sonar_output)

        self.logger.highlight(f"📊 Coverage: {coverage}%")
        self.logger.highlight(f"🔴 Critical: {critical}, 🛑 Blocker: {blocker}, ⚠️ Major: {major}")

        self._write_markdown_summary(coverage, critical, blocker, major)

        if coverage < 80 or critical > 0 or blocker > 0 or major > 2:
            self.logger.warn("⚠️ Validation failed: low coverage or critical issues found.")
            user_input = input("Do you want to fix these issues before proceeding? (y/n): ")
            if user_input.lower() == "y":
                self.logger.error("⛔ Aborting due to SonarQube/Jacoco issues.")
                raise Exception("Validation failed.")
            else:
                self.logger.warn("⚠️ Continuing despite warnings.")
        else:
            self.logger.success("✅ SonarQube and Jacoco validation passed.")

    def _check_prerequisites(self):
        if not os.path.exists("sonar-project.properties"):
            raise FileNotFoundError("❌ sonar-project.properties file not found.")
        for tool in ["jq", "sonar-scanner"]:
            if not ShellUtils.run_command(f"which {tool}", capture_output=True):
                raise EnvironmentError(f"❌ Required tool '{tool}' not found in PATH.")

    def _parse_coverage(self):
        if not self.jacoco_xml_path.is_file():
            raise FileNotFoundError(f"❌ Jacoco report missing at {self.jacoco_xml_path}.")

        with self.jacoco_xml_path.open("r") as file:
            content = file.read()

        coverage_match = re.search(r'<counter type="INSTRUCTION" missed="(\d+)" covered="(\d+)"', content)
        if not coverage_match:
            raise ValueError("❌ Unable to parse coverage from Jacoco report.")

        missed, covered = map(int, coverage_match.groups())
        total = missed + covered
        return round((covered / total) * 100, 2) if total else 0

    def _parse_issues_from_log(self, log_output: str):
        # Initialize counters
        critical = blocker = major = 0

        for line in log_output.splitlines():
            if "severity=CRITICAL" in line:
                critical += 1
            elif "severity=BLOCKER" in line:
                blocker += 1
            elif "severity=MAJOR" in line:
                major += 1

        return critical, blocker, major

    def _write_markdown_summary(self, coverage, critical, blocker, major):
        with self.summary_report_path.open("w") as f:
            f.write("# 🧾 SonarQube & Jacoco Report Summary\n\n")
            f.write(f"**🕒 Generated on:** `{datetime.now().isoformat(sep=' ', timespec='seconds')}`\n\n")
            f.write(f"**📊 Code Coverage:** `{coverage}%`\n\n")
            f.write("| Severity | Count |\n")
            f.write("|----------|-------|\n")
            f.write(f"| 🔴 Critical | {critical} |\n")
            f.write(f"| 🛑 Blocker  | {blocker} |\n")
            f.write(f"| ⚠️ Major     | {major} |\n\n")
            f.write(f"📄 **Verbose log:** [`sonar_verbose.log`]({self.sonar_log_path})\n")
