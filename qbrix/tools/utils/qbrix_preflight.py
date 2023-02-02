import os
from abc import ABC
import subprocess
import time

from cumulusci.core.tasks import BaseTask
from cumulusci.core.config import ScratchOrgConfig
from qbrix.tools.shared.qbrix_console_utils import init_logger, run_command
from qbrix.salesforce.qbrix_salesforce_tasks import QbrixInstallCheck
from qbrix.tools.shared.qbrix_cci_tasks import run_cci_task, run_cci_flow

log = init_logger()


class RunPreflight(BaseTask, ABC):
    task_docs = """
    Runs pre-flight checks and deployments for target Salesforce orgs.

    Supports information only mode where no tasks are executed. Use the command cci task run qbrix_preflight --info_mode True --org OrgAliasHere

    Support Base Config and Base Data Deployments. Set the include_base_config, base_config_only_scratch and only_base_config options accordingly
    """

    task_options = {
        "info_mode": {
            "description": "Set to True if you just want to see what tasks this will run, without running them.",
            "required": False
        },
        "include_base_config": {
            "description": "Set to True if you want the base config and data deployed into the target org. Defaults to False",
            "required": False
        },
        "base_config_only_scratch": {
            "description": "Set to True if you want the base config and data deployed into only scratch orgs. Defaults to False",
            "required": False
        },
        "only_base_config": {
            "description": "Set to True if you only want to deploy base config and NOT base data. Defaults to False",
            "required": False
        },
        "org": {
            "description": "org alias",
            "required": False
        },
        "source_dependencies": {
            "description": "[BETA] ONLY USE IN LEVEL 5 Q BRIX - Add a list of GitHub Q Brix Repo Locations which you want to check and install pre-deployment",
            "required": False
        }
    }

    salesforce_task = True

    def _init_options(self, kwargs):
        super(RunPreflight, self)._init_options(kwargs)
        self.scratch_org_mode = False
        self.include_base_config = self.options[
            "include_base_config"] if "include_base_config" in self.options else False
        self.base_config_only_scratch = self.options[
            "base_config_only_scratch"] if "base_config_only_scratch" in self.options else False
        self.info_mode = self.options["info_mode"] if "info_mode" in self.options else False
        self.only_base_config = self.options["only_base_config"] if "only_base_config" in self.options else False
        self.source_dependencies = self.options[
            "source_dependencies"] if "source_dependencies" in self.options else None

    def scratch_org_tasks(self):
        if self.include_base_config:
            self.deploy_base_config_and_data()

    def production_org_tasks(self):
        if self.include_base_config and self.base_config_only_scratch is False:
            self.deploy_base_config_and_data()

    def shared_tasks(self):

        # Deploy Settings if Present
        log.info(f"Check and Deploy Settings to Org {self.org_config.name}")
        if os.path.exists("force-app/main/default/settings"):
            log.info("Settings directory found. Deploying.")
            if not self.info_mode:

                settings_deploy_result = run_cci_task("deploy_settings", self.org_config.name, path="force-app/main/default/settings")

                if settings_deploy_result:
                    log.info("Settings Deployment Complete!")
                else:
                    log.error("Settings Deployment Failed. Check errors and warnings (if any) mentioned above.")
        else:
            log.info("No Settings Directory Found, skipping")

        # Check and Deploy Q Brix Register
        if not self.info_mode:
            log.info(f"Deploying Q Brix Registration to Org {self.org_config.name}")

            checkreg_deploy_result = run_cci_task("base:check_register", self.org_config.name)

            if checkreg_deploy_result:
                log.info("Register Check Complete!")
            else:
                log.error("Register Check Failed. Check errors and warnings (if any) mentioned above.")

        else:
            log.info(
                f"[INFO ONLY] Org with alias {self.org_config.name} would have the Q Brix Package installed if it is not already installed")

        if self.source_dependencies:
            log.error("THIS FUNCTION IS NOT SUPPORTED AT THIS TIME. PLEASE INSTALL SOURCES USING THE SORUCE_DEPENCENCIES FLOW")

        #     log.info("Checking Source Dependencies...")

        #     # Check which Q Brix need to be installed

        #     qbrix_install_dict = {}

        #     for source in list(self.source_dependencies):

        #         # Clear Invalid Sources
        #         if "/" not in source:
        #             log.error(f"{source} is not in a valid format. Please provide the URL to the GitHub repo for the source.")
        #             continue

        #         # Exclude Known Q Brix which are not supported here
        #         if source.rsplit('/', 1)[-1] in {"QBrix-0-xDO-BaseConfig", "QBrix-0-xDO-BaseData", "QBrix-1-xDO-Tool-QBrixRegister"}:
        #             log.debug(f"{source} is one of the Q Brix installed by this function. Please use the correct options to deploy it.")
        #             continue

        #         # Get Key Information for Q Brix
        #         for key, value_dict in self.project_config.sources.items():
        #             if source.lower() == dict(value_dict).get("github").lower():
        #                 qbrix_install_dict.update({key: dict(value_dict).get("github")})

        #         # if source not in qbrix_install_dict.items():
        #         #     log.error(f"The dependency you requested with name ({source.rsplit('/', 1)[-1]}) was not found in the project source list. Please add it to the source list or remove it from the task > source_dependencies option to remove this error. Moving onto the next dependency (if any)")
        #         #     continue

        #     # Install (if required) each Q Brix
        #     for qbrix_source_name, qbrix_repo in qbrix_install_dict.items():

        #         repo_qbrix_name = qbrix_repo.rsplit('/', 1)[-1]

        #         log.info(f"Checking if {repo_qbrix_name} is already installed in Salesforce org with alias ({self.org_config.name})...")
        #         if not QbrixInstallCheck(repo_qbrix_name, self.org_config):
        #             # log.info(f"Installing {repo_qbrix_name}")

        #             pass

        #             # project_folder = os.getcwd()

        #             # proc = subprocess.Popen(f"cd {project_folder} && cci flow run {qbrix_source_name}:deploy_qbrix --org {self.org_config.name}",
        #             #         shell=True,
        #             #         cwd=project_folder
        #             #     )

        #             # while proc.poll() is None:
        #             #     print(f"{repo_qbrix_name} is still deploying...")
        #             #     time.sleep(1)

        #             # output, error = proc.communicate()

        #             # print(output)

        #             # if error:
        #             #     log.error(error.decode("utf-8"))
        #         else:
        #             log.info(f"{repo_qbrix_name} is already installed in Salesforce org with alias ({self.org_config.name}). Moving onto the next dependency (if any).")
        #             continue
        # else:
        #     log.info("No source dependencies defined for pre-install. Skipping Task")

    def deploy_base_config_and_data(self):

        log.info("Checking and loading Q Brix Base Config and Data")

        if not QbrixInstallCheck("QBrix-0-xDO-BaseConfig", self.org_config):
            if not self.info_mode:
                log.info("Installing Q Brix Base Config")
                deploy_result = run_cci_flow(f"base:deploy_qbrix", self.org_config.name)

                if deploy_result:
                    log.info(f"Q Brix Base Config Deployment Complete!")
                else:
                    log.error(f"Q Brix Base Config Deployment Failed. Check errors and warnings (if any) mentioned above.")
            else:
                log.info(
                    f"[INFO ONLY] Org with alias {self.org_config.name} would have the Q Brix Base Config installed if it is not already installed")

        if not self.only_base_config:
            if not QbrixInstallCheck("QBrix-0-xDO-BaseData", self.org_config):
                if not self.info_mode:
                    log.info("Installing Q Brix Base Data")
                    deploy_result = run_cci_flow(f"base:deploy_qbrix_base_data", self.org_config.name)

                    if deploy_result:
                        log.info(f"Q Brix Base Data Deployment Complete!")
                    else:
                        log.error(f"Q Brix Base Data Deployment Failed. Check errors and warnings (if any) mentioned above.")
                else:
                    log.info(
                        f"[INFO ONLY] Org with alias {self.org_config.name} would have the Q Brix Base Data installed if it is not already installed")

    def _run_task(self):

        log.info("Starting QBrix Preflight Check")

        if self.info_mode:
            log.info("*** RUNNING AS INFORMATION MODE - NO TASKS WILL ACTUALLY BE RUN ***")

        self.scratch_org_mode = True if isinstance(self.org_config, ScratchOrgConfig) else False
        if self.scratch_org_mode:
            log.info("Running in Scratch Org Mode")
            self.scratch_org_tasks()
        else:
            log.info("Running in Production Org Mode")
            self.production_org_tasks()

        self.shared_tasks()

        log.info("Preflight Complete")
