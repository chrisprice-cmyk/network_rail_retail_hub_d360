import json
import os
from abc import ABC

import requests
from cumulusci.core.exceptions import CommandException
from cumulusci.core.keychain import BaseProjectKeychain
from cumulusci.core.tasks import BaseTask
from cumulusci.core.config import ScratchOrgConfig
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.salesforce.qbrix_salesforce_tasks import QbrixInstallCheck
from qbrix.tools.shared.qbrix_cci_tasks import run_cci_task, run_cci_flow
from qbrix.tools.shared.qbrix_project_tasks import run_command

log = init_logger()


class RunPreflight(BaseTask, ABC):
    task_docs = """
    Q Brix Preflight runs multiple tasks and flows against your target org to prepare it for the main deployment. By default it deploys settings and ensures that the Q Brix Registration package is installed.
    """

    task_options = {
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
        "skip_settings_deployment": {
            "description": "Set to True if you don't want preflight to deploy settings. Defaults to False",
            "required": False
        },
        "skip_hydrate": {
            "description": "Set to True if you don't want preflight to hydrate options for where clauses. Defaults to False",
            "required": False
        },
        "org": {
            "description": "The alias for the connected target org within the CumulusCI Project. Ensure that either this is provided or the access token.",
            "required": False
        },
        "accesstoken": {
            "description": "[Optional] Access Token for the target org, if known.",
            "required": False
        },
        "instanceurl": {
            "description": "[Optional] The Salesforce Instance URL for the target org.",
            "required": False
        }
    }

    salesforce_task = True
    keychain_class = BaseProjectKeychain

    def _init_options(self, kwargs):
        super(RunPreflight, self)._init_options(kwargs)

        try:
            # Initiate Shared Variables
            self.scratch_org_mode = True if isinstance(self.org_config, ScratchOrgConfig) else False
            self.targetusername = ""
            self.accesstoken = self.options["accesstoken"] if "accesstoken" in self.options else self.org_config.access_token
            self.instanceurl = self.options["instanceurl"] if "instanceurl" in self.options else self.org_config.instance_url

            # Initiate Options
            self.include_base_config = self.options["include_base_config"] if "include_base_config" in self.options else False
            self.base_config_only_scratch = self.options["base_config_only_scratch"] if "base_config_only_scratch" in self.options else False
            self.info_mode = self.options["info_mode"] if "info_mode" in self.options else False
            self.only_base_config = self.options["only_base_config"] if "only_base_config" in self.options else False
            self.skip_settings_deployment = self.options["skip_settings_deployment"] if "skip_settings_deployment" in self.options else False
            self.skip_hydrate = self.options["skip_hydrate"] if "skip_hydrate" in self.options else False
        except:
            print('Error on Preflight')

    def deploy_settings(self):
        # Deploy Settings if Present
        if os.path.exists("force-app/main/default/settings") and not self.skip_settings_deployment:
            log.info("PREFLIGHT: Settings directory found. Starting Deployment...")
            run_command(f"cci task run deploy --path force-app/main/default/settings --org {self.org_config.name}")
        else:
            log.info("PREFLIGHT: Skipping Settings Deployment.")

    def deploy_qbrix_register(self):
        log.info(f"PREFLIGHT: Deploying Q Brix Registration to Org {self.org_config.name}")
        checkreg_deploy_result = run_cci_task("base:check_register", self.org_config.name)
        if checkreg_deploy_result:
            log.info("PREFLIGHT: Register Check Complete!")
        else:
            log.error("PREFLIGHT: Register Check Failed. Check errors and warnings (if any) mentioned above.")

    def deploy_base_config_and_data(self):
        log.info("Checking and loading Q Brix Base Config and Data")

        if not QbrixInstallCheck("QBrix-0-xDO-BaseConfig", self.org_config):
            log.info("Installing Q Brix Base Config")
            deploy_result = run_cci_flow(f"base:deploy_qbrix", self.org_config.name)

            if deploy_result:
                log.info(f"Q Brix Base Config Deployment Complete!")
            else:
                log.error(f"Q Brix Base Config Deployment Failed. Check errors and warnings (if any) mentioned above.")
        else:
            log.info("Q Brix Base Config Deployed")

        if not self.only_base_config:
            if not QbrixInstallCheck("QBrix-0-xDO-BaseData", self.org_config):
                log.info("Installing Q Brix Base Data")
                deploy_result = run_cci_flow(f"base:deploy_qbrix_base_data", self.org_config.name)

                if deploy_result:
                    log.info(f"Q Brix Base Data Deployment Complete!")
                else:
                    log.error(f"Q Brix Base Data Deployment Failed. Check errors and warnings (if any) mentioned above.")
            else:
                log.info("Q Brix Base Data Deployed")

    def _get_org_max_api_version(self):
        url = f"{self.instanceurl}/services/data/"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        #self.logger.info(response.text)
        return float(data[-1]['version'])

    def _is_qbrix_installed(self, qbrixname):
        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+MasterLabel+from+xDO_Base_QBrix_Register__mdt+where+MasterLabel='{qbrixname}'"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1

    def _is_package_namespace_installed(self, namespace):
        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+NamespacePrefix+from+PackageLicense+where+NamespacePrefix='{namespace}'"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1

    def _is_object_present_in_org(self, targetobject):
        # SELECT  QualifiedApiName FROM EntityDefinition Where QualifiedApiName=

        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+QualifiedApiName+from+EntityDefinition+where+QualifiedApiName='{targetobject}' LIMIT 1"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1

    def _is_psl_present_in_org(self, psl):
        # e.g.
        # SELECT  id,MasterLabel,DeveloperName from PermissionSetLicense where (Masterlabel='OmniStudioDesigner' or DeveloperName='OmniStudioDesigner')

        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+Id+from+PermissionSetLicense+where(Masterlabel='{psl}' or DeveloperName='{psl}') LIMIT 1"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1

    def _prepruntime(self):

        if self.scratch_org_mode:
            self.targetusername = self.org_config.username
        else:
            self.targetusername = self.org_config.access_token

        if not self.org_config.max_org_api_version:
            self.org_config.max_org_api_version = self._get_org_max_api_version()

        if not self.org_config.is_qbrix_installed:
            self.org_config.is_qbrix_installed = self._is_qbrix_installed

        if not self.org_config.is_object_in_org:
            self.org_config.is_object_in_org = self._is_object_present_in_org

        if not self.org_config.is_psl_in_org:
            self.org_config.is_psl_in_org = self._is_psl_present_in_org

        if not self.org_config.is_namespace_installed:
            self.org_config.is_namespace_installed = self._is_package_namespace_installed

    def _handle_returncode(self, returncode, stderr):
        if returncode:
            message = "Return code: {}".format(returncode)
            if stderr:
                message += "\nstderr: {}".format(stderr.read().decode("utf-8"))
            self.logger.error(message)
            raise CommandException(message)

    def scratch_org_tasks(self):
        if self.include_base_config:
            self.deploy_base_config_and_data()

    def production_org_tasks(self):
        if self.include_base_config and self.base_config_only_scratch is False:
            self.deploy_base_config_and_data()

    def shared_tasks(self):
        # Deploy Settings
        if not self.skip_settings_deployment:
            self.deploy_settings()

        # Check and deploy Q Brix Register
        self.deploy_qbrix_register()

    def _run_task(self):
        log.info("PREFLIGHT: Starting Q Brix Preflight Check")

        log.info("PREFLIGHT: Running Shared Tasks")
        if not self.skip_hydrate:
            self._prepruntime()
        self.shared_tasks()

        if self.scratch_org_mode:
            log.info("PREFLIGHT: Running Scratch Org and Sandbox Related Tasks")
            self.scratch_org_tasks()
        else:
            log.info("PREFLIGHT: Running Production Org Related Tasks")
            self.production_org_tasks()

        log.info("PREFLIGHT: Preflight Complete")
