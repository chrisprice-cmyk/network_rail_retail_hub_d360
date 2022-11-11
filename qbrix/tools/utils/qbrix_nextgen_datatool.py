import requests

from abc import ABC
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger

log = init_logger()


class RunDataTool(BaseTask, ABC):
    task_options = {
      "DataKey": {
            "description": "Data Collection Key",
            "required": True
        }
    }

    def _init_options(self, kwargs):
      super(RunDataTool, self)._init_options(kwargs)
      self.url = "https://nxdo-data-tool.herokuapp.com/api/jobs/deployment"

    def _run_task(self):

      headers = {"Content-Type": "application/json; charset=utf-8"}

      data = {
        "username": "stewartanderson@stewartanderson-221107-810.demo",
        "email": "stewart.anderson@salesforce.com",
        "collection_version_id": "3cbc53bc-796c-481d-800c-bad0885686c5"
      }

      result = requests.post(self.url, json = data, headers=headers)

      print(result)
