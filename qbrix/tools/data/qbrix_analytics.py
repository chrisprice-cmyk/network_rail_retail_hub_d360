
from abc import ABC
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import *

log = init_logger()


class DataSetCleaner(BaseTask, ABC):
    task_options = {
      "dataset_folder": {
            "description": "Path to folder which contains .json datasets",
            "required": True
        }
    }

    def _init_options(self, kwargs):
        super(DataSetCleaner, self)._init_options(kwargs)
        self.dataset_folder = self.options["dataset_folder"] if "dataset_folder" in self.options else None

    def _run_task(self):
      wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
      for wave in wave_files:
        log.info(f"Checking {wave}... ")
        # Runs twice to allow for formatted and unformatted files. Potentially replace with regex?
        replace_file_text(wave, f"\"defaultValue\": \"null\"", f"\"defaultValue\": \"0\"")
        replace_file_text(wave, f"\"defaultValue\":\"null\"", f"\"defaultValue\": \"0\"")
      log.info("Cleaning Completed!")
