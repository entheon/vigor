import os
import subprocess
from typing import Any

from vigor.utils import CommandRunner


class Compose(CommandRunner):
    """
    Runs commands using CommandRunner's run function.

    Project name is specified here so that every instance of Compose has the same
    name. Extension: Project directory could also be set here as well.
    """

    def __init__(self, project_name: str):
        self.project_name = project_name

    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """
        Runs commands using CommandRunner's run function.

        Extension: Project directory could also be set here as well.

        Returns:
            subprocess.CompletedProcess[str]: Result of the command execution
        """
        params = ["docker", "compose", "-p", self.project_name]
        params.extend(args)

        return super().run(*params, capture_output=True)

    def generate_compose_file(self, files: list[str], env: str | None = None) -> str:
        """
        Generates aggregated Compose file using Docker Compose's built-in config
        command.

        Args:
            files (List[str]): List of Docker Compose files (absolute path) to
                aggregate together.
            env (Optional[str]): Absolute path to aggregated env file.
                Defaults to None.

        Returns:
            str: Parsed and interpolated valid Compose file, in string.
        """
        params = []

        if env:
            if not os.path.isabs(env):
                raise ValueError("Environment file (.env) must be an Absolute Path!")

            params.append("--env-file")
            params.append(env)

        for file in files:
            if not os.path.isabs(file):
                raise ValueError("Compose files must be an Absolute Path!")

            params.append("--file")
            params.append(file)

        params.append("config")

        result = self.run(*params)
        return result.stdout
