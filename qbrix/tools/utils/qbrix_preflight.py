from abc import ABC
from cumulusci.core.tasks import BaseTask
from cumulusci.core.config import ScratchOrgConfig
from qbrix.tools.shared.qbrix_console_utils import init_logger, run_command
from qbrix.tools.shared.qbrix_project_tasks import *
from qbrix.salesforce.qbrix_salesforce_tasks import *

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
            "description": "Add a list of GitHub Q Brix Repo Locations which you want to check and install pre-deployment",
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
                result = run_command(command=f"cci task run deploy_settings --org {self.org_config.name}",
                                     cwd=os.getcwd())
                if result == 0:
                    log.info("Settings Checked and Deployed")
                else:
                    log.error(f"Settings deployment has failed with error detail: {result}")
                    raise Exception(f"{result}")
        else:
            log.info("No Settings Directory Found, skipping")

        # Check and Deploy Q Brix Register
        if not self.info_mode:
            log.info(f"Deploying Q Brix Registration to Org {self.org_config.name}")
            result = run_command(command=f"cci task run base:check_register --org {self.org_config.name}",
                                 cwd=os.getcwd())
            if result == 0:
                log.info("Q Brix Register Checked and Deployed")
            else:
                log.error(f"Q Brix Register has failed with return code: {result}")
                raise Exception(f"{result}")
        else:
            log.info(
                f"[INFO ONLY] Org with alias {self.org_config.name} would have the Q Brix Package installed if it is not already installed")

        if self.source_dependencies:

            log.info("Checking Sources")

            for source in list(self.source_dependencies):

                log.info(f"Checking {source} is pre-installed in org.")
                source_found = False

                for key, value_dict in self.project_config.sources.items():

                    if source in dict(value_dict).get("github"):
                        repo_qbrix_name = source.rsplit('/', 1)[-1]
                        source_found = True

                        if repo_qbrix_name == "QBrix-0-xDO-BaseConfig" or repo_qbrix_name == "QBrix-0-xDO-BaseData":
                            log.debug(
                                "Skipping Base Config and Base Data Repos, these should be handled with the options on this task instead.")
                            continue

                        if not QbrixInstallCheck(repo_qbrix_name, self.org_config):
                            if not self.info_mode:
                                log.info(f"Installing {repo_qbrix_name}")
                                result = run_command(
                                    command=f"cci flow run {key}:deploy_qbrix --org {self.org_config.name}",
                                    cwd=os.getcwd())
                                if result == 0:
                                    log.info(f"{repo_qbrix_name} Checked and Deployed")
                                else:
                                    log.error(f"{repo_qbrix_name} has failed to install.")
                                    raise Exception(f"{repo_qbrix_name} has failed to install.")
                            else:
                                log.info(
                                    f"[INFO ONLY] Org with alias {self.org_config.name} would have the {repo_qbrix_name} installed if it is not already installed, using command {key}:deploy_qbrix --org {self.org_config.name}")

                if not source_found:
                    log.error(
                        f"You have requested a source Q Brix is pre-installed, although it is not present in your project sources. Please add {source} to your project sources in the cumulusci.yml file and try again.")
                    continue
        else:
            log.info("No sources defined for pre-install. Skipping")

    def deploy_base_config_and_data(self):

        log.info("Checking and loading Q Brix Base Config and Data")

        if not QbrixInstallCheck("QBrix-0-xDO-BaseConfig", self.org_config):
            if not self.info_mode:
                log.info("Installing Q Brix Base Config")
                result = run_command(command=f"cci flow run base:deploy_qbrix --org {self.org_config.name}", cwd=os.getcwd())
                if result == 0:
                    log.info("Q Brix Base Config Checked and Deployed")
                else:
                    log.error(f"Q Brix Base Config has failed with return code: {result}")
                    raise Exception(f"{result}")
            else:
                log.info(
                    f"[INFO ONLY] Org with alias {self.org_config.name} would have the Q Brix Base Config installed if it is not already installed")

        if not self.only_base_config:
            if not QbrixInstallCheck("QBrix-0-xDO-BaseData", self.org_config):
                if not self.info_mode:
                    log.info("Installing Q Brix Base Data")
                    result = run_command(command=f"cci flow run base:deploy_qbrix_base_data --org {self.org_config.name}", cwd=os.getcwd())
                    if result == 0:
                        log.info("Q Brix Base Data Checked and Deployed")
                    else:
                        log.error(f"Q Brix Base Data has failed with return code: {result}")
                        raise Exception(f"{result}")
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
