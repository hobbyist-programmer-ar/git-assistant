# git_assist/main.py

import os
from modules.maven_build import MavenBuild
from modules.sonar_checker import SonarChecker
from modules.snyk_checker import SnykChecker
from modules.committer import Committer
from modules.pusher import Pusher
from modules.branch_cleaner import BranchCleaner
from utils.logger import Logger


def main():
    # Ensure log directory and file exist
    log_dir = "git-assist"
    log_file_path = os.path.join(log_dir, "git-assist.log")
    os.makedirs(log_dir, exist_ok=True)
    if not os.path.exists(log_file_path):
        open(log_file_path, 'a').close()

    logger = Logger(log_file=log_file_path)
    sonar_report_dir = "git-assist/sonar-reports"
    snyk_report_dir = "git-assist/snyk-reports"

    builder = MavenBuild(logger)
    sonar = SonarChecker(logger, report_dir=sonar_report_dir)
    snyk = SnykChecker(logger, report_dir=snyk_report_dir)
    committer = Committer(logger)
    pusher = Pusher(logger)
    cleaner = BranchCleaner(logger)

    menu_options = {
        "1": ("🔧 Run 'mvn clean install'", builder.run),
        "2": ("🧪 Run SonarQube and Jacoco checks", sonar.run),
        "3": ("🔎 Run Snyk test and generate report", snyk.run),
        "4": ("📝 Stage and commit git changes", committer.stage_and_commit),
        "5": ("🚀 Push to remote branch", pusher.push_to_remote),
        "6": ("⚙️ Execute All (1, 2, 3, 4)", lambda: [
            builder.run(),
            sonar.run(),
            snyk.run(),
            committer.stage_and_commit(),
            pusher.push_to_remote()
        ]),
        "7": ("🧹 Clean merged remote branches", cleaner.clean_merged_branches),
        "8": ("❌ Exit", exit)
    }

    while True:
        logger.highlight("🎛️ Git Assistant Menu")
        for key, (desc, _) in menu_options.items():
            print(f"  {key}) {desc}")

        choice = input("Enter your selection (e.g. 1 3 4): ").strip().split()

        for option in choice:
            action = menu_options.get(option)
            if action:
                _, func = action
                try:
                    func()
                except Exception as e:
                    logger.error(f"❌ Error executing option {option}: {e}")
            else:
                logger.warn(f"❓ Unknown option: {option}")

        print("")
        logger.highlight("✅ Task(s) completed. Back to main menu...\n")


if __name__ == "__main__":
    main()
