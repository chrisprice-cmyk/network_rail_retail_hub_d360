from abc import ABC
import os
import shutil

from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import update_file_api_versions, push_changes, compare_metadata, delete_standard_fields, assign_prefix_to_files, create_external_id_field

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
        [1]     Update File APIs : Updates Apex Classes and LWC/Aura Components with Q Brix API Version\n
        [2]     Delete Standard Fields : Removes standard fields within object folders\n
        [3]     Prefix Generator : Assign Prefix to all Custom Entities (Folders and References) in Project\n
        [4]     External ID Field Generator : Generate External ID Fields for a list of Object names\n
        [5]     Push Upgrade Tool (BETA) : Compare changes in metadata between the target org and your project, then push changes to the org.\n
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
        elif option.lower() == "4":
            file_input = input("\n\nPlease provide the relevent path to the txt file within the project, which holds the names of the objects. (There should be one object api name per line.) : ")
            if file_input and os.path.exists(file_input):
                create_external_id_field(file_input)
                log.info("Update Complete!")
        elif option.lower() == "5":
            target_org_alias = input("Please enter the alias of the connected org: ")
            metadata_diff = compare_metadata(target_org_alias)
            if metadata_diff:
                print("Differences found:")
                print(metadata_diff)
                if input("\nWould you like to push these changes? (Y,n)").lower() == 'y':
                    push_result = push_changes(target_org_alias)
                    print("Push result:")
                    print(push_result)
            else:
                print("No differences found")


            if os.path.exists('src'):
                shutil.rmtree('src')

            if os.path.exists('.qbrix/mdapipkg'):
                shutil.rmtree('.qbrix/mdapipkg')

            if os.path.exists('.qbrix/upgrade_src'):
                shutil.rmtree('.qbrix/upgrade_src')
        elif option.lower() == "e":
            log.info("Exiting Q Brix Mass Operations Utility")
            exit()
        else:
            log.error("Invalid Menu Option Entered. Please choose a valid option from the list above.")
            self._run_task()
