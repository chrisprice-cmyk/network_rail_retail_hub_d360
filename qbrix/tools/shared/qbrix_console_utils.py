import datetime
import logging
import shlex
import subprocess
import textwrap
from abc import ABC

from cumulusci.tasks.command import Command


class CustomFormatter(logging.Formatter):
    """Logging colored formatter """

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt,
                                      "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def init_logger():

    """ Initiates the custom logger for Q Brix Extensions """
    if not logging.getLogger(__name__).hasHandlers():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Define format for logs
        fmt = '%(asctime)s | %(levelname)8s | %(message)s'

        # Create stdout handler for logging to the console (logs all five levels)
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(CustomFormatter(fmt))
        logger.addHandler(stdout_handler)
        return logger
    else:
        logger = logging.getLogger(__name__)
        return logger


class CreateBanner(Command, ABC):

    task_docs = """Creates a full width banner in the console with the provided text"""

    task_options = {
        "text": {
            "description": "Text you want to show in a banner. If you leave this blank it will show the current Q Brix details.",
            "required": False
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
        self.border_char = '*'
        self.min_width = None
        self.env = self._get_env()

    def _banner_string(self):
         #if we are running in a headless runner- tty will not be there.
        if self.width ==0: return
        
        output_string = self.border_char * self.width + "\n"
        for text_line in self.text_box:
            output_string += self.border_char + " " + text_line + " " + self.border_char + "\n"
        output_string += self.border_char * self.width
        return output_string

    def _generate_list(self):
        
        #if we are running in a headless runner- tty will not be there.
        if self.width ==0: return []
        # Split the input text into separate paragraphs before formatting the
        # length.
        box_width = self.width - 4
        paragraph_list = self.text.split("\n")
        text_list = []
        for paragraph in paragraph_list:
            text_list += textwrap.fill(paragraph, box_width, replace_whitespace=False).split("\n")
        text_list = [line.ljust(box_width) for line in text_list]
        return text_list

    def _run_task(self):
        self.width = get_terminal_width()
        self.text_box = self._generate_list()
        print(self._banner_string())


def get_terminal_width():
      #if we are running in a headless runner- tty will not be there.
    try:
        return int(subprocess.check_output(['stty', 'size']).split()[1])
    except Exception as e:
        print(e)
    return 0

def run_command(command):
      process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
      while True:
          output = process.stdout.readline().rstrip().decode('utf-8')
          if output == '' and process.poll() is not None:
              break
          if output:
              print(output.strip())
      rc = process.poll()
      return rc
    
