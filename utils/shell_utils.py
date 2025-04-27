# git_assist/utils/shell_utils.py

import subprocess

class ShellUtils:
    @staticmethod
    def run_command(command, capture_output=False, check=True, shell=True):
        """Run the shell command and raise error if it fails."""
        if capture_output:
            result = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if check and result.returncode != 0:
                # Raise error and pass stderr
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout,
                                                    stderr=result.stderr)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=shell)
            if check and result.returncode != 0:
                # Raise error and pass stderr
                raise subprocess.CalledProcessError(result.returncode, command)

    @staticmethod
    def capture_output(command):
        return ShellUtils.run_command(command, capture_output=True)

    @staticmethod
    def command_success(command):
        return ShellUtils.run_command(command, capture_output=False)
