# git_assist/modules/maven_build.py

from utils.logger import Logger
from utils.shell_utils import ShellUtils

class MavenBuild:
    def __init__(self, logger: Logger):
        self.logger = logger

    def run(self):
        self.logger.highlight("🔧 Running mvn clean install...")
        try:
            ShellUtils.run_command("mvn clean install", check=True)
            self.logger.success("✅ Maven build successful")
        except Exception as e:
            self.logger.error(f"❌ Maven build failed: {e}")
            raise
