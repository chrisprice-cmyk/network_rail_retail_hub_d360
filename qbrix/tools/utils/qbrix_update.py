from abc import ABC
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_project_tasks import download_and_unzip, replace_file_text
from qbrix.tools.shared.qbrix_console_utils import init_logger
from abc import ABC

from cumulusci.core.tasks import BaseTask

from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import download_and_unzip, replace_file_text

log = init_logger()


class QBrixUpdater(BaseTask, ABC):
    task_options = {
        "UpdateLocation": {
            "description": "String URL for the location where the update package .zip file is located",
            "required": False
        },
        "ArchivePassword": {
            "description": "String password for the .zip file",
            "required": False
        },
        "IgnoreOptionalUpdates": {
            "description": "True or False - When True this will ignore any Optional Updates being added to the project.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(QBrixUpdater, self)._init_options(kwargs)
        self.ArchivePassword = self.options["ArchivePassword"] if "ArchivePassword" in self.options else None
        self.UpdateLocation = self.options[
            "UpdateLocation"] if "UpdateLocation" in self.options else "https://qnextgen.s3.us-west-1.amazonaws.com/qbrix/q_update_package.zip"
        self.IgnoreOptionalUpdates = self.options[
            "IgnoreOptionalUpdates"] if "IgnoreOptionalUpdates" in self.options else False

    def _check_and_deploy_class(self, tasks: dict):

        with open("cumulusci.yml", "r") as cci_file:
            cci_file.seek(0)
            cci_data = cci_file.read()

        for key, value in tasks.items():
            log.info(f"Checking for custom task: {key} with class path {value}...")

            key_index = cci_data.find(f"{key}:")
            value_index = cci_data.find(value)

            if key_index < 0 and value_index < 0:
                replacement_text = f"# CUSTOM TASKS ADDED FOR Q BRIX DEVELOPMENT\n\n  {key}:\n    class_path: {value}"
                replace_file_text("cumulusci.yml", "# CUSTOM TASKS ADDED FOR Q BRIX DEVELOPMENT", replacement_text)
            else:
                log.info(f"Custom task: {key} already exists so skipping.")

    def _run_task(self):

        """" Downloads the update package from AWS S3 and applies updates """

        log.info("Starting Update")

        # Download and Apply Update
        download_and_unzip(self.UpdateLocation, self.ArchivePassword, self.IgnoreOptionalUpdates)

        # Add new custom tasks
        tasks_to_update = {}
        tasks_to_update.update({'qbrix_preflight':'qbrix.tools.utils.qbrix_preflight.RunPreflight'})
        tasks_to_update.update({'qbrix_landing':'qbrix.tools.utils.qbrix_landing.RunLanding'})
        tasks_to_update.update({'analytics_manager':'qbrix.tools.data.qbrix_analytics.AnalyticsManager'})
        self._check_and_deploy_class(tasks_to_update)

        log.info("Update Complete. Check the .qbrix/OPTIONAL_UPDATES directory for additional files you may want to change.")
