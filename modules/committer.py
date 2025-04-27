import subprocess
import os
from utils.logger import Logger
from utils.shell_utils import ShellUtils
from utils.config_reader import ConfigReader

class Committer:
    def __init__(self, logger: Logger):
        self.logger = logger

    def stage_and_commit(self):
        self.logger.highlight("📁 Checking Git status...")

        untracked_files = self._get_untracked_files()
        modified_files = self._get_modified_files()
        files_to_add = []

        # Handle untracked files
        for file_path in untracked_files:
            if not self._is_ignored(file_path):
                add = input(f"Add untracked file '{file_path}'? (y/n): ")
                if add.lower() == 'y':
                    files_to_add.append(file_path)

        # Handle modified but unstaged files
        for file_path in modified_files:
            if not self._is_ignored(file_path):
                add = input(f"Add modified file '{file_path}'? (y/n): ")
                if add.lower() == 'y':
                    files_to_add.append(file_path)

        # Handle directories inside those files
        for line in untracked_files + modified_files:
            if os.path.isdir(line):
                add_dir = input(f"Directory '{line}' has been modified. Check each file inside? (y/n): ")
                if add_dir.lower() == "y":
                    for root, dirs, files in os.walk(line):
                        for file in files:
                            file_full_path = os.path.join(root, file)
                            if not self._is_ignored(file_full_path):
                                add_file = input(f"Add file '{file_full_path}'? (y/n): ")
                                if add_file.lower() == "y":
                                    files_to_add.append(file_full_path)
                else:
                    files_to_add.append(line)

        # Handle .gitignore specifically
        if self._is_gitignore_modified():
            add = input("Add modified file '.gitignore'? (y/n): ")
            if add.lower() == 'y':
                files_to_add.append(".gitignore")

        if files_to_add:
            ShellUtils.run_command(f"git add {' '.join(files_to_add)}", check=True)
            self.logger.success(f"✅ Staged {len(files_to_add)} file(s).")
        else:
            self.logger.highlight("📎 No new files staged.")

        staged = self._get_staged_files()
        if not staged:
            self.logger.success("✅ No staged changes to commit.")
            return

        # Jira ticket config
        jira_ticket_prefix = ConfigReader.get_value("JIRA_TICKET_PREFIX", "FINDATA-")
        jira_ticket = input(f"Enter Jira Ticket (e.g., {jira_ticket_prefix}123): ").strip()
        while not jira_ticket.startswith(jira_ticket_prefix):
            self.logger.error(f"❌ Invalid Jira Ticket. Must start with {jira_ticket_prefix}")
            jira_ticket = input("Try again: ").strip()

        # Commit message
        commit_message = input("Enter commit message: ").strip()
        if not commit_message:
            self.logger.error("❌ Commit message cannot be empty!")
            return

        full_message = f"{jira_ticket}: {commit_message}"
        ShellUtils.run_command(f'git commit -m "{full_message}"', check=True)
        self.logger.success("✅ Commit successful.")

    def _get_untracked_files(self):
        try:
            output = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"])
            return output.decode().strip().splitlines()
        except subprocess.CalledProcessError:
            return []

    def _get_modified_files(self):
        try:
            output = subprocess.check_output(["git", "diff", "--name-only"])
            return output.decode().strip().splitlines()
        except subprocess.CalledProcessError:
            return []

    def _get_staged_files(self):
        try:
            output = subprocess.check_output(["git", "diff", "--cached", "--name-only"])
            return output.decode().strip().splitlines()
        except subprocess.CalledProcessError:
            return []

    def _is_ignored(self, file_path: str) -> bool:
        try:
            subprocess.check_output(["git", "check-ignore", "-q", file_path])
            return True
        except subprocess.CalledProcessError:
            return False

    def _is_gitignore_modified(self):
        try:
            status = subprocess.check_output(["git", "status", "--porcelain", ".gitignore"]).decode().strip()
            return status.startswith("M")
        except subprocess.CalledProcessError:
            return False
