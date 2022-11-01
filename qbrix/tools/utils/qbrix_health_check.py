from abc import ABC
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import *
from qbrix.tools.shared.qbrix_project_tasks import clean_project_files, check_api_versions

log = init_logger()

from cumulusci.core.tasks import BaseTask


class HealthChecker(BaseTask, ABC):
    task_options = {
        "RunAllChecks": {
            "description": "Boolean, which when set to true runs all checks automatically.",
            "required": False
        },
        "SkipCacheRebuild": {
            "description": "Boolean, Skips the cci cache rebuild if true. Normally used for testing.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(HealthChecker, self)._init_options(kwargs)
        self.RunAllChecks = self.options["RunAllChecks"] if "RunAllChecks" in self.options else False
        self.SkipCacheRebuild = self.options["SkipCacheRebuild"] if "SkipCacheRebuild" in self.options else False

    def _run_task(self):
        log.info("Health Check: Starting Health Checker Tool")

        log.info("Health Check: Removing cached/unneeded files and folders from project.")
        clean_project_files()
        log.info("Health Check: Removed cached/unneeded files and folders from project.")

        log.info("Health Check: Checking for old class references and updating them...")
        check_and_update_old_class_refs()
        log.info("Health Check: Old References checks complete.")

        log.info("Health Check: Checking placeholder names have been replaced and other naming is correct.")
        self.check_project_file_naming()

        log.info("Health Check: Checking that all references to the API version, match the project version.")
        check_api_versions(self.project_config.project__package__api_version)

        log.info("Health Check: Checking that orgs/dev.json has all features from all sources related to this Q Brix.")
        source_org_feature_checker(False)

        log.info("Health Check: Checking that dev_preview has all features from dev.")
        org_feature_checker()

        log.info("Health Check: Checking that scratch org files are configured with required settings")
        check_org_config_files(True)

        log.info("Checking .gitignore file")
        test_list = []
        test_list.append(".sf/")
        test_list.append(".qbrix/")
        test_list.append("testim-headless.zip")
        test_list.append("src/")
        test_list.append(".cci/")
        test_list.append(".sfdx/")
        test_list.append("browser/")
        test_list.append("playwright-log.txt")
        test_list.append("log.html")
        test_list.append("output.xml")
        test_list.append("report.html")
        test_list.append(".qbrix/*")
        test_list.append("qbrix/robot/__pycache__")
        test_list.append("qbrix/salesforce/__pycache__")
        test_list.append("qbrix/tools/utils/__pycache__")
        test_list.append("qbrix/tools/shared/__pycache__")
        test_list.append("qbrix/tools/data/__pycache__")
        test_list.append("qbrix/tools/testing/__pycache__")
        test_list.append("tasks/custom/__pycache__")
        upsert_gitignore_entries(test_list)

        replace_file_text(".gitignore", "#.vscode", ".vscode")

        log.info("Health Check: All Checks completed.")

    def check_project_file_naming(self):

        """ Checks that the project file names are set correctly """

        repo_url = get_qbrix_repo_url()
        if repo_url is not None:
            repo_qbrix_name = repo_url.rsplit('/', 1)[-1]
        else:
            repo_qbrix_name = self.project_config.project__git__repo_url.rsplit('/', 1)[-1]

        project_name = self.project_config.project__name
        package_name = self.project_config.project__package__name
        repo_url = self.project_config.project__git__repo_url

        log.info("Naming Check: Checking File and Project Naming aligns with correct Q Brix Name")
        file_name_error = False

        if project_name is None or package_name is None or repo_url is None:
            file_name_error = True
            log.error(
                "Naming Check: [FAIL] One or more of the required parameters are missing from the cumulusci.yml file. Check that the Project name, Project Package Name and Repo URL have all been added and populated.")
            log.info(
                f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

        else:

            # Check Repo Name has been found
            if repo_qbrix_name is None:
                file_name_error = True
                log.error(
                    "Naming Check: [FAIL] Check you have a valid URL for the project > Repo Url in the cumulusci.yml file")
                log.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check for the Template name in the config file.
            if 'xDO-Template' in project_name or 'xDO-Template' in package_name or 'xDO-Template' in repo_url:
                file_name_error = True
                log.error(
                    "Naming Check: [FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url. xDO-Template was found and this should have been updated, see Readme.")
                log.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check that the repo name and project names all match
            if not project_name == package_name == repo_qbrix_name:
                file_name_error = True
                log.error(
                    "Naming Check: [FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url")
                log.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check that the dev.json file has the correct qbrix name
            if repo_qbrix_name not in get_json_file_value("orgs/dev.json", "orgName"):
                log.debug("Naming Check: Updating OrgName in orgs/dev.json has not been updated. Updating now...")
                update_json_file_value("orgs/dev.json", "orgName", f"{repo_qbrix_name} - Dev org")
                log.info("Naming Check: Updated orgs/dev.json")

            # Check that the dev_preview.json file has the correct qbrix name
            if repo_qbrix_name not in get_json_file_value("orgs/dev_preview.json", "orgName"):
                log.debug(
                    "Naming Check: Updating OrgName in orgs/dev_preview.json has not been updated. Updating Now...")
                update_json_file_value("orgs/dev_preview.json", "orgName", f"{repo_qbrix_name} - Preview Dev org")
                log.debug(
                    "Naming Check: Updated orgs/dev_preview.json")

        if not file_name_error:
            log.info("Health Check: [OK] All naming Checks Passed!")
        else:
            log.info(
                "Health Check: [ACTION NEEDED] Some tests did not pass. Check the error messages above for more information.")

        log.info("Health Check: Naming Checks completed")
