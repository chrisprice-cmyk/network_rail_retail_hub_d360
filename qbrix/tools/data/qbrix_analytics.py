import glob
import json
import os
import subprocess
from abc import ABC
from pathlib import Path
import shlex
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger

log = init_logger()


def cleanup_null_values(file_location):

    if not str(file_location).endswith(".json"):
        log.error(f"The file provided was not a json file. File Location: {file_location}")
        return

    log.info(f"Cleaning {file_location}... ")

    with open(file_location, 'r') as f:
        data = json.load(f)

    if data is not None:
        for o in data["objects"][0]["fields"]:
            if "defaultValue" in o and "type" in o and o["type"] == "Numeric":
                o["defaultValue"] = "0" if o["defaultValue"].lower() == "null" else o["defaultValue"]

        with open(file_location, 'w') as f:
            json.dump(data, f)


def get_app_name(file_location):

    if not file_location:
        log.error("File was not passed. Skipping file")
        return None

    if not os.path.exists(file_location):
        log.error(f"The file provided doesn't exist or you do not have permissions to access it. File location: {file_location}")
        return None

    if not str(file_location).endswith(".wds-meta.xml"):
        log.debug(f"A file has been passed to an Analytics method, which is not in the expected file format (i.e. File Extension should be .wds-meta.xml). This method will continue to review the file although there may be unexpected results. Please check the file {file_location}")

    with open(file_location, 'r') as file:
        file.seek(0)
        file_data = file.read()

    start_pos = file_data.find("<application>") + len("<application>")
    end_pos = file_data.find("</application>")

    if start_pos > -1 and end_pos > -1:
        return file_data[start_pos:end_pos]
    else:
        return ""


class AnalyticsManager(BaseTask, ABC):
    task_docs = """
    Q Brix Analytics Manager handles data which is contained within Analytics CRM Dataset Files. It downloads the data to csv files within the datasets/analytics folder.

    You can run the task in 3 modes by setting the 'mode' option to one of the following: \n
    Download (or d): Which Downloads and Cleans Up The Datasets (Note: You still need to download json files when you have uploaded your initial csv, see docs for notes) \n
    Upload (or u): Which Uploads the datasets \n
    Clean (or c): Which cleans existing files \n
    """

    task_options = {
        "dataset_folder": {
            "description": "Path to folder which contains your analytics datasets. Defaults to datasets/analytics",
            "required": False
        },
        "mode": {
            "description": "(optional) Data Options are Download (d), Upload (u) or clean (c).",
            "required": False
        },
        "org": {
            "description": "(optional) Org Alias for target org when not running this task within a flow",
            "required": False
        },
        "share_to_all_internal_users": {
            "description": "(optional) If set to True, this will auto share the analytics apps to all internal users. Default False",
            "required": False
        },
        "share_to_all_portal_users": {
            "description": "(optional) If set to True, this will auto share the analytics apps to all portal/community users. Default False",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(AnalyticsManager, self)._init_options(kwargs)
        self.dataset_folder = self.options["dataset_folder"] if "dataset_folder" in self.options else "datasets/analytics"
        self.mode = self.options["mode"] if "mode" in self.options else "upload"
        self.share_to_all_internal_users = self.options["share_to_all_internal_users"] if "share_to_all_internal_users" in self.options else False
        self.share_to_all_portal_users = self.options["share_to_all_portal_users"] if "share_to_all_portal_users" in self.options else False

    def run_cleaners(self):
        wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
        for wave in wave_files:
            cleanup_null_values(wave)
        log.info("Cleaning Completed!")

    def download_datasets(self):

        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Analytics Folder Found. Skipping Dataset Download.")
            return

        wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

        log.info("Starting Download of dataset files")

        if not os.path.exists(self.dataset_folder):
            log.info("Creating Dataset Directory")
            os.mkdir(self.dataset_folder)

        subprocess.run(f"sf config set instanceUrl={self.org_config.instance_url}", shell=True, capture_output=True)

        for file in wave_dataset_files:
            dataset_name = Path(file).stem.replace(".wds-meta", "")

            with subprocess.Popen(shlex.split(
                    f"sfdx shane:analytics:dataset:download -n {dataset_name} -t {self.dataset_folder} -u {self.org_config.access_token}"),
                                  stdout=subprocess.PIPE) as result:
                pass

            if result.returncode != 0:
                log.error(result.stderr)
            else:
                log.info(f"Dataset {dataset_name} has been downloaded to {self.dataset_folder}")

        subprocess.run("sf config unset instanceUrl", shell=True, capture_output=True)

    def upload_dataset_data(self):

        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Source Analytics Folder Found at the expected location (force-app/main/default/wave). Skipping Dataset Deployment.")
            return

        if not os.path.exists(self.dataset_folder):
            log.debug(f"No Analytics Datasets Folder Found at expected location ({self.dataset_folder}). Skipping Dataset Deployment.")
            return

        self.run_cleaners()

        wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

        if len(wave_dataset_files) > 0:
            subprocess.run(f"sf config set instanceUrl={self.org_config.instance_url}", shell=True, capture_output=True)

        app_names = []

        for file in wave_dataset_files:
            dataset_name = Path(file).stem.replace(".wds-meta", "")
            data_file_location = f"{self.dataset_folder}/{dataset_name}.csv"
            app_name = get_app_name(file)
            shane_query = f"sfdx shane:analytics:dataset:upload -f {data_file_location} -n {dataset_name} -u {self.org_config.access_token}"

            if os.path.exists(data_file_location):

                log.info(f"Uploading {data_file_location}...")

                if app_name != "":
                    log.info(f"Relating dataset to app: {app_name}")
                    shane_query = f"{shane_query} -a {app_name}"
                    app_names.append(app_name)

                related_json_file = f"{self.dataset_folder}/{dataset_name}.json"
                if os.path.exists(related_json_file):
                    shane_query = f"{shane_query} -m {related_json_file}"

                process = subprocess.Popen(shlex.split(shane_query), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                output, error = process.communicate()

                if process.returncode != 0:
                    if error:
                        log.error(error.strip())
                else:
                    log.info(f"Uploaded {data_file_location} successfully!")

            else:

                log.error(
                    f"Expected to find dataset file at {data_file_location} and it was missing. Please check you have downloaded the dataset data files. Skipping this file.")

        subprocess.run("sf config unset instanceUrl", shell=True, capture_output=True)

        if self.share_to_all_portal_users or self.share_to_all_internal_users:
            self.share_app(app_names)

    def share_app(self, app_names):

        if not app_names:
            return

        extra_cmd = f"sfdx shane:analytics:app:share -u {self.org_config.access_token}"

        if self.share_to_all_portal_users or self.share_to_all_internal_users:

            # Clean Up Names of App Passed to method
            clean_list = list(dict.fromkeys(app_names))

            # Process Apps
            for app in clean_list:

                if self.share_to_all_portal_users:
                    extra_cmd += " --allcsp"

                if self.share_to_all_internal_users:
                    extra_cmd += " --org"

                log.info(f"Sharing Analytics App: {app}")
                subprocess.run(f"sf config set instanceUrl={self.org_config.instance_url}", shell=True, capture_output=True)
                subprocess.run(extra_cmd, shell=True, capture_output=True)

        subprocess.run("sf config unset instanceUrl", shell=True, capture_output=True)

    def _run_task(self):

        log.info("Starting QBrix Analytics Manager")

        if not self.mode or self.mode.lower() == "upload" or self.mode.lower() == "u":
            self.upload_dataset_data()

        if self.mode.lower() == "download" or self.mode.lower() == "d":
            self.download_datasets()
            self.run_cleaners()

        if self.mode.lower() == "clean" or self.mode.lower() == "c":
            self.run_cleaners()
