from abc import ABC

from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import update_file_api_versions, delete_standard_fields, assign_prefix_to_files

log = init_logger()


class MassFileOps(BaseTask, ABC):

    task_docs = """
    Q Brix Mass Operations Utility has a number of helpful methods to save time when developing projects which store Salesforce metadata.
    """

    task_options = {}

    def _init_options(self, kwargs):
        super(MassFileOps, self)._init_options(kwargs)

    def _run_task(self):
        log.info(f""" 
        \nQ BRIX - MASS OPERATIONS UTILITY\n\n
        OPTION  DESCRIPTION\n
        [1]     Update File APIs - Updates Apex Classes and LWC/Aura Components with Q Brix API Version\n
        [2]     Delete Standard Fields - Removes standard fields within object folders\n
        [3]     Assign Prefix to all Custom Entities (Folders and References) in Project\n
        [e]     Exit   
    """)
        option = input("\n\nWhich task you like to run? (Enter the option number) : ")


        if option.lower() == "1":
            confirmation = input("\n\nThis will update ALL Apex Classes, Aura Component's and LWC Component's metadata files with the project API Version. Are you sure you want to continue? (y/n) Default y:") or 'y'
            if confirmation.lower() == 'y':
                update_file_api_versions(self.project_config.project__package__api_version)
                log.info("Update Complete!")
        elif option.lower() == "2":
            confirmation = input("\n\nThis will DELETE all Standard/Core Salesforce fields from all object folders within force-app/main/default/objects. Are you sure you want to continue? (y/n) Default y:") or 'y'
            if confirmation.lower() == 'y':
                delete_standard_fields()
                log.info("Update Complete!")
        elif option.lower() == "3":

            print("RUNNING MASS RENAME TOOL\nWARNING: This tool is still new so please review all changes which is makes.\nWARNING: The following Prefixes are Ignored - sdo_, xdo_, db_\nThe following directories are ignored within force-app/main/default: settings,quickActions,layouts,corswhitelistorigins,roles and standardValueSets")

            warning_input = input("\nAre you happy to proceed? (y/n) : ")

            if warning_input and warning_input.lower() == 'y':
                prefix = input("What prefix do you want to assign to custom files and folders? (e.g. FINS) : ")

                set_interactive_mode = False
                interactive_mode = input("Do you want to be prompted about any potential changes? (y/n) : ")
                if interactive_mode and interactive_mode.lower() == 'y':
                    set_interactive_mode = True
                   
                assign_prefix_to_files(prefix=prefix, interactive_mode=set_interactive_mode)

                print("REMEMBER TO CHECK CHANGES AND TEST DEPLOYMENT")

            else:
                print("Confirmation not recieved, exiting.")
                exit()

        elif option.lower() == "e":
            log.info("Exiting Q Brix Mass Operations Utility")
            exit()
        else:
            log.error("Invalid Menu Option Entered. Please choose a valid option from the list above.")
            self._run_task()
