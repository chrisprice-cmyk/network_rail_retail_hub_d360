import logging
import os
import shlex
import subprocess
import sys
import textwrap
from abc import ABC

from cumulusci.cli.logger import init_logger as cci_init_logger
from cumulusci.tasks.command import Command


def init_logger():
    """
    Initiates cumulusci logger for static methods

    Usage:
        from qbrix.tools.shared.qbrix_console_utils import init_logger

        def test_func():
            logger = init_logger()
            logger.info("hey")

    """

    cci_init_logger(False)
    logger = logging.getLogger("cumulusci")
    return logger


class CreateBanner(Command, ABC):
    task_docs = """Creates a full width banner in the console with the provided text"""

    task_options = {
        "text": {
            "description": "Text you want to show in a banner. If you leave this blank it will show the current Q Brix details.",
            "required": False,
        }
    }

    def _init_options(self, kwargs):
        super(CreateBanner, self)._init_options(kwargs)
        self.text = ""
        if "text" in self.options:
            self.text = self.options["text"]
        else:
            self.text = f"{self.project_config.project__name}\n\nAPI VERSION: {self.project_config.project__package__api_version}\nREPO URL:    {self.project_config.project__git__repo_url}"

        self.width = None
        self.text_box = None
        self.max_width = None
        self.border_char = "*"
        self.min_width = None
        self.env = self._get_env()

    def _banner_string(self):
        # if we are running in a headless runner- tty will not be there.
        if self.width == 0:
            return

        output_string = self.border_char * self.width + "\n"
        for text_line in self.text_box:
            output_string += (
                self.border_char + " " + text_line + " " + self.border_char + "\n"
            )
        output_string += self.border_char * self.width
        return output_string

    def _generate_list(self):
        # if we are running in a headless runner- tty will not be there.
        if self.width == 0:
            return []
        # Split the input text into separate paragraphs before formatting the
        # length.
        box_width = self.width - 4
        paragraph_list = self.text.split("\n")
        text_list = []
        for paragraph in paragraph_list:
            text_list += textwrap.fill(
                paragraph, box_width, replace_whitespace=False
            ).split("\n")
        text_list = [line.ljust(box_width) for line in text_list]
        return text_list

    def _run_task(self):
        self.width = get_terminal_width()
        self.text_box = self._generate_list()
        print(self._banner_string())


def get_terminal_width():
    # if we are running in a headless runner- tty will not be there.
    try:
        return int(subprocess.check_output(["stty", "size"]).split()[1])
    except Exception as e:
        print(e)
    return 0


def run_command(cmd: str, cwd=None, silent=False) -> int:
    """
    Runs a command as a subprocess and returns the result code

    Args:
        command (str): string command statement
        cwd (str): (Optional) Current Working Directory override

    Returns:
        (int) code (0 = success, 1 or above = error/failure)
    """

    log = init_logger()

    # Check Command
    if cmd:
        # Blacklisted Command Keywords
        blacklisted_keywords = {
            "rm",
            "shutdown",
            "reboot",
            "dd",
            "mkfs",
            "fdisk",  # Linux/Unix commands
            "del",
            "format",
            "rmdir",
            "rd",
            "sfc",
            "chkdsk",
            "move",
            "attrib",  # Windows commands
            "mv",
            "chmod",
            "chown",
            "sudo",
            "kill",
            "killall",
            "iptables",  # More Linux/Unix commands
        }

        # Check if any blacklisted keyword is in the command
        if any(keyword in cmd.split() for keyword in blacklisted_keywords):
            raise ValueError(f"Dangerous command detected: {cmd}")

    else:
        raise ValueError(
            "No command was passed to the run_command function. Stopping script."
        )

    # Check Current Working Directory
    if not cwd:
        cwd = "."
    cwd = os.path.normpath(cwd)

    if not silent:
        log.info("Running Command: [%s] in directory [%s]...", cmd, cwd)
    try:
        process_result = subprocess.check_call(cmd, shell=True, cwd=cwd)

        if not silent:
            log.info(f" -> Command [{cmd}] succeeded, returned: {str(process_result)}")
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            log.info(e)
            return 0
        sys.exit("'%s' failed, returned code %d" % (cmd, e.returncode))
    except OSError as e:
        sys.exit("failed to run shell: '%s'" % (str(e)))

    return process_result
