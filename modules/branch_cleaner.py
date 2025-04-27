# git_assist/modules/branch_cleaner.py

import subprocess
from utils.logger import Logger
from utils.shell_utils import ShellUtils

class BranchCleaner:
    def __init__(self, logger: Logger):
        self.logger = logger

    def clean_merged_branches(self):
        self.logger.highlight("🧹 Cleaning up remote merged branches...")

        ShellUtils.run_command("git fetch --all --prune")

        bases = ["develop", "dev", "main", "master"]
        base_branch = None

        for base in bases:
            if ShellUtils.command_success(f"git show-ref --verify --quiet refs/remotes/origin/{base}"):
                base_branch = base
                break

        if not base_branch:
            self.logger.error("❌ No base branch found (develop, dev, main, master).")
            return

        self.logger.highlight(f"📥 Pulling latest for base branch: {base_branch}")
        ShellUtils.run_command(f"git checkout {base_branch}")
        ShellUtils.run_command(f"git pull origin {base_branch}")

        merged_branches_raw = ShellUtils.capture_output(f"git branch -r --merged origin/{base_branch}")
        merged_branches = [
            branch.strip().replace("origin/", "")
            for branch in merged_branches_raw.splitlines()
            if branch.strip() and not any(branch.strip().endswith(base) for base in bases)
        ]

        if not merged_branches:
            self.logger.success("✅ No remote merged branches to delete.")
            return

        self.logger.highlight("🌿 Merged branches ready for deletion:")
        for idx, branch in enumerate(merged_branches, start=1):
            print(f" {idx}. {branch}")

        confirm = input("Do you want to delete these merged branches from remote? (y/n): ").strip().lower()
        if confirm != 'y':
            self.logger.warn("⚠️ Deletion aborted by user.")
            return

        for branch in merged_branches:
            if ShellUtils.run_command(f"git push origin --delete {branch}"):
                self.logger.success(f"🗑️ Deleted: {branch}")
            else:
                self.logger.warn(f"⚠️ Failed to delete: {branch}")
