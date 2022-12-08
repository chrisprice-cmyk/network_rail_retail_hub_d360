from time import sleep
import time
import requests

from abc import ABC
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from cumulusci.core.config import ScratchOrgConfig
from qbrix.salesforce.qbrix_salesforce_tasks import salesforce_query

log = init_logger()


class RunDataTool(BaseTask, ABC):

    task_options = {
      "data_keys": {
        "description": "Data Collection Key or keys",
        "required": True
        },
      "total_timeout": {
        "description": "Total Timeout in Seconds. Defaults to 1000 seconds.",
        "required": False
      },
      "wait": {
        "description": "If defined, this is the total amount of time in seconds which the script will wait between each data load. If only one data collection is defined, this will be the wait time after the data load has completed.",
        "required": False
      }
    }

    def _init_options(self, kwargs):
      super(RunDataTool, self)._init_options(kwargs)
      self.url = "https://nxdo-data-tool.herokuapp.com/api/jobs/deployment"
      self.data_keys = self.options["data_keys"]
      self.total_timeout = int(self.options["total_timeout"]) if "total_timeout" in self.options else 8600
      self.wait = int(self.options["wait"]) if "wait" in self.options else 2

    def _run_task(self):

      log.info("NextGen Data Tool: Starting Data Load")

      if not self.data_keys:
        log.error("NextGen Data Tool: Error, there were no data collection keys were passed! Please check your task definition and add the correct data keys.")
        raise Exception("No Data Keys Passed! Data Load Failed.")

      data_load_job_counter = 1
      total_keys = len(self.data_keys)

      # Get Email from target org
      email_address = salesforce_query(f"SELECT Email From User Where Username = '{self.org_config.username}' LIMIT 1", self.org_config)
      if email_address is None or email_address == "":
        raise Exception("Unable to get email address from the target org. Stopping Data Load.")

      # Get Org Type
      IsScratchOrg = True if isinstance(self.org_config, ScratchOrgConfig) else False
      if self.org_config.is_sandbox:
        IsScratchOrg = True

      for data_key in self.data_keys:

        # Set Start Time of Job
        st = time.time()
        log.info(f"NextGen Data Tool: Processing Data Load {data_load_job_counter} of {total_keys}")

        # Check for missing Data Collection Key
        if data_key is None or data_key == "":
          log.error(f"NextGen Data Tool: Invalid or missing Data Collection ID. Skipping Job {data_load_job_counter} of {total_keys}.")
          continue

        # Start Data Load and get Job ID
        headers = {"Content-Type": "application/json; charset=utf-8"}     
        data = {
          "username": self.org_config.username,
          "email": email_address,
          "collection_version_id": f"{data_key}",
          "is_production": not IsScratchOrg
        }

        log.info(f"NextGen Data Tool: Starting Job\n\nRequesting Data Job with the following configuration:\n\nData Collection ID: {data_key}\nUsername: {self.org_config.username}\nEmail: {email_address}\nScratch Org Mode: {IsScratchOrg}\n")
        result = requests.post(self.url, json=data, headers=headers)
        jsonResponse = result.json()

        if jsonResponse is not None:
          job_id = jsonResponse["id"]
          log.info(f"NextGen Data Tool: Data Load started with ID {job_id}")
        else:
          log.error(f"NextGen Data Tool: Error the job failed to start. This could be due to network issues or issues with the NextGen Data Load host.")
          raise Exception("Data Load Job Failed to start.")

        job_status_check_url = f"{self.url}/{job_id}"
        
        # Check job for status updates
        timeout = 0
        total_retries = 0

        if self.total_timeout < 500 or self.total_timeout > 8600:
          self.total_timeout = 8600

        while True:

          # Get Job Status
          check_job = requests.get(job_status_check_url)

          # Handle issues with job status
          if check_job.json() is None:
            if total_retries > 3:
              log.error("NextGen Data Tool: Unable to lookup job status. Check your internet connection.")
              raise Exception("NextGen Data Tool Job Failed")
            else:
              total_retries += 1
              log.debug(f"NextGen Data Tool: Unable to lookup job status. Waiting 5 seconds and then retrying... retry attempt {total_retries}")
              sleep(5)
              continue

          # Handle Timeout
          if timeout > self.total_timeout:
            log.error(f"NextGen Data Tool: Error Data Load Timeout Reached (Timeout set at {self.total_timeout} seconds)")
            raise Exception("Data Load timed out. Data load failed.")

          check_job_json = check_job.json()
          status = check_job_json["state"]
          progress = check_job_json["progress"]

          if status == "completed":
            et = time.time()
            elapsed_time = et - st
            log.info(f"Job Complete! Total Time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
            break

          if status == "active":
            log.info(f"NextGen Data Tool: Job ID {job_id} still deploying... Estimated Progress - {progress}%")

          if status == "failed":
            log.error(f"The data load job has failed. Job ID: {job_id}")
            raise Exception("Data Load Failed")
          
          if status != "active" and status != "completed":
            log.error(f"NextGen Data Tool: Unsupported status ({status}) read. Stopping deployment")
            raise Exception("Data Load Failed. An unsupported status was received from the NextGen Data Tool.")

          sleep(2)
          timeout += 1
          
        data_key_number += 1
        sleep(self.wait)
          
        
