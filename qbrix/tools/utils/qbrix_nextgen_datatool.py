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
      }
    }

    def _init_options(self, kwargs):
      super(RunDataTool, self)._init_options(kwargs)
      self.url = "https://nxdo-data-tool.herokuapp.com/api/jobs/deployment"
      self.data_keys = self.options["data_keys"]
      self.total_timeout = int(self.options["total_timeout"]) if "total_timeout" in self.options else 1000

    def _run_task(self):

      for data_key in self.data_keys:

        if data_key is None or data_key == "":
          log.debug(f"In valid Data Collection ID Passed. Skipping Data Collection ID: {data_key}")
          continue

        st = time.time()

        email_address = salesforce_query(f"SELECT Email From User Where Username = '{self.org_config.username}' LIMIT 1", self.org_config)

        if email_address is None:
          exit

        IsScratchOrg = True if isinstance(self.org_config, ScratchOrgConfig) else False

        if self.org_config.is_sandbox:
          IsScratchOrg = True

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
          log.info(f"NextGen Data Tool: Job ID: {job_id} Started")
        else:
          log.error(f"NextGen Data Tool: Error Job failed to start.")
          exit

        
        job_status_check_url = f"https://nxdo-data-tool.herokuapp.com/api/jobs/deployment/{job_id}"
        
        timeout = 0

        if self.total_timeout < 500 or self.total_timeout > 8600:
          self.total_timeout = 1000

        while True:
          check_job = requests.get(job_status_check_url)

          if check_job.json() is None:
            log.error("NextGen Data Tool: Unable to lookup job status. Check your internet connection.")
            exit

          if timeout > self.total_timeout:
            log.error("NextGen Data Tool: Error Data Load Timeout Reached")
            exit

          check_job_json = check_job.json()
          status = check_job_json["state"]
          progress = check_job_json["progress"]

          if status == "completed":
            break

          if status == "active":
            log.info(f"NextGen Data Tool: Job ID {job_id} still deploying...")
          
          if status != "active" and status != "completed":
            log.debug(f"NextGen Data Tool: Unsupported status ({status}) read. Stopping deployment")
            exit

          sleep(2)
          timeout += 1

          
        et = time.time()
        elapsed_time = et - st
        log.info(f"Job Complete! Total Time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
