import filecmp

from abc import ABC
import os
import shutil
from os.path import exists
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import download_and_unzip, replace_file_text

log = init_logger()


class QBrixUpdater(BaseTask, ABC):
    q_branch_location = "https://qbrix-core-stage.herokuapp.com/qbrix/q_update_package.zip"

    task_docs = """
    Updated the Q brix Extension Library and other Q Brix related bundles like GitHub Actions and VSCode Extensions in line with the XDO-Template (main branch). 

    Can also be used to update custom scripts and other custom directories from a .zip file which needs to be hosted somewhere (by setting the URL of the .zip file as the UpdateLocation option), in addition the .zip files can also have a password set and you can specify the password using the ArchivePassword option when running the task.
    """

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
        self.UpdateLocation = self.options["UpdateLocation"] if "UpdateLocation" in self.options else None
        self.IgnoreOptionalUpdates = self.options["IgnoreOptionalUpdates"] if "IgnoreOptionalUpdates" in self.options else False

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

    def update_folder(self, folder_path, update_dir, remove_existing):
        try:
            if exists(folder_path) and remove_existing:
                log.info(f"Removing {folder_path}")
                shutil.rmtree(folder_path)
            update_path = update_dir + "/" + folder_path
            log.info(f"Updating {folder_path} from {update_path}")
            shutil.copytree(src=update_path, dst=folder_path, dirs_exist_ok=True)
        except Exception as e:
            log.error(f"Update Failed: Error details... {e}")

    def _run_task(self):

        """" Downloads the update package from AWS S3 and applies updates """

        log.info("Starting Q Brix Update...")

        shutil.copyfile("qbrix/tools/utils/qbrix_update.py", ".qbrix/qbrix_update.py")

        log.info("Updating Q Brix Library...")
        if download_and_unzip(self.q_branch_location, self.ArchivePassword, False, True):
            # ADD FOLDERS HERE WHICH YOU WANT TO UPDATE IN PROJECT DIRECTORIES
            # PARAM1 = The folder as if it was from the root path
            # PARAM2 = The location where the source files should be located
            # PARAM3 = If True, it will delete the whole directory in project before updating
            self.update_folder("qbrix", ".qbrix/Update/xDO-Template-main", False)
            self.update_folder(".vscode", ".qbrix/Update/xDO-Template-main", False)
            self.update_folder(".github", ".qbrix/Update/xDO-Template-main", False)

            # Finally Clean Up Cached Folder
            shutil.rmtree(".qbrix/Update")

        if filecmp.cmp(".qbrix/qbrix_update.py", "qbrix/tools/utils/qbrix_update.py"):
            log.info("Update File unchanged")
        else:
            log.info("Update File Changed")
            log.info("Re-Running Code")
            self._run_task()

        # Add new custom tasks
        tasks_to_update = {}
        tasks_to_update.update({'qbrix_preflight': 'qbrix.tools.utils.qbrix_preflight.RunPreflight'})
        tasks_to_update.update({'qbrix_landing': 'qbrix.tools.utils.qbrix_landing.RunLanding'})
        tasks_to_update.update({'analytics_manager': 'qbrix.tools.data.qbrix_analytics.AnalyticsManager'})
        tasks_to_update.update({'user_manager': 'qbrix.salesforce.qbrix_salesforce_tasks.CreateUser'})
        self._check_and_deploy_class(tasks_to_update)

        if self.UpdateLocation:
            log.info("Running Custom Update....")
            download_and_unzip(self.UpdateLocation, self.ArchivePassword, self.IgnoreOptionalUpdates)
            log.info("Custom Update Complete")

        log.info("Q Brix Update Complete!")
