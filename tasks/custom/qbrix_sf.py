from cumulusci.tasks.sfdx import SFDXOrgTask

class ListQBrix(SFDXOrgTask):

  task_options = {
    }

  salesforce_task = True

  def _init_options(self, kwargs):
    super(ListQBrix, self)._init_options(kwargs)
    self.options["command"] = "force:data:soql:query -q 'SELECT MasterLabel,xDO_Version__c,xDO_Repository_URL__c from xDO_Base_QBrix_Register__mdt order by MasterLabel'"

