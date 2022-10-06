import glob
import json
import subprocess
import shutil
import os
from os.path import exists
from cumulusci.core.tasks import BaseTask
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

class HealthChecker(BaseTask):

  # Global Task Options

  task_options={
        "RunAllChecks": {
            "description": "Boolean, which when set to true runs all checks",
            "required": False
        },
        "SkipCacheRebuild": {
            "description": "Boolean, Skips the cci cache rebuild if true",
            "required": False
        }
    }

  def _init_options(self, kwargs):
    super(HealthChecker, self)._init_options(kwargs)

    self.RunAllChecks = True
    if "RunAllChecks" in self.options:
      self.RunAllChecks = self.options["RunAllChecks"]

    self.SkipCacheRebuild = False
    if "SkipCacheRebuild" in self.options:
      self.SkipCacheRebuild = self.options["SkipCacheRebuild"]

  # File and Project Utilities

  def clean_project(self):

    """ Removes Cached folders from project """

    self.logger.info("Checking for downloaded CCI project source caches in /.cci/projects...")
    if os.path.isdir(".cci/projects"):
      self.logger.info("Removing CCI project source caches...")
      shutil.rmtree(".cci/projects")
    
    self.logger.info("Checking for MDAPI src cache in /src...")
    if os.path.isdir("src"):
      self.logger.info("Removing MDAPI src cache...")
      shutil.rmtree("src")

    self.logger.info("Checking for Q Robot cache...")
    if os.path.isdir("browser"):
      self.logger.info("Removing Robot cache in /browser...")
      shutil.rmtree("browser")
    if os.path.isfile("log.html"):
      os.remove("log.html")
    if os.path.isfile("playwright-log.txt"):
      os.remove("playwright-log.txt")
    if os.path.isfile("output.xml"):
      os.remove("output.xml")
    if os.path.isfile("report.html"):
      os.remove("report.html")

  def get_json_file_value(self, file_location, key_name):

    """ Reads a value from a json file based on key name """

    if not file_location is None and os.path.isfile(file_location):
      with open(file_location) as mFile:
        mObject = json.load(mFile)
        mFile.close()
      
      try:
        return_value = mObject[key_name]
      except:
        return_value = ""
      return return_value
    else:
      self.logger.info(f"WARNING: Key {key_name} not found in {file_location}")
      return None

  def update_json_file_value(self, file_location, key_name, new_value):

    """ Updates a scratch org json file key value with a new value. Not designed to be used with a list """

    if not file_location is None and os.path.isfile(file_location):

      self.logger.info(f"Updating {file_location}, setting key {key_name} to a new value of {new_value}")

      with open(file_location) as mFile:
              mObject = json.load(mFile)
              mFile.close()

      mObject[key_name] = new_value

      with open(file_location, "w") as nFile:
        json.dump(mObject, nFile, indent=2)
        nFile.close()

      self.logger.info(f"{file_location} has been updated!")

  def update_org_file_features(self, file_location, missing_features):

    """ Update scratch org json file features with additional features """

    getResponse = input(f"Would you like to append these missing features to your {file_location} file? (y/n) Default y: ") or 'y'
    if getResponse == 'y':
      self.logger.info(f"Updating {file_location} file")

      with open(file_location) as mFile:
            mObject = json.load(mFile)
            mFile.close()

      current_features = mObject['features']
      current_features.extend(missing_features)
      current_features = [x.lower() for x in current_features]
      current_features.sort()

      clean_feature_list = []
      for f in current_features:
        if not f is None and not f.lower() in clean_feature_list:
            clean_feature_list.append(f.lower())

      mObject['features'] = clean_feature_list

      with open(file_location, "w") as nFile:
        json.dump(mObject, nFile, indent=2)
        nFile.close()

  def find_missing_features(self, main_features_file, check_features_file):

    """ Compares two json scratch org definition files and checks the main file has all the features which the check file has. You can then optionally update the current project file with missing features. """

    #Check two arrays have been passed
    if main_features_file is None or check_features_file is None:
      raise Exception("You must pass two arrays, one or more is missing")

    if not exists(main_features_file) or not exists(check_features_file):
      raise Exception("One of the files cannot be accessed. Check it has not been deleted.")

    self.logger.info(f"Comparing {main_features_file} to {check_features_file}")

    #Init Missing Features List
    missing_features = []

    #Get Features to Compare to 
    CompareToList = []
    CompareFromList = []

    try:
      #Load Main File
      with open(main_features_file) as mFile:
        mObject = json.load(mFile)
        mFile.close()

      CompareToList = mObject['features']
      CompareToList = [x.lower() for x in CompareToList]

      #Load Comparison File
      with open(check_features_file) as mFile:
        mObject = json.load(mFile)
        mFile.close()

      CompareFromList = mObject['features']
      CompareFromList = [x.lower() for x in CompareFromList]
    except:
      self.logger.info(f"ERROR: Failed to compare file: {check_features_file}")
      return None

    if CompareFromList is None:
      self.logger.info(f"ERROR: Failed to find any features in file: {check_features_file}")
      return None

    #Compare both lists and populate missing list
    for cf in CompareFromList:
      if cf.lower() not in CompareToList and cf.lower() not in missing_features:
        missing_features.append(cf.lower())

    if len(missing_features) == 0:
      self.logger.info(f"[OK] There are no missing features found when comparing to file: {check_features_file}")
    else:
      self.logger.info(f"[WARNING] There are missing features, when comparing to file: {check_features_file}")

    missing_features.sort()

    return missing_features     

  # File Checks

  def check_api_versions(self):

    """ Checks API Versions within the project are all in sync with cumulusci.yml file api version """

    project_api_version = self.project_config.project__package__api_version

    self.logger.info(f"\n\n[CHECK STARTED] Checking File API Versions are set to v{project_api_version}")

    self.logger.info("Checking sfdx-project.json file...")

    sfdx_version = self.get_json_file_value("sfdx-project.json", "sourceApiVersion")

    self.logger.info(f"sfdx-project.json API Version: {sfdx_version}")

    if project_api_version != sfdx_version:
      self.logger.info("[ERROR] Sfdx Project Version does not match Project API Version.")

      sfdx_input = input("Would you like to update the sfdx-project.json file? (y/n) Default y") or 'y'
      if sfdx_input == 'y':
        self.update_json_file_value("sfdx-project.json","sourceApiVersion",project_api_version)

    self.logger.info(f"[CHECK COMPLETE] Checking File API Versions are set to v{project_api_version} has completed.")

  def check_for_missing_files(self):

    """ Checks for essential files within the current project folder """

    self.logger.info("\n\n[CHECK STARTED] Checking for missing project files.")

    if not os.path.isfile("cumulusci.yml"):
      self.logger.warn("Missing File: cumulusci.yml")
    if not os.path.isfile("orgs/dev.json"):
      self.logger.warn("Missing File: orgs/dev.json")
    if not os.path.isfile("sfdx-project.json"):
      self.logger.warn("Missing File: sfdx-project.json")
    if not os.path.isfile("orgs/dev_preview.json"):
      self.logger.warn("Missing File: orgs/dev_preview.json")

    self.logger.info("[CHECK COMPLETE] Missing files check complete.\n\n")

  def check_org_config_files(self):

    """ Checks the orgs/dev.json and orgs/dev_preview.json file for key values """

    self.logger.info("\n\n[CHECK STARTED] Checking your org config files for issues")
    error_found = False 
    if not "enterprise" in self.get_json_file_value("orgs/dev.json", "edition").lower():
      self.logger.info("[FAIL] Your org/dev.json file is not set to Enterprise edition.")
      error_found = True
      devInput = input("Would you like to update the dev.json file? (y/n) Default y") or 'y'
      if devInput == 'y':
        self.update_json_file_value('orgs/dev.json', 'edition', 'Enterprise')

    if not "enterprise" in self.get_json_file_value("orgs/dev_preview.json", "edition").lower():
      self.logger.info("[FAIL] Your org/dev_preview.json file is not set to Enterprise edition.")
      error_found = True
      devInput = input("Would you like to update the dev_preview.json file? (y/n) Default y") or 'y'
      if devInput == 'y':
        self.update_json_file_value('orgs/dev_preview.json', 'edition', 'Enterprise')

    if not "preview" in self.get_json_file_value("orgs/dev_preview.json", "release").lower():
      self.logger.info("[FAIL] Your org/dev_preview.json file is not set to the preview release.")
      error_found = True
      devInput = input("Would you like to update the dev_preview.json file? (y/n) Default y") or 'y'
      if devInput == 'y':
        self.update_json_file_value('orgs/dev_preview.json', 'release', 'preview')

    
    if not error_found:
      self.logger.info("[OK] Both files have passed checks")

    self.logger.info("[CHECK COMPLETE] config files check complete.\n\n")

  def source_org_feature_checker(self):

    """ Check all source project dev.json files for missing features from current project dev.json file """

    self.logger.info("\n\n[CHECK STARTED] Checking that all source dev.json file features are listed in the current dev.json file")

    #Prepare Project File
    if not self.SkipCacheRebuild:
      self.clean_project()
      self.rebuild_cci_cache()
    else:
      self.logger.info("Cache Rebuild Skipped")

    #Locate all dev.json files in CCI Cache
    dev_files = glob.glob(".cci/projects" + "/**/dev.json", recursive = True)

    missing_features = []
    for f in dev_files:
      featureList = self.find_missing_features("orgs/dev.json", f)

      if not featureList is None:
        missing_features.extend(featureList)
      
    if len(missing_features) > 0:
      self.logger.info(json.dumps(missing_features, indent=4))
      self.update_org_file_features("orgs/dev.json",missing_features)
    else:
      self.logger.info("[OK] No Missing Features Found")  

    self.logger.info("[CHECK COMPLETE] config files check complete.\n\n")


  def org_feature_checker(self):

    """ Check and optionally update the dev_preview.json file with features from the dev.json file """

    self.logger.info("\n\n[CHECK STARTED] Checking dev_preview.json file has all the features which are in the dev.json file\n\n")  
    missing_features = []
    missing_features = self.find_missing_features("orgs/dev_preview.json", "orgs/dev.json")
    if len(missing_features) > 0:
      self.logger.info("WARNING: Missing Features Found. Check and add the following features to the org/dev.json file")  
      self.logger.info(json.dumps(missing_features, indent=4))
      self.update_org_file_features("orgs/dev_preview.json",missing_features)
    else:
      self.logger.info("[CHECK COMPLETE] No Missing Features Found\n\n")  

  def check_project_file_naming(self):

    """ Checks that the project file names are set correctly """

    project_name = self.project_config.project__name
    package_name = self.project_config.project__package__name
    repo_url = self.project_config.project__git__repo_url

    self.logger.info("\n\n[CHECK STARTING] Checking Q Brix Names")
    file_name_error = False 

    if project_name is None or package_name is None or repo_url is None:
      file_name_error = True
      self.logger.info("[FAIL] One of the names is missing in your cumulusci.yml file. Update the file and run the Health Checker again.")
    else:
      repo_qbrix_name = repo_url.rsplit('/', 1)[-1]

      if repo_qbrix_name is None:
        file_name_error = True
        self.logger.info("[FAIL] Check you have a valid URL for the project > Repo Url in the cumulusci.yml file")

        self.logger.info(f"Names Found:\nProject Name: {project_name}\nPackage Name: {package_name}\nRepo URL: {repo_url}\nQBrix Name (From Repo URL): {repo_qbrix_name}")

      if 'xDO-Template' in project_name or 'xDO-Template' in package_name or 'xDO-Template' in repo_url:
        file_name_error = True
        self.logger.info("[FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url. xDO-Template was found and this should have been updated, see Readme.")

      if not project_name == package_name == repo_qbrix_name:
        file_name_error = True
        self.logger.info("[FAIL] You must update your project names in the cumulusci.yml file to be the same as your Q Brix repo url")

      if not repo_qbrix_name in self.get_json_file_value("orgs/dev.json", "orgName"):
        file_name_error = True
        self.logger.info("[FAIL] OrgName in orgs/dev.json has not been updated.")
        uinput = input("Would you like to update the dev.json file? (y/n) Default y") or 'y'
        if uinput == 'y':
          self.update_json_file_value("orgs/dev.json", "orgName", f"{repo_qbrix_name} - Dev org")

      if not repo_qbrix_name in self.get_json_file_value("orgs/dev_preview.json", "orgName"):
        file_name_error = True
        self.logger.info("[FAIL] OrgName in orgs/dev_preview.json has not been updated.")
        uinput = input("Would you like to update the dev_preview.json file? (y/n) Default y") or 'y'
        if uinput == 'y':
          self.update_json_file_value("orgs/dev_preview.json", "orgName", f"{repo_qbrix_name} - Dev org")

    if not file_name_error:
      self.logger.info("[OK] All Checks Passed!")
    self.logger.info("[CHECK COMPLETE] Checking Q Brix Names")

  # Cache Utilities

  def rebuild_cci_cache(self):

    """" Rebuilds the CCI projects Cache folder using the dev_org flow from CCI """

    self.logger.info("\n\n[START] CCI Project Cache Rebuild Starting")
    subprocess.run(["cci", "flow" , "info", "dev_org"])
    self.logger.info("[COMPLETE] CCI Project Cache Rebuild Complete!\n\n")

  
  # MAIN EXECUTE
  
  def _run_task(self):
    self.logger.info("\n\n[HEALTH CHECKER] STARTING Q HEALTH CHECKER\n\n")
    self.check_project_file_naming()
    self.check_api_versions()
    self.check_for_missing_files()
    self.source_org_feature_checker()
    self.org_feature_checker()
    self.check_org_config_files()
    self.logger.info("\n\n[HEALTH CHECKER] Complete!\n\n")

class QBrixUpdater(BaseTask):

  # Global Task Options

  task_options={
        "UpdateLocation": {
            "description": "String URL for the location where the update package .zip file is located",
            "required": False
        }
    }

  def _init_options(self, kwargs):
    super(QBrixUpdater, self)._init_options(kwargs)

    self.UpdateLocation = "https://qnextgen.s3.us-west-1.amazonaws.com/qbrix/q_update_package.zip"
    if "UpdateLocation" in self.options:
      self.UpdateLocation = self.options["UpdateLocation"]
  
  def download_and_unzip(self, url):
    http_response = urlopen(url)
    self.logger.info("Download Complete!")
    self.logger.info("Updating Q Brix...")
    try:
      zipfile = ZipFile(BytesIO(http_response.read()))

      dir_check_list = [x for x in zipfile.namelist() if x.endswith('/')]

      for d in dir_check_list:
        if not exists(d):
          os.mkdir(d)

      zipfile.extractall()

      return True
    except:
      self.logger.info("[ERROR] Update Failed!")
    return False 


  def _run_task(self):

    """" Downloads the update package from AWS S3 and applies updates """

    self.logger.info("\n\n[START] QBrix Update Commencing")
    self.logger.info("Downloading Update Package...")

    if self.download_and_unzip(self.UpdateLocation):
      self.logger.info("Clearing cache and temp files...")
      if exists("__MACOSX"):
        shutil.rmtree("__MACOSX")
      if exists("tasks/__pycache__"):
        shutil.rmtree("tasks/__pycache__")
      if exists("tasks/custom/__pycache__"):
        shutil.rmtree("tasks/custom/__pycache__")
      if exists("tasks/__init__.py"):
        os.remove("tasks/__init__.py")
      if exists("tasks/custom/__init__.py"):
        os.remove("tasks/custom/__init__.py")
      if exists("q_update_package"):
        shutil.rmtree("q_update_package")
      self.logger.info("Cleanup Complete!")

      self.logger.info("[COMPLETE] Update Complete!")

