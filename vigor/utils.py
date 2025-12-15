import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Any


def get_immediate_subdirectories(
    full_path: str, ignore: list[str] | None = None
) -> list[str]:
    """
    Get all immediate sub-directories for a certain full path.

    Args:
        full_path (str): Path (absolute) to folder to get immediate sub-directories for.
        ignore (Optional[List[str]]): List of folders to ignore. Defaults to None.

    Returns:
        List[str]: List of immediate sub-directory names.
    """
    if not os.path.isabs(full_path):
        raise ValueError("Parameter full_path must be an Absolute Path!")

    if ignore is None:
        ignore = []

    subdirectories = []
    for item in os.scandir(full_path):
        if item.is_dir() and item.name not in ignore:
            subdirectories.append(item.name)

    return subdirectories


class CommandRunner(ABC):
    @abstractmethod
    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """
        Run a command with the given arguments.

        Args:
            *args: Command and its arguments
            **kwargs: Additional keyword arguments for subprocess.run

        Returns:
            subprocess.CompletedProcess: Result of the command execution
        """
        logging.info(f"Command: {args}")
        sys.stdout.flush()

        try:
            return subprocess.run(
                args, shell=False, check=True, encoding="utf-8", **kwargs
            )
        except subprocess.CalledProcessError as e:
            logging.error(
                f"""
                Command ran with {args} resulted in an error:
                {e.stdout if e.stdout else ""}
                {e.stderr if e.stderr else ""}
                """
            )
            raise
