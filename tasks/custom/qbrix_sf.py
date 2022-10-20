from cumulusci.tasks.sfdx import SFDXOrgTask,SFDXJsonTask
import json

class ListQBrix(SFDXOrgTask):

  task_options = {
    }

  salesforce_task = True

  def _init_options(self, kwargs):
    super(ListQBrix, self)._init_options(kwargs)
    self.options["command"] = "force:data:soql:query -q 'SELECT MasterLabel,xDO_Version__c,xDO_Repository_URL__c from xDO_Base_QBrix_Register__mdt order by MasterLabel'"

class CheckQBrixInstalled(SFDXOrgTask):

  task_options = {
    "QBrixName": {
            "description": "Name of Q Brix",
            "required": False
        }
    }

  def _init_options(self, kwargs):
    super(CheckQBrixInstalled, self)._init_options(kwargs)
    self.options["command"] = "force:data:soql:query -q 'SELECT xDO_Repository_URL__c from xDO_Base_QBrix_Register__mdt order by MasterLabel' --json"
    self.QBrixName = None
    if "QBrixName" in self.options:
      self.QBrixName = self.options["QBrixName"]
    self.tempjson = ''
    

  def _process_output(self, line):
    if not line is None:
      self.tempjson = self.tempjson + line.decode("utf-8")   

  def _process_data(self, data):
      self.logger.info("JSON = {}".format(data))

  def _run_task(self):
    env = self._get_env()
    self._run_command(env)
    jList = json.loads(self.tempjson)
    print(jList[0])

