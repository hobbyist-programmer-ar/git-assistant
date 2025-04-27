# git_assist/modules/pusher.py

import subprocess
from utils.logger import Logger
from utils.shell_utils import ShellUtils

class Pusher:
    def __init__(self, logger: Logger):
        self.logger = logger

    def push_to_remote(self):
        try:
            branch = ShellUtils.capture_output("git rev-parse --abbrev-ref HEAD")
        except subprocess.CalledProcessError as e:
            # Handle the case where `git rev-parse` fails and return a custom error message
            self.logger.error(f"❌ Error: {e.stderr.strip()}")
            return

        protected_branches = ["main", "master", "develop", "dev"]

        if branch in protected_branches:
            self.logger.warn(f"⚠️ You are on a protected branch: {branch}")
            confirm = input(f"Do you really want to push to '{branch}'? (y/n): ").strip().lower()
            if confirm != 'y':
                self.logger.error("⛔ Push cancelled.")
                return

        self.logger.highlight(f"🚀 Pushing to origin/{branch}...")
        try:
            # Try pushing to the remote repository
            ShellUtils.run_command(f"git push -u origin {branch}", capture_output=True)
            self.logger.success("✅ Push complete.")
        except subprocess.CalledProcessError as e:
            # Error in case push fails
            self.logger.error(f"❌ Push failed: {e.stderr.strip() if e.stderr else 'Unknown error'}")
