from abc import ABC
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_project_tasks import download_and_unzip


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

    def _run_task(self):

        """" Downloads the update package from AWS S3 and applies updates """

        download_and_unzip(self.UpdateLocation, self.ArchivePassword, self.IgnoreOptionalUpdates)
