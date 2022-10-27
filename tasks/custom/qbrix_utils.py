import glob
import json
import os
import shutil
import subprocess
from abc import ABC
from datetime import datetime
from io import BytesIO
from os.path import exists
from urllib.request import urlopen
from zipfile import ZipFile

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

    def check_and_delete_dir(self, dir_path):

        """ Deletes a folder (and all contents) if it exists. Returns True if folder has been deleted. """

        if dir_path is None or dir_path == "":
            return
        if exists(dir_path):
            self.logger.info(f"Removing {dir_path}")
            try:
                shutil.rmtree(f"{dir_path}")
                return True
            except:
                self.logger.info(f"[ERROR] Unable to remove folder: {dir_path}")
                return False

    def check_and_delete_file(self, file_path):

        """ Deletes a File if it exists. Returns True if File has been removed. """

        if file_path is None or file_path == "":
            return False
        if exists(file_path):
            self.logger.info(f"Removing file: {file_path}")
            try:
                os.remove(f"{file_path}")
                return True
            except:
                self.logger.info(f"[ERROR] Unable to remove file: {file_path}")
                return False

    def get_json_file_value(self, file_location, key_name):

        """ Reads a value from a json file based on key name. Returns None if nothing is found or error. """

        if file_location is None or not exists(file_location):
            self.logger.info(f"[ERROR] {file_location} not found.")
            return None
        else:
            try:
                with open(file_location) as json_file:
                    json_file_data = json.load(json_file)
                return json_file_data[key_name]
            except:
                return None

    def update_json_file_value(self, file_location, key_name, new_value):

        """ Updates a scratch org json file key value with a new value. Not designed to be used with a list """

        if file_location is None or not exists(file_location):
            return

        self.logger.info(f"Updating {file_location}, setting key {key_name} to a new value of {new_value}")

        try:
            with open(file_location) as json_file:
                json_file_data = json.load(json_file)

            json_file_data[key_name] = new_value

            with open(file_location, "w") as updated_json_file:
                json.dump(json_file_data, updated_json_file, indent=2)

            self.logger.info(f"{file_location} has been updated!")
        except:
            self.logger.info(f"[ERROR] {file_location} update failed!")

    def remove_json_entry(self, file_location, key_name):

        if key_name is None:
            raise Exception("Error: Missing Key Name for JSON File Update. Please check you are passing a key name.")

        with open(file_location) as mFile:
            mObject = json.load(mFile)
            mFile.close()

        del mObject[key_name]

        with open(file_location, "w") as nFile:
            json.dump(mObject, nFile, indent=2)
            nFile.close()

    def clean_project(self):

        """ Removes Cached files and folders from q brix project """

        self.check_and_delete_dir(".cci/projects")
        self.check_and_delete_dir("src")
        self.check_and_delete_dir("browser")
        self.check_and_delete_file("log.html")
        self.check_and_delete_file("playwright-log.txt")
        self.check_and_delete_file("output.xml")
        self.check_and_delete_file("report.html")

    def update_org_file_features(self, file_location, missing_features):

        """ Update scratch org json file features with additional features. Expects a file location and a list of
        missing features. Returns False on issue otherwise returns True """

        if not exists(file_location) or missing_features is None:
            raise Exception("[ERROR] File Location was not found or feature list was empty.")

        if not self.RunAllChecks:
            get_response = input(
                f"Would you like to append these missing features to your {file_location} file? (y/n) Default y: ") \
                           or 'y'
        else:
            get_response = 'y'

        if get_response == 'y':
            self.logger.info(f"Updating: {file_location}")

            try:
                with open(file_location) as json_file:
                    json_file_data = json.load(json_file)

                # Get Existing Feature List
                current_features = json_file_data['features']
                current_features = [x.lower() for x in current_features]

                # De-Duplicate Feature Lists and Append to Clean List
                clean_feature_list = []
                for current_feature in current_features:
                    if (":" not in current_feature and not current_feature.lower() in clean_feature_list) or (
                            ":" in current_feature and not self.advancedfeaturematch(current_feature.lower(),
                                                                                     clean_feature_list)):
                        clean_feature_list.append(current_feature.lower())

                for missing_feature in missing_features:
                    if (":" not in missing_feature and not missing_feature.lower() in clean_feature_list) or (
                            ":" in missing_feature and not self.advancedfeaturematch(missing_feature.lower(),
                                                                                     clean_feature_list)):
                        clean_feature_list.append(missing_feature.lower())

                clean_feature_list.sort()

                # Update File
                json_file_data['features'] = clean_feature_list
                with open(file_location, "w") as nFile:
                    json.dump(json_file_data, nFile, indent=2)

                self.logger.info(f"Updated features in file: {file_location}")

                return True
            except:
                self.logger.info(f"[ERROR] Unable to update features in file: {file_location}")
                return False

    def advancedfeaturematch(self, check_value, list_value):

        """ Checks for a feature containing a : within a list. If the feature already exists, this return True
        otherwise False is returned. """

        chk = False
        for substring in list_value:
            if substring.split(":")[0] == check_value.split(":")[0]:
                chk = True
        return chk

    def find_missing_features(self, main_features_file, check_features_file):

        """ Compares two json scratch org definition files and checks the main file has all the features which the
        check file has. You can then optionally update the current project file with missing features. """

        # Check two arrays have been passed
        if main_features_file is None or check_features_file is None:
            raise Exception("[ERROR] You must provide two files to compare. One or more is missing.")

        if not exists(main_features_file) or not exists(check_features_file):
            raise Exception("[ERROR] One of the files cannot be found. Check it has not been deleted.")

        self.logger.info(f"Feature Check: Comparing {main_features_file} to {check_features_file}")

        # Init Missing Features List
        missing_features = []

        try:
            # Load Main File
            with open(main_features_file) as main_json_file:
                main_json_file_data = json.load(main_json_file)

            if main_json_file_data['features'] is None:
                raise Exception(f"[ERROR] No features found in file: {main_json_file}. Check the file and try again.")
            main_comparison_list = main_json_file_data['features']
            main_comparison_list = [x.lower() for x in main_comparison_list]

            # Load Comparison File
            with open(check_features_file) as check_json_file:
                check_json_file_data = json.load(check_json_file)

            if check_json_file_data['features'] is None:
                raise Exception(f"[ERROR] No features found in file: {check_json_file}. Check the file and try again.")
            check_comparison_list = check_json_file_data['features']
            check_comparison_list = [x.lower() for x in check_comparison_list]

            # Compare both lists and populate missing list
            missing_feature_count = 0
            for missing_feature in check_comparison_list:
                if (":" not in missing_feature and not missing_feature.lower() in main_comparison_list) or (
                        ":" in missing_feature and not self.advancedfeaturematch(missing_feature.lower(),
                                                                                 main_comparison_list)):
                    missing_features.append(missing_feature.lower())
                    missing_feature_count += 1

            if len(missing_features) == 0:
                self.logger.info(
                    f"[OK] There are no missing features found when comparing to file: {check_features_file}")
            else:
                self.logger.info(
                    f"{missing_feature_count} missing feature(s) found, when comparing to file: {check_features_file}")

            missing_features.sort()

            return missing_features
        except:
            raise Exception("[ERROR] Failed to compare files.")

    def check_api_versions(self):

        """ Checks API Versions within the project are all in sync with cumulusci.yml file api version """

        project_api_version = self.project_config.project__package__api_version

        self.logger.info(f"API Version Check: Checking File API Versions are set to v{project_api_version}")

        # Check and Update sfdx-project.json File
        sfdx_version = self.get_json_file_value("sfdx-project.json", "sourceApiVersion")
        if project_api_version != sfdx_version:
            self.update_json_file_value("sfdx-project.json", "sourceApiVersion", project_api_version)
            self.logger.info("API Version Check: Updated sfdx-project.json File")

    def check_for_missing_files(self):

        """ Checks for essential files within the current project folder """

        if not exists("cumulusci.yml"):
            self.logger.info("[ERROR] Missing File: cumulusci.yml")
        if not exists("orgs/dev.json"):
            self.logger.info("[ERROR] Missing File: orgs/dev.json")
        if not exists("sfdx-project.json"):
            self.logger.info("[ERROR] Missing File: sfdx-project.json")
        if not exists("orgs/dev_preview.json"):
            self.logger.info("[ERROR] Missing File: orgs/dev_preview.json")

    def check_org_config_files(self):

        """ Checks the orgs/dev.json and orgs/dev_preview.json file for key values """

        self.logger.info("Scratch Org File Check: Checking your org config files for issues")
        error_found = False

        # Check that dev.json is set to an Enterprise Edition. Partner Enterprise would also pass check.
        if "enterprise" not in self.get_json_file_value("orgs/dev.json", "edition").lower():
            self.logger.info("Scratch Org File Check: [FAIL] Your org/dev.json file is not set to Enterprise edition.")
            error_found = True
            if not self.RunAllChecks:
                update_dev_input = input("                        Would you like to update the dev.json file edition? (y/n) Default y") or 'y'
            else:
                update_dev_input = 'y'
            if update_dev_input == 'y':
                self.update_json_file_value('orgs/dev.json', 'edition', 'Enterprise')
                self.logger.info("Scratch Org File Check: Updated orgs/dev.json to use Enterprise Edition")

        if "enterprise" not in self.get_json_file_value("orgs/dev_preview.json", "edition").lower():
            self.logger.info("Scratch Org File Check: [FAIL] Your org/dev_preview.json file is not set to Enterprise edition.")
            error_found = True
            if not self.RunAllChecks:
                update_dev_input = input(
                    "                        Would you like to update the dev_preview.json file edition? (y/n) Default y") or 'y'
            else:
                update_dev_input = 'y'
            if update_dev_input == 'y':
                self.update_json_file_value('orgs/dev.json', 'edition', 'Enterprise')
                self.logger.info("Scratch Org File Check: Updated orgs/dev_preview.json to use Enterprise Edition")

        instance = self.get_json_file_value("orgs/dev_preview.json", "instance") or ""
        if "na135" not in instance.lower():
            self.logger.info("Scratch Org File Check: [FAIL] Your org/dev_preview.json file is not set to the NA135 Instance.")
            error_found = True
            if not self.RunAllChecks:
                update_dev_input = input(
                    "                        Would you like to update the dev_preview.json file instance? (y/n) Default y") or 'y'
            else:
                update_dev_input = 'y'
            if update_dev_input == 'y':
                self.update_json_file_value('orgs/dev_preview.json', 'instance', 'NA135')
                self.remove_json_entry('orgs/dev_preview.json', 'release')

        if not error_found:
            self.logger.info("Scratch Org File Check: [OK] All files have passed checks")

    def source_org_feature_checker(self):

        """ Check all source project dev.json files for missing features from current project dev.json file """

        self.logger.info("Source Feature Check: Checking that all source dev.json file features are listed in the "
                         "current dev.json file")

        # Prepare Project File
        if not self.SkipCacheRebuild:
            self.clean_project()
            self.rebuild_cci_cache()
        else:
            self.logger.info("Cache Rebuild Skipped")

        # Locate all dev.json files in CCI Cache
        dev_files = glob.glob(".cci/projects" + "/**/dev.json", recursive=True)

        # Check for missing features and add them to dev.json
        main_missing_feature_list = []
        for feature_check_file in dev_files:
            missing_feature_list = self.find_missing_features("orgs/dev.json", feature_check_file)
            if missing_feature_list is not None and len(missing_feature_list) > 0:
                main_missing_feature_list.extend(missing_feature_list)
        if len(main_missing_feature_list) > 0:
            main_missing_feature_list.sort()
            self.update_org_file_features("orgs/dev.json", main_missing_feature_list)
        else:
            self.logger.info("Source Feature Check: No missing features found when comparing all sources to "
                             "orgs/dev.json")

    def org_feature_checker(self):

        """ Checks and updates the dev_preview.json file with missing features from the dev.json file """

        self.logger.info(
            "Scratch Org Config Check: Comparing dev.json and dev_preview.json files for missing features.")
        missing_features = self.find_missing_features("orgs/dev_preview.json", "orgs/dev.json")
        if len(missing_features) > 0:
            self.logger.info(
                "Scratch Org Config Check: Missing Features Found. Check and add the following features to the "
                "org/dev.json file")
            #self.logger.info(json.dumps(missing_features, indent=4))
            self.update_org_file_features("orgs/dev_preview.json", missing_features)
        else:
            self.logger.info("Scratch Org Config Check: No Missing Features Found")

    def check_project_file_naming(self):

        """ Checks that the project file names are set correctly """

        repo_url = InitProject.get_qbrix_repo_url(self)
        if repo_url is not None:
            repo_qbrix_name = repo_url.rsplit('/', 1)[-1]
        else:
            repo_qbrix_name = self.project_config.project__git__repo_url.rsplit('/', 1)[-1]

        project_name = self.project_config.project__name
        package_name = self.project_config.project__package__name
        repo_url = self.project_config.project__git__repo_url

        self.logger.info("Naming Check: Checking File and Project Naming aligns with correct Q Brix Name")
        file_name_error = False

        if project_name is None or package_name is None or repo_url is None:
            file_name_error = True
            self.logger.info(
                "Naming Check: [FAIL] One or more of the required parameters are missing from the cumulusci.yml file. Check that the Project name, Project Package Name and Repo URL have all been added and populated.")
            self.logger.info(
                f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

        else:

            # Check Repo Name has been found
            if repo_qbrix_name is None:
                file_name_error = True
                self.logger.info(
                    "Naming Check: [FAIL] Check you have a valid URL for the project > Repo Url in the cumulusci.yml file")
                self.logger.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check for the Template name in the config file.
            if 'xDO-Template' in project_name or 'xDO-Template' in package_name or 'xDO-Template' in repo_url:
                file_name_error = True
                self.logger.info(
                    "Naming Check: [FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url. xDO-Template was found and this should have been updated, see Readme.")
                self.logger.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check that the repo name and project names all match
            if not project_name == package_name == repo_qbrix_name:
                file_name_error = True
                self.logger.info(
                    "Naming Check: [FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url")
                self.logger.info(
                    f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

            # Check that the dev.json file has the correct qbrix name
            if not repo_qbrix_name in self.get_json_file_value("orgs/dev.json", "orgName"):
                self.logger.info("Naming Check: Updating OrgName in orgs/dev.json has not been updated.")
                self.update_json_file_value("orgs/dev.json", "orgName", f"{repo_qbrix_name} - Dev org")

            # Check that the dev_preview.json file has the correct qbrix name
            if not repo_qbrix_name in self.get_json_file_value("orgs/dev_preview.json", "orgName"):
                self.logger.info("Naming Check: Updating OrgName in orgs/dev_preview.json has not been updated.")
                self.update_json_file_value("orgs/dev_preview.json", "orgName", f"{repo_qbrix_name} - Preview Dev org")

        if not file_name_error:
            self.logger.info("[OK] All Checks Passed!")
        else:
            self.logger.info("Naming Check: [ACTION NEEDED] Some tests did not pass. Check the messages above for more information.")

        self.logger.info("[CHECK COMPLETE] Checking Q Brix Names")

    def rebuild_cci_cache(self):

        """" Rebuilds the CCI projects Cache folder using the dev_org flow from CCI """

        self.logger.info("[START] CCI Project Cache Rebuild Starting")
        subprocess.run(["cci", "flow", "info", "dev_org"])
        self.logger.info("[COMPLETE] CCI Project Cache Rebuild Complete!")

    def _run_task(self):
        self.logger.info("[HEALTH CHECKER] STARTING Q HEALTH CHECKER")
        QBrixUpdater.silent_run(self)
        self.check_project_file_naming()
        self.check_api_versions()
        self.check_for_missing_files()
        self.source_org_feature_checker()
        self.org_feature_checker()
        self.check_org_config_files()
        self.logger.info("[HEALTH CHECKER] Complete!")


class QBrixUpdater(BaseTask, ABC):

    task_options = {
        "UpdateLocation": {
            "description": "String URL for the location where the update package .zip file is located",
            "required": False
        },
        "ArchivePassword": {
            "description": "String password for the .zip file",
            "required": False
        },
        "IgnoreOptionalUpdates": {
            "description": "True or False - When True this will ignore any Optional Updates being added to the project.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(QBrixUpdater, self)._init_options(kwargs)
        self.ArchivePassword = self.options["ArchivePassword"] if "ArchivePassword" in self.options else None
        self.UpdateLocation = self.options["UpdateLocation"] if "UpdateLocation" in self.options else "https://qnextgen.s3.us-west-1.amazonaws.com/qbrix/q_update_package.zip"
        self.IgnoreOptionalUpdates = self.options["IgnoreOptionalUpdates"] if "IgnoreOptionalUpdates" in self.options else False

    def download_and_unzip(self, url):

        """ Downloads a .zip file and extracts all folders to the root project directory """

        http_response = urlopen(url)
        self.logger.info("Download Complete!")
        self.logger.info("Extracting Update Package...")
        try:
            zipfile = ZipFile(BytesIO(http_response.read()))

            # CHECK FOR MISSING DIRS AND CREATE THEM
            dir_check_list = [x for x in zipfile.namelist() if x.endswith('/')]
            for d in dir_check_list:
                if not exists(d):
                    os.mkdir(d)
                    self.logger.info(f"Created New Directory: {d}")

            # HANDLE ZIP PASSWORDS
            if not self.ArchivePassword is None:
                zipfile.setpassword(pwd=bytes(self.ArchivePassword, 'utf-8'))

            # EXTRACT FILES
            self.logger.info("Updating Q Brix files...")
            zipfile.extractall()

            return True
        except:
            self.logger.info("[ERROR] Update Failed!")
            if exists("q_update_package"):
                shutil.rmtree("q_update_package")
        return False
    
    def cleanup(self):
        if exists("__MACOSX"):
            shutil.rmtree("__MACOSX")
        if exists("tasks/__pycache__"):
            shutil.rmtree("tasks/__pycache__")
        if exists("tasks/custom/__pycache__"):
            shutil.rmtree("tasks/custom/__pycache__")
        if exists("q_update_package"):
            shutil.rmtree("q_update_package")
        if self.IgnoreOptionalUpdates:
            if exists("OPTIONAL_UPDATES"):
                shutil.rmtree("OPTIONAL_UPDATES")
        InitProject.replace_file_text(self, "cumulusci.yml", "tasks.custom.qbrix_utils.Initialise_Project", "tasks.custom.qbrix_utils.InitProject")
    
    def silent_run(self):
        self.IgnoreOptionalUpdates = True
        self.download_and_unzip(self.UpdateLocation)

    def _run_task(self):

        """" Downloads the update package from AWS S3 and applies updates """

        self.logger.info("Downloading Update Package...")

        if self.download_and_unzip(self.UpdateLocation):
            self.logger.info("Clearing cache and temp files...")
            self.cleanup()
        
        self.logger.info("Update Complete!")


class InitProject(BaseTask, ABC):

    task_options = {
        "TestMode": {
            "description": "When in test mode, no files are updated.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(InitProject, self)._init_options(kwargs)
        self.qbrix_owner = self.project_config.project__custom__qbrix_owner_name
        self.qbrix_owner_team = self.project_config.project__custom__qbrix_owner_team
        self.qbrix_publisher_name = self.project_config.project__custom__qbrix_publisher_name
        self.qbrix_publisher_team = self.project_config.project__custom__qbrix_publisher_team
        self.qbrix_documentation_url = self.project_config.project__custom__qbrix_documentation_url or 'https://confluence.internal.salesforce.com/pages/viewpage.action?pageId=487362018'
        self.qbrix_description = self.project_config.project__custom__qbrix_description
        self.project_name = self.project_config.project__name
        self.repo_url = self.project_config.project__git__repo_url
        self.template_file_location = "force-app/main/default/customMetadata/xDO_Base_QBrix_Register.xDO_Template.md-meta.xml"
        self.TestMode = False

        if "TestMode" in self.options:
            self.TestMode = self.options["TestMode"]

    def get_qbrix_repo_url(self):

        """ Get Repo URL for current Q Brix"""

        result = subprocess.run("git config --get remote.origin.url", shell=True, capture_output=True).stdout
        if result is None:
            repo_url = input(
                "                        Please Enter the URL for the Q brix Repo (e.g. https://www.github.com/sfdc-qbranch/Qbrix-1-repo): ")
        else:
            repo_url = result.decode('utf-8').rstrip().replace(".git", "")

        return repo_url

    def update_create_qbrix_register(self, file_location):

        now = datetime.now()

        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
      <CustomMetadata xmlns="http://soap.sforce.com/2006/04/metadata" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
          <label>{self.project_name}</label>
          <protected>true</protected>
          <values>
              <field>xDO_Content_Type__c</field>
              <value xsi:type="xsd:string">Metadata_and_Record_Data</value>
          </values>
          <values>
              <field>xDO_Description__c</field>
              <value xsi:type="xsd:string">WHO: {self.qbrix_owner_team} | {self.qbrix_owner}
      WHAT: {self.qbrix_description}
      WHEN: {now.strftime("%B %Y")}</value>
          </values>
          <values>
              <field>xDO_Documentation_Link__c</field>
              <value xsi:type="xsd:string">{self.qbrix_documentation_url}</value>
          </values>
          <values>
              <field>xDO_Publisher__c</field>
              <value xsi:type="xsd:string">{self.qbrix_publisher_team} | {self.qbrix_publisher_name}</value>
          </values>
          <values>
              <field>xDO_Repository_URL__c</field>
              <value xsi:type="xsd:string">{self.repo_url}</value>
          </values>
          <values>
              <field>xDO_Type__c</field>
              <value xsi:type="xsd:string">Base xDO Component</value>
          </values>
          <values>
              <field>xDO_Version__c</field>
              <value xsi:type="xsd:string">1.0</value>
          </values>
      </CustomMetadata>'''

        if self.TestMode:
            print(xml)
        else:
            with open(file_location, "w") as f:
                f.write(xml)

    def replace_file_text(self, file_location, old_text, new_text):

        """ Replace specific text within a file """

        if os.path.isfile(file_location):
            with open(f"{file_location}", "r") as tmpFile:
                fcontents = tmpFile.read()

            new_fcontents = fcontents.replace(f"{old_text}", f"{new_text}")

            with open(f"{file_location}", "w") as tmpFile:
                tmpFile.write(new_fcontents)

    def _run_task(self):

        self.logger.info("[Starting Q Brix Setup]")

        QBrixUpdater.silent_run(self)

        repo_url = self.get_qbrix_repo_url()
        qbrix_name = ""
        if repo_url != "":
            qbrix_name = repo_url.rsplit('/', 1)[-1]
            if qbrix_name is not None and qbrix_name != "":
                self.repo_url = repo_url
                self.project_name = qbrix_name

        # YAML File Update

        if self.project_name == "xDO-Template" or self.project_name != qbrix_name:
            self.replace_file_text("cumulusci.yml", "xDO-Template", f"{qbrix_name}")
            self.replace_file_text("cumulusci.yml", f"name: {self.project_name}", f"name: {qbrix_name}")

        # Registration File Update

        self.logger.info("Q Brix Details Check")

        if "OWNER NAME HERE" in self.qbrix_owner:
            self.qbrix_owner = input("                        Enter the owner name for this Q Brix (i.e. Who is the contact for issues?): ") or "OWNER NAME HERE"
            self.replace_file_text("cumulusci.yml", "OWNER NAME HERE", self.qbrix_owner)

        if "OWNER TEAM HERE" in self.qbrix_owner_team:
            self.qbrix_owner_team = input("                        Enter the owners team for this Q Brix (e.g. Q Branch): ") or "OWNER TEAM HERE"
            self.replace_file_text("cumulusci.yml", "OWNER TEAM HERE", self.qbrix_owner_team)

        if "OWNER OR PUBLISHER NAME HERE" in self.qbrix_publisher_name or "OWNER OR PUBLISHER TEAM HERE" in self.qbrix_publisher_team:
            same_person_check = input("                        Is the Owner the same person as the publisher? (Default y/n) ") or 'y'
            if same_person_check.lower() == "y":
                self.replace_file_text("cumulusci.yml", "OWNER OR PUBLISHER NAME HERE", self.qbrix_owner)
                self.replace_file_text("cumulusci.yml", "OWNER OR PUBLISHER TEAM HERE", self.qbrix_owner_team)
                self.qbrix_publisher_name = self.qbrix_owner
                self.qbrix_publisher_team = self.qbrix_owner_team
            else:

                if "OWNER OR PUBLISHER NAME HERE" in self.qbrix_publisher_name:
                    self.qbrix_publisher_name = input("                        Enter the publishers name for this Q Brix (i.e. Who is the contact for publishing updates?): ") or "OWNER OR PUBLISHER NAME HERE"
                    self.replace_file_text("cumulusci.yml", "OWNER OR PUBLISHER NAME HERE", self.qbrix_publisher_name)

                if "OWNER OR PUBLISHER TEAM HERE" in self.qbrix_publisher_team:
                    self.qbrix_publisher_team = input("                        Enter the publisher's team name for this Q Brix (e.g. Q Branch): ") or "OWNER OR PUBLISHER TEAM HERE"
                    self.replace_file_text("cumulusci.yml", "OWNER OR PUBLISHER TEAM HERE", self.qbrix_publisher_team)

        default_docs_location = f"https://confluence.internal.salesforce.com/pages/viewpage.action?pageId=487362018"
        if self.qbrix_documentation_url == "" or self.qbrix_documentation_url == default_docs_location:
            self.qbrix_documentation_url = input("                        Enter the URL for documentation related to this Q Brix: ") or default_docs_location
            self.replace_file_text("cumulusci.yml", default_docs_location, self.qbrix_documentation_url)

        if self.qbrix_description == "" or self.qbrix_description == "SHORT DESCRIPTION OF QBRIX HERE":
            self.qbrix_description = input("                        Enter a short description for this Q Brix (e.g. Deploys base configuration for Commerce Cloud): ") or "SHORT DESCRIPTION OF QBRIX HERE"
            self.replace_file_text("cumulusci.yml", "SHORT DESCRIPTION OF QBRIX HERE", self.qbrix_description)

        self.logger.info("Q Brix Details Updated")

        file_name = self.project_name.replace("-", "_")
        final_file_name = f"force-app/main/default/customMetadata/xDO_Base_QBrix_Register.{file_name}.md-meta.xml"

        if exists(final_file_name):
            self.update_create_qbrix_register(final_file_name)
            self.logger.info("Q Brix Registration: Updated Q Brix Register File")
        else:

            # Create Folder and File if they are missing
            if not exists("force-app/main/default/customMetadata"):
                os.mkdir("force-app/main/default/customMetadata")
            else:

                # Clean Up any existing files which would cause issues
                if not exists(self.template_file_location) and not exists(final_file_name):
                    register_files = glob.glob("force-app/main/default/customMetadata/" + "/**/xDO_Base_QBrix_Register.*.md-meta.xml", recursive=True)
                    for file_to_delete in register_files:
                        os.remove(file_to_delete)
                        self.logger.info(f"Q Brix Registration: Removed old or incorrect file {file_to_delete}")

                if exists(self.template_file_location):
                    os.rename(self.template_file_location, final_file_name)
                    self.logger.info("Q Brix Registration: Renamed Q Brix Register File")

                self.update_create_qbrix_register(final_file_name)
                self.logger.info("Q Brix Registration: Updated Q Brix Register File")

        # UPDATE SCRATCH ORG TEMPLATE FILES

        if exists("orgs/dev.json"):
            HealthChecker.update_json_file_value(self, "orgs/dev.json", "orgName", f"{self.project_name} - Dev org")
        if exists("orgs/dev_preview.json"):
            HealthChecker.update_json_file_value(self, "orgs/dev_preview.json", "orgName",
                                                 f"{self.project_name} - Dev Preview org")

        self.logger.info("Q Brix Setup: Scratch Org Files Updated")

        self.logger.info(
            "[Q Brix Setup Complete!]\n\n***Remember to update the Readme.md file and check in your changes.***")
