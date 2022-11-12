
from abc import ABC
from multiprocessing import process
from pathlib import Path
import shlex
import time
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import *

log = init_logger()


class AnalyticsManager(BaseTask, ABC):

    task_docs = """
    Q Brix Analytics Manager handles data which is contained within Analytics CRM Dataset Files. It downloads the data to csv files within the datasets/analytics folder.

    You can run the task in 3 modes by setting the 'mode' option to one of the following: \n
    Download (or d): Which Downloads and Cleans Up The Datasets \n
    Upload (or u): Which Uploads the datasets \n
    Clean (or c): Which cleans existing files \n
    """

    task_options = {
      "dataset_folder": {
        "description": "Path to folder which contains your analytics datasets. Defaults to datasets/analytics",
        "required": False
      },
      "mode": {
        "description": "Options are Download (d), Upload (u) or Clean (c)",
        "required": False
      }
    }

    def _init_options(self, kwargs):
        super(AnalyticsManager, self)._init_options(kwargs)
        self.dataset_folder = self.options["dataset_folder"] if "dataset_folder" in self.options else "datasets/analytics"
        self.mode = self.options["mode"] if "mode" in self.options else "upload"

    def run_cleaners(self):
      wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
      for wave in wave_files:
        self.cleanup_null_values(wave)
      log.info("Cleaning Completed!")

    def cleanup_null_values(self, file_location):
      log.info(f"Cleaning {file_location}... ")
      # Runs twice to allow for formatted and unformatted files. Potentially replace with regex?
      replace_file_text(file_location, f"\"defaultValue\": \"null\"", f"\"defaultValue\": \"0\"")
      replace_file_text(file_location, f"\"defaultValue\":\"null\"", f"\"defaultValue\": \"0\"")

    def download_datasets(self):

      if not os.path.exists("force-app/main/default/wave"):
        log.info("No Analytics Folder Found. Skipping Dataset Deployment.")
        return

      wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

      log.info("Starting Download of dataset files")

      if not os.path.exists(self.dataset_folder):
        log.info("Creating Dataset Directory")
        os.mkdir(self.dataset_folder)

      subprocess.run(f"sfdx config:set instanceUrl={self.org_config.instance_url}", shell=True, capture_output=True)

      for file in wave_dataset_files:
        dataset_name = Path(file).stem.replace(".wds-meta", "")
        
        with subprocess.Popen(shlex.split(f"sfdx shane:analytics:dataset:download -n {dataset_name} -t {self.dataset_folder} -u {self.org_config.access_token}"), stdout=subprocess.PIPE) as result:
          pass

        if result.returncode != 0:
          log.error(result.stderr)
        else:
          log.info(f"Dataset {dataset_name} has been downloaded to {self.dataset_folder}")

      subprocess.run("sfdx config:unset instanceUrl", shell=True, capture_output=True)

    def get_app_name(self, file_location):
      with open(file_location, 'r') as file:
        file.seek(0)
        file_data = file.read()
      
      start_pos = file_data.find("<application>") + len("<application>")
      end_pos = file_data.find("</application>")

      if start_pos > -1 and end_pos > -1:
        return file_data[start_pos:end_pos]
      else:
        return ""

    def upload_dataset_data(self):
      if not os.path.exists("force-app/main/default/wave"):
        log.info("No Source Analytics Folder Found. Skipping Dataset Deployment.")
        return

      if not os.path.exists(self.dataset_folder):
        log.info("No Analytics Datasets Folder Found. Skipping Dataset Deployment.")
        return

      self.run_cleaners()

      wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

      if len(wave_dataset_files) > 0:
        subprocess.run(f"sfdx config:set instanceUrl={self.org_config.instance_url}", shell=True, capture_output=True)

      for file in wave_dataset_files:
        dataset_name = Path(file).stem.replace(".wds-meta", "")
        data_file_location = f"{self.dataset_folder}/{dataset_name}.csv"
        app_name = self.get_app_name(file)
        shane_query = f"sfdx shane:analytics:dataset:upload -f {data_file_location} -n {dataset_name} -u {self.org_config.access_token}"

        if os.path.exists(data_file_location):

          log.info(f"Uploading {data_file_location}...")

          if app_name != "":
            log.info(f"Relating dataset to app: {app_name}")
            shane_query = f"{shane_query} -a {app_name}"

          related_json_file = f"{self.dataset_folder}/{dataset_name}.json"
          if os.path.exists(related_json_file):
            shane_query = f"{shane_query} -m {related_json_file}"

          process = subprocess.Popen(shlex.split(shane_query), stdout=subprocess.PIPE,stderr=subprocess.PIPE)

          if process.returncode != 0:
            log.error(process.stderr)
          else:
            log.info(f"Uploaded {data_file_location} successfully!")

        else:

          log.error(f"Expected to find dataset file at {data_file_location} and it was missing. Please check you have downloaded the dataset data files. Skipping this file.")

      subprocess.run("sfdx config:unset instanceUrl", shell=True, capture_output=True)

    def _run_task(self):
      
      log.info("Starting QBrix Analytics Manager")

      match self.mode.lower():
        case "upload" | "u":
          self.upload_dataset_data()
        case "download" | "d":
          self.download_datasets()
          self.run_cleaners()
        case "clean" | "c":
          self.run_cleaners()
        case _:
          log.debug("Analytics Manager was called without a valid mode.")
          exit
  

