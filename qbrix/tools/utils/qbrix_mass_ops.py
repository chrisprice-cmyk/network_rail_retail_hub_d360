from abc import ABC

from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import *

log = init_logger()


class MassFileOps(BaseTask, ABC):
    task_options = {}

    def _init_options(self, kwargs):
        super(MassFileOps, self)._init_options(kwargs)

    def _run_task(self):
        log.info(f''' 
    Q BRIX - MASS OPERATION UTILITIES\n\n
      OPTION  DESCRIPTION\n
      [1]     Update File APIs - Updates Apex Classes and LWC/Aura Components with Q Brix API Version\n
      [2]     Delete Standard Fields - Removes standard fields within object folders\n
      [e]     Exit   
    ''')
        option = input("\n\nWhich task you like to run? (Enter the option number) : ")
        match option.lower():
            case "1":
                confirmation = input("\n\nThis will update ALL Apex Classes, Aura Component's and LWC Component's metadata files with the project API Version. Are you sure you want to continue? (y/n) Default y:") or 'y'
                if confirmation.lower() == 'y':
                    update_file_api_versions(self.project_config.project__package__api_version)
                    log.info("Update Complete!")
            case "2":
                confirmation = input("\n\nThis will DELETE all Standard/Core Salesforce fields from all object folders within force-app/main/default/objects. Are you sure you want to continue? (y/n) Default y:") or 'y'
                if confirmation.lower() == 'y':
                    delete_standard_fields()
                    log.info("Update Complete!")
            case "e":
                log.info("Exiting Mass Operations Utilities")
                exit()
            case _:
                log.error("Invalid Menu Option Selected. Please choose a valid option from the list above.")
        self._run_task()
