import json
import subprocess
from abc import ABC
from typing import Optional

import click
from cumulusci.core.config import ScratchOrgConfig
from cumulusci.core.dependencies.dependencies import PackageVersionIdDependency, PackageNamespaceVersionDependency, \
    BaseGitHubDependency, UnmanagedGitHubRefDependency
from cumulusci.core.dependencies.resolvers import dependency_filter_ignore_deps, get_static_dependencies
from cumulusci.core.exceptions import CumulusCIException
from cumulusci.tasks.salesforce.update_dependencies import UpdateDependencies
from cumulusci.tasks.sfdx import SFDXOrgTask
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger

log = init_logger()


def salesforce_query(soql, org_config):
    if soql != "" and org_config is not None:

        dx_command = f"sfdx force:data:soql:query -q \"{soql}\" --json "

        subprocess.run(f"sfdx config:set instanceUrl={org_config.instance_url}", shell=True, capture_output=True)

        if isinstance(org_config, ScratchOrgConfig):
            dx_command += " -u {username}".format(username=org_config.username)
        else:
            dx_command += " -u {username}".format(username=org_config.access_token)

        result = subprocess.run(dx_command, shell=True, capture_output=True)
        subprocess.run("sfdx config:unset instanceUrl", shell=True, capture_output=True)

        if result.returncode > 0:
            log.error(f"Salesforce Query Error - Details: {result.stderr}")
            return None

        json_result = json.loads(result.stdout)

        if json_result["result"]["totalSize"] >= 1:
            return json_result["result"]["records"][0][list(json_result["result"]["records"][0].keys())[1]]
        else:
            return None


def QbrixInstallCheck(qbrix_name, org_config):
    log.info(f"Checking for Qbrix: {qbrix_name}")
    subprocess.run(f"sfdx config:set instanceUrl={org_config.instance_url}", shell=True, capture_output=True)

    dx_soql = f"SELECT Id from xDO_Base_QBrix_Register__mdt WHERE xDO_Repository_URL__c LIKE '%{qbrix_name}%'"
    dx_command = f"sfdx force:data:soql:query -q \"{dx_soql}\" --json "

    if isinstance(org_config, ScratchOrgConfig):
        dx_command += " -u {username}".format(username=org_config.username)
    else:
        dx_command += " -u {username}".format(username=org_config.access_token)

    result = subprocess.run(dx_command, shell=True, capture_output=True)
    subprocess.run("sfdx config:unset instanceUrl", shell=True, capture_output=True)

    if result is None:
        log.error("Nothing was returned. Check that the org still exists and that you can login via cci.")
        return False

    json_result = json.loads(result.stdout)

    if 'result' not in json_result or len(json_result['result']) == 0:
        log.info("No Q Brix installed")
        return False

    if json_result["result"]["totalSize"] >= 1:
        log.info(f"{qbrix_name} is installed.")
        return True
    else:
        log.info(f"{qbrix_name} is NOT installed.")
        return False


class ListQBrix(SFDXOrgTask, ABC):
    task_options = {
    }

    salesforce_task = True

    def _init_options(self, kwargs):
        super(ListQBrix, self)._init_options(kwargs)
        self.options[
            "command"] = "force:data:soql:query -q 'SELECT MasterLabel,xDO_Version__c,xDO_Repository_URL__c from " \
                         "xDO_Base_QBrix_Register__mdt order by MasterLabel' "


class QBrixInstalled(BaseTask, ABC):
    task_options = {
        "qbrix_name": {
            "description": "Name of the Q Brix, starting with Qbrix-",
            "required": True
        }
    }

    salesforce_task = True

    def _init_options(self, kwargs):
        super(QBrixInstalled, self)._init_options(kwargs)
        self.qbrix_name = self.options["qbrix_name"]

    def _run_task(self):
        self.return_value = QbrixInstallCheck(self.qbrix_name, self.org_config)


class QUpdateDependencies(UpdateDependencies, ABC):

    def _init_options(self, kwargs):
        super(QUpdateDependencies, self)._init_options(kwargs)

    def _run_task(self):
        if not self.dependencies:
            self.logger.info("Project has no dependencies, doing nothing")
            return

        log.info("Resolving dependencies...")
        if "ignore_dependencies" in self.options:
            filter_function = dependency_filter_ignore_deps(
                self.options["ignore_dependencies"]
            )
        else:
            filter_function = None

        dependencies = self._filter_dependencies(
            get_static_dependencies(
                self.project_config,
                dependencies=self.dependencies,
                strategies=self.resolution_strategy,
                filter_function=filter_function,
            )
        )
        log.info("Collected dependencies:")

        for d in dependencies:
            if isinstance(d, PackageVersionIdDependency):
                desc = self.options["base_package_url_format"].format(d.version_id)
            elif isinstance(d, PackageNamespaceVersionDependency):
                if d.version_id:
                    desc = self.options["base_package_url_format"].format(d.version_id)
                else:
                    desc = ""
            elif isinstance(d, UnmanagedGitHubRefDependency):
                if "qbrix" in d.github.lower():
                    desc = "Q Brix"
                else:
                    desc = ""
            else:
                desc = "unpackaged"

            desc = f" ({desc})" if desc else desc
            self.logger.info(f"    {d}{desc}")

        if self.options["interactive"]:
            if not click.confirm("Continue to install dependencies?", default=True):
                raise CumulusCIException("Dependency installation was canceled.")

        for d in dependencies:
            if isinstance(d, UnmanagedGitHubRefDependency):
                if "qbrix" in d.github.lower():
                    uqbrix_name = d.github.rsplit('/', 1)[-1]
                    if QbrixInstallCheck(uqbrix_name, self.org_config):
                        continue
            self._install_dependency(d)

        self.org_config.reset_installed_packages()
