import filecmp
import glob
import json
import os
import re
import shutil
import subprocess
from io import BytesIO
from os.path import exists
import tempfile
from typing import Optional
from urllib.request import urlopen
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from xml.dom import minidom

from qbrix.tools.shared.qbrix_json_tasks import update_json_file_value, get_json_file_value, remove_json_entry
from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.utils.qbrix_fart import FART
from qbrix.tools.shared.qbrix_cci_tasks import rebuild_cci_cache

log = init_logger()

DEFAULT_UPDATE_LOCATION = "https://qnextgen.s3.us-west-1.amazonaws.com/qbrix/q_update_package.zip"


def replace_file_text(file_location, old_text, new_text):

    """ Replace specific text within a file
    :param file_location: Relative path and file name of the file you want to replace text within
    :param old_text: Text string to search for
    :param new_text: New text to replace old text
    """
           
    if not exists(file_location):
        raise Exception(f"Error: File Path does not exist or you do not have access to the given file path. Please check this file path and update as required: {file_location}")

    try:
        log.info(f"Opening {file_location}...")
        with open(f"{file_location}", "r") as tmpFile:
            file_contents = tmpFile.read()
    except Exception as e:
        raise Exception(f"There was an error opening the file with path: {file_location}. Please check the file still exists and that you have access to read it. Error detail: {e}")

    # log.info(f"Searching for all references to '{old_text}' and replacing with '{new_text}'.")

    updated_file_contents = file_contents.replace(f"{old_text}", f"{new_text}")

    try:
        with open(f"{file_location}", "w") as tmpFile:
            tmpFile.write(updated_file_contents)
    except Exception as e:
        raise Exception(f"There was an error updating the file with path: {file_location}. Please check the file still exists and that you have access to edit it. Error detail: {e}")


def get_qbrix_repo_url():

    """ Get Repo URL for current Q Brix
    :return: Returns the GitHub repo url for the Q Brix.
    """
    result = None
    try:
        result = subprocess.run("git config --get remote.origin.url", shell=True, capture_output=True).stdout
    except Exception as e:
        log.error(f"Unable to access GitHub Repository connected to this project. Please check that you have an internet connection and access to the GitHub Repository and you have git installed on your device. Error Detail: {e}")

    if not result:
        repo_url = input("Please Enter the complete URL for the Q brix Repo which should be linked to this project (e.g. https://www.github.com/sfdc-qbranch/Qbrix-1-repo): ")
        if repo_url == "" or repo_url is None:
            log.error("A valid GitHub Repo address was not entered. Please ensure that you enter the full URL for the repo.")
            raise Exception("No GitHub Repo URL found or connected to this project. Skipping task")
    else:
        repo_url = result.decode('utf-8').rstrip().replace(".git", "")

    return repo_url


def advanced_feature_match(check_value, list_value):
    """ Checks for a feature containing a : within a list. If the feature already exists, this return True
    otherwise False is returned.
    :param check_value: Value to check
    :param list_value: List to check
    :return: Returns True if feature already exists in list or False if not """

    if ":" not in check_value:
        log.debug("Feature was passed to advanced feature match which does not match format expected.")
        return

    chk = False
    for substring in list_value:
        if substring.split(":")[0] == check_value.split(":")[0]:
            chk = True
    return chk


def check_and_delete_dir(dir_path):
    """ Deletes a folder (and all contents) if it exists. Returns True if folder has been deleted.
    :param dir_path: Relative path to directory
    :return: True when directory has been deleted. False if there was an issue.
    """

    if dir_path is None or dir_path == "":
        log.error("No Directory Path was provided. Skipping task to delete directory.")
        return
    if exists(dir_path):
        try:
            shutil.rmtree(f"{dir_path}")
            log.info(f"Deleted {dir_path} and its contents (if any)")
            return True
        except Exception as e:
            log.error(f"Unable to delete directory with path: {dir_path}. {e}")
            return False
    else:
        log.debug(f"Directory {dir_path} not found. Skipping.")
        return True


def check_and_delete_file(file_path):
    """ Deletes a File if it exists. Returns True if File has been removed.
     :param file_path: Relative File path and name of the file to delete.
     :return: True if deleted and False if there was an issue.
     """

    if file_path == "":
        return False
    if exists(file_path):
        try:
            os.remove(f"{file_path}")
            log.info(f"File Deleted: {file_path}")
            return True
        except Exception as e:
            log.error(f"Unable to remove file: {file_path}. {e}")
            return False
    else:
        log.debug(f"File {file_path} not found. Skipping.")
        return True


def update_org_file_features(file_location, missing_features, auto: Optional[bool] = False):
    """ Update scratch org json file features with additional features.
    :param file_location: Relative path to file and file name
    :param missing_features: list of missing features
    :param auto: When True auto updates the file without prompting
    :return: True when complete, False if there was an issue. """

    if not exists(file_location) or missing_features is None:
        raise Exception("[ERROR] File Location was not found or feature list was empty.")

    if not auto:
        get_response = input(
            f"Would you like to append these missing features to your {file_location} file? (y/n) Default y: ") \
                       or 'y'
    else:
        get_response = 'y'

    if get_response == 'y':
        log.info(f"Updating: {file_location}")

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
                        ":" in current_feature and not advanced_feature_match(current_feature.lower(),
                                                                              clean_feature_list)):
                    clean_feature_list.append(current_feature.lower())

            for missing_feature in missing_features:
                if (":" not in missing_feature and not missing_feature.lower() in clean_feature_list) or (
                        ":" in missing_feature and not advanced_feature_match(missing_feature.lower(),
                                                                              clean_feature_list)):
                    clean_feature_list.append(missing_feature.lower())

            clean_feature_list.sort()

            # Update File
            json_file_data['features'] = clean_feature_list
            with open(file_location, "w") as nFile:
                json.dump(json_file_data, nFile, indent=2)

            log.info(f"Updated features in file: {file_location}")

            return True
        except Exception as e:
            log.error(f"[ERROR] Unable to update features in file: {file_location}. Error Message: {e}")
            return False


def find_missing_features(main_features_file, check_features_file):
    """ Compares two json scratch org definition files and checks the main file has all the features which the
    check file has. You can then optionally update the current project file with missing features.
    :param main_features_file: Relative path and file name for the file you want to update
    :param check_features_file: Relative path and file name for the file you want check against
    :return: List of features """

    if not exists(main_features_file) or not exists(check_features_file):
        raise Exception("[ERROR] One of the files cannot be found. Check it has not been deleted.")

    log.info(f"Feature Check: Comparing {main_features_file} to {check_features_file}")

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

            add_feature = False

            # Separate out features which contain a :
            if ":" in missing_feature:
                if not advanced_feature_match(missing_feature.lower(), main_comparison_list):
                    add_feature = True
            else:
                if not missing_feature.lower() in main_comparison_list:
                    add_feature = True

            if add_feature:
                missing_features.append(missing_feature.lower())
                missing_feature_count += 1

        if len(missing_features) == 0:
            log.info(
                f"[OK] There are no missing features found when comparing to file: {check_features_file}")
        else:
            log.info(
                f"{missing_feature_count} missing feature(s) found, when comparing to file: {check_features_file}")

        missing_features.sort()

        return missing_features
    except Exception as e:
        raise Exception(f"[ERROR] Failed to compare files. {e}")


def check_org_config_files(auto: Optional[bool] = False):
    """ Checks the orgs/dev.json and orgs/dev_preview.json file for key values """

    log.info("Scratch Org File Check: Checking your org config files for issues")
    error_found = False

    # Check that dev.json is set to an Enterprise Edition. Partner Enterprise would also pass check.
    if "enterprise" not in get_json_file_value("orgs/dev.json", "edition").lower():
        log.info("Scratch Org File Check: [FAIL] Your org/dev.json file is not set to Enterprise edition.")
        error_found = True
        if not auto:
            update_dev_input = input("\n\nWould you like to update the dev.json file edition? (y/n) Default y: ") or 'y'
        else:
            update_dev_input = 'y'
        if update_dev_input == 'y':
            update_json_file_value('orgs/dev.json', 'edition', 'Enterprise')
            log.info("Scratch Org File Check: Updated orgs/dev.json to use Enterprise Edition")

    if "enterprise" not in get_json_file_value("orgs/dev_preview.json", "edition").lower():
        log.error(
            "Scratch Org File Check: [FAIL] Your org/dev_preview.json file is not set to Enterprise edition.")
        error_found = True
        if not auto:
            update_dev_input = input(
                "Would you like to update the dev_preview.json file edition? (y/n) Default y: ") or 'y'
        else:
            update_dev_input = 'y'
        if update_dev_input == 'y':
            update_json_file_value('orgs/dev.json', 'edition', 'Enterprise')
            log.info("Scratch Org File Check: Updated orgs/dev_preview.json to use Enterprise Edition")

    instance = get_json_file_value("orgs/dev_preview.json", "instance") or ""
    if "na135" not in instance.lower():
        log.error(
            "Scratch Org File Check: [FAIL] Your org/dev_preview.json file is not set to the NA135 Instance.")
        error_found = True
        if not auto:
            update_dev_input = input(
                "\n\nWould you like to update the dev_preview.json file instance? (y/n) Default y: ") or 'y'
        else:
            update_dev_input = 'y'
        if update_dev_input == 'y':
            update_json_file_value('orgs/dev_preview.json', 'instance', 'NA135')
            remove_json_entry('orgs/dev_preview.json', 'release')

    if not error_found:
        log.info("Scratch Org File Check: [OK] All files have passed checks")


def check_api_versions(project_api_version):
    """ Checks API Versions within the project are all in sync with cumulusci.yml file api version """

    log.info(f"API Version Check: Checking File API Versions are set to v{project_api_version}")

    # Check and Update sfdx-project.json File
    sfdx_version = get_json_file_value("sfdx-project.json", "sourceApiVersion")
    if project_api_version != sfdx_version:
        update_json_file_value("sfdx-project.json", "sourceApiVersion", project_api_version)
        log.info("API Version Check: Updated sfdx-project.json File")


def source_org_feature_checker(skip_rebuild = False, auto=False):
    """ Check all source project dev.json files for missing features from current project dev.json file
    :param skip_rebuild: Set to True when you do no want CumulusCI Cache Rebuilt. Defaults to False
    """

    log.info("Source Feature Check: Checking that all source dev.json file features are listed in the "
             "current dev.json file")

    # Prepare Project File
    if not skip_rebuild:
        clean_project_files()
        rebuild_cci_cache()
    else:
        log.info("Cache Rebuild Skipped")

    # Locate all dev.json files in CCI Cache
    dev_files = glob.glob(".cci/projects" + "/**/dev.json", recursive=True)

    # Check for missing features and add them to dev.json
    main_missing_feature_list = []
    for feature_check_file in dev_files:
        missing_feature_list = find_missing_features("orgs/dev.json", feature_check_file)
        if missing_feature_list is not None and len(missing_feature_list) > 0:
            main_missing_feature_list.extend(missing_feature_list)
    if len(main_missing_feature_list) > 0:
        main_missing_feature_list.sort()
        update_org_file_features("orgs/dev.json", main_missing_feature_list, auto)
    else:
        log.info("Source Feature Check: No missing features found when comparing all sources to "
                 "orgs/dev.json")


def org_feature_checker(auto=False):
    """ Checks and updates the dev_preview.json file with missing features from the dev.json file """

    log.info(
        "Scratch Org Config Check: Comparing dev.json and dev_preview.json files for missing features.")
    missing_features = find_missing_features("orgs/dev_preview.json", "orgs/dev.json")
    if len(missing_features) > 0:
        log.info("Scratch Org Config Check: Missing Features Found. Updating orgs/dev_preview.json file")
        update_org_file_features("orgs/dev_preview.json", missing_features, auto)
    else:
        log.info("Scratch Org Config Check: No Missing Features Found")


def check_for_missing_files():
    """ Checks for essential files within the current project folder """

    if not exists("cumulusci.yml"):
        log.error("[ERROR] Missing File: cumulusci.yml")
    if not exists("orgs/dev.json"):
        log.error("[ERROR] Missing File: orgs/dev.json")
    if not exists("sfdx-project.json"):
        log.error("[ERROR] Missing File: sfdx-project.json")
    if not exists("orgs/dev_preview.json"):
        log.error("[ERROR] Missing File: orgs/dev_preview.json")


def download_and_unzip(url: Optional[str] = DEFAULT_UPDATE_LOCATION, archive_password: Optional[str] = "",
                       ignore_optional_updates: Optional[bool] = False, q_update: Optional[bool] = False):
    """ Downloads a .zip file and extracts all folders to the root project directory """

    log.info("Downloading Update Package")
    http_response = urlopen(url)
    log.info("Download Complete!")
    log.info("Extracting Update Package to project folder...")
    try:
        zipfile = ZipFile(BytesIO(http_response.read()))

        # Extraction Path
        extract_path = ""

        # HANDLE Q UPDATE
        if q_update:
            if not exists(".qbrix"):
                log.info("Creating Update Folder")
                os.mkdir(".qbrix")

            if not exists(".qbrix/Update"):
                log.info("Creating Update Folder")
                os.mkdir(".qbrix/Update")

            extract_path = ".qbrix/Update/"

            if exists(".qbrix/Update/xDO-Template-main"):
                log.info("Removing Old Source")
                shutil.rmtree(".qbrix/Update/xDO-Template-main")

        # CHECK FOR MISSING DIRS AND CREATE THEM
        dir_check_list = [x for x in zipfile.namelist() if x.endswith('/')]
        for d in dir_check_list:
            if not exists(extract_path + d):
                os.mkdir(extract_path + d)
                log.info(f"Created New Directory: {extract_path + d}")

        # HANDLE ZIP PASSWORDS
        if archive_password is not None and archive_password != "":
            zipfile.setpassword(pwd=bytes(archive_password, 'utf-8'))

        # EXTRACT FILES
        log.info("Updating Q Brix files...")
        zipfile.extractall(path=extract_path)

        # Clean Up
        dirs = glob.glob(".qbrix/Update/**/__pycache__/", recursive=True)
        for folder in dirs:
            shutil.rmtree(folder)
        if exists("__MACOSX"):
            shutil.rmtree("__MACOSX")
        if exists("q_update_package"):
            shutil.rmtree("q_update_package")
        if ignore_optional_updates:
            if exists(".qbrix/OPTIONAL_UPDATES"):
                shutil.rmtree(".qbrix/OPTIONAL_UPDATES")

        return True
    except Exception as e:
        log.error(f"[ERROR] Update Failed! Error Message: {e}")
        if exists("q_update_package"):
            shutil.rmtree("q_update_package")
    return False


def check_and_update_old_class_refs():
    # Health Check
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_utils.HealthChecker",
                      "qbrix.tools.utils.qbrix_health_check.HealthChecker")

    # Q Brix Update
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_utils.QBrixUpdater",
                      "qbrix.tools.utils.qbrix_update.QBrixUpdater")

    # FART
    replace_file_text("cumulusci.yml", "tasks.custom.fart.FART",
                      "qbrix.tools.utils.qbrix_fart.FART")

    # Batch Apex
    replace_file_text("cumulusci.yml", "tasks.custom.batchanonymousapex.BatchAnonymousApex",
                      "qbrix.tools.utils.qbrix_batch_apex.BatchAnonymousApex")

    # Org Generator
    replace_file_text("cumulusci.yml", "tasks.custom.orggenerator.Spin",
                      "qbrix.tools.utils.qbrix_org_generator.Spin")

    # Init Project
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_utils.Initialise_Project",
                      "qbrix.tools.utils.qbrix_project_setup.InitProject")
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_utils.InitProject",
                      "qbrix.tools.utils.qbrix_project_setup.InitProject")

    # List Q Brix
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_sf.ListQBrix",
                      "qbrix.salesforce.qbrix_salesforce_tasks.ListQBrix")

    # Banner
    replace_file_text("cumulusci.yml", "tasks.custom.announce.CreateBanner",
                      "qbrix.tools.shared.qbrix_console_utils.CreateBanner")

    # Mass File Ops
    replace_file_text("cumulusci.yml", "tasks.custom.qbrix_utils.MassFileOps",
                      "qbrix.tools.utils.qbrix_mass_ops.MassFileOps")

    # SFDMU
    replace_file_text("cumulusci.yml", "tasks.custom.sfdmuload.SFDMULoad", "qbrix.tools.data.qbrix_sfdmu.SFDMULoad")

    # TESTIM
    replace_file_text("cumulusci.yml", "tasks.custom.testim.RunTestim", "qbrix.tools.testing.qbrix_testim.RunTestim")


def clean_project_files():
    """ Removes Cached files and folders from q brix project """

    try:
        check_and_delete_dir(".cci/projects")
        check_and_delete_dir("src")
        check_and_delete_dir("browser")
        check_and_delete_file("log.html")
        check_and_delete_file("playwright-log.txt")
        check_and_delete_file("output.xml")
        check_and_delete_file("report.html")
        check_and_delete_file("validationresult.json")

    except Exception() as e:
        log.info(f"Failed to Clean Up Project Files. Error Message: {e}")


def delete_standard_fields():
    """ Removes Standard Salesforce Fields from Project """
    object_fields = glob.glob("force-app/main/default/objects" + "/**/*.field-meta.xml", recursive=True)
    if len(object_fields) == 0:
        log.info("No Standard/Core Fields Found in Project!")
    else:
        for of in object_fields:
            if not os.path.basename(of).endswith(".field-meta.xml"):
                os.remove(of)
                log.info(f"Deleted File: {of}")


def update_file_api_versions(project_api_version):
    """ Update file API version in project
    :param project_api_version: Target API Version you want to update the files to. e.g. 56
    """
    # Handle Bulk Files
    # To add: Visualforce and Apex Triggers
    class_files = glob.glob("force-app/main/default/classes" + "/**/*.cls-meta.xml", recursive=True)
    aura_files = glob.glob("force-app/main/default/aura" + "/**/*.cmp-meta.xml", recursive=True)
    lwc_files = glob.glob("force-app/main/default/lwc" + "/**/*.js-meta.xml", recursive=True)
    results = []
    results.extend(class_files)
    results.extend(aura_files)
    results.extend(lwc_files)
    for f in results:
        try:
            FART.fartbetween(FART, f, "<apiVersion>", "</apiVersion>", project_api_version, None)
            log.info(f"[OK] File Updated: {f}")
        except Exception as e:
            log.error(f"[FAILED] File Update Failed: {f} - {e}")
    # Handle Single Files
    if exists("files/package.xml"):
        try:
            FART.fartbetween(FART, "files/package.xml", "<version>", "</version>", project_api_version, None)
            log.info(f"[OK] File Updated: files/package.xml")
        except Exception as e:
            log.error(f"[FAILED] File Update files/package.xml - Error: {e}")
    if exists("sfdx-project.json"):
        try:
            update_json_file_value("sfdx-project.json", "sourceApiVersion", project_api_version)
            log.info(f"[OK] File Updated: sfdx-project.json")
        except Exception as e:
            log.error(f"[FAILED] File Update sfdx-project.json - Error: {e}")


def upsert_gitignore_entries(list_entries):
    if len(list_entries) == 0:
        log.debug("Updated .gitignore file skipped. No entries passed to check.")
        return

    entries_to_append = []

    with open(".gitignore", 'a+') as git_file:
        git_file.seek(0)
        content = git_file.read()

        for entry in list_entries:
            if entry not in content or f"#{entry}" in content:
                if entry.lower() not in entries_to_append:
                    entries_to_append.append(entry.lower())
            else:
                continue

        if len(entries_to_append) > 0:
            for e in entries_to_append:
                git_file.write(f"{e}\n")


def check_permset_group_files():
    psg_files = glob.glob("force-app/main/default/permissionsetgroups" + "/**/*.permissionsetgroup-meta.xml",
                          recursive=True)

    if len(psg_files) > 0:
        log.info("Checking Permission Set Group Files...")
        for psg in psg_files:
            log.info(f"Checking {psg} file configuration.")
            FART.fartbetween(FART, psg, "<status>", "</status>", "Outdated", None)
    else:
        log.info("No Permission Set Group Files in Project, skipping check.")

def add_prefix(path, prefix):
    parts = os.path.split(path)
    return os.path.join(parts[0], prefix + parts[1])

def update_references(old_value, new_value, prefix=''):

    if old_value == 'All':
        return

    project_path = 'force-app/main/default'
    reference_pattern = re.compile(rf'(?<!{prefix})\b{old_value}\b')

    for root, dirs, files in os.walk(project_path):
        for file_name in files:
            if "external_id" in os.path.basename(file_name).lower() or os.path.basename(file_name).lower().startswith("sdo_") or os.path.basename(file_name).lower().startswith("xdo_") or os.path.basename(file_name).lower().startswith("db_"):
                #print(f"SKIPPED: {file_name}")
                continue

            if os.path.basename(root) in {"standardValueSets", "roles", "corsWhitelistOrigins"}:
                continue

            file_path = os.path.join(root, file_name)
            with open(file_path, 'r') as f:
                f.seek(0)
                file_contents = f.read()

            new_contents = reference_pattern.sub(new_value, file_contents)
            if new_contents != file_contents:
                with open(file_path, 'w') as f:
                    f.write(new_contents)
                    print(f'Updated references for {old_value} in {file_path}')

def assign_prefix_to_files(prefix, parent_folder='force-app/main/default', interactive_mode=False):

    # Validation
    if not prefix:
        raise Exception("Error: No prefix provided to the Mass Rename Tool. You must provide a prefix.")
    
    if not os.path.exists(parent_folder):
        raise Exception("Parent folder doesn't exist. Please correct the folder path and try again.")

    # Generate Prefix Variations
    prefix = prefix.replace("_", "")
    under_prefix = str(prefix).upper() + "_"
    open_prefix = str(prefix).upper() + " "
    
    # Set Matching Pattern for Cumstom API references
    PATTERN = re.compile(r'^.+$')
    FILE_PATTERN = re.compile(r'^.+.')

    paths_to_rename = []
   
    # Find and Update Custom Object Folder Names
    for root, dirs, files in os.walk(os.path.join(parent_folder, 'objects')):
        for dir_name in dirs:
            if PATTERN.match(dir_name) and not dir_name.lower().startswith(prefix.lower()):
                old_path = os.path.join(root, dir_name)
                new_path = add_prefix(old_path, under_prefix)
                print(f'CUSTOM OBJECT DIRECTORY FOUND:\n    Current Path: {old_path}\n    Updated Path: {new_path}')
                approve_change = False
                if interactive_mode:
                    confirmation = input("Are you happy to make this change? (Y/n) : ") or 'y'
                    if confirmation.lower() == 'y':
                        approve_change = True
                    else:
                        approve_change = False
                else:
                    approve_change = True
                if approve_change:
                    paths_to_rename.append((old_path, new_path))
                    update_references(os.path.basename(old_path), os.path.basename(new_path), prefix)
                

        if root.endswith('compactLayouts') or root.endswith('recordTypes') or root.endswith('businessProcesses'):
            for file_name in files:

                if root.endswith('listViews') and "All.listView" in file_name:
                    continue

                if not file_name.lower().startswith(prefix.lower()) and not file_name.lower().startswith('sdo_') and not file_name.lower().startswith('xdo_'):
                    old_path = os.path.join(root, file_name)
                    if root.endswith('businessProcesses'):
                        new_path = add_prefix(old_path, open_prefix)
                    else:
                        new_path = add_prefix(old_path, under_prefix)
                    #os.rename(old_path, new_path)
                    print(f'CUSTOM OBJECT FILE FOUND:\n    Current Path: {old_path}\n    Updated Path: {new_path}')

                    old_value = os.path.splitext(os.path.basename(old_path))[0].split('.')[0]
                    new_value = os.path.splitext(os.path.basename(new_path))[0].split('.')[0]

                    approve_change = False
                    if interactive_mode:
                        confirmation = input("Are you happy to make this change? (Y/n) : ") or 'y'
                        if confirmation.lower() == 'y':
                            approve_change = True
                        else:
                            approve_change = False
                    else:
                        approve_change = True
                    if approve_change:
                        paths_to_rename.append((old_path, new_path))
                        update_references(old_value, new_value, prefix)

                    

    # Update Custom File Names
    file_list = glob.glob(f'{parent_folder}/**/*.*-meta.xml', recursive=True)

    for current_file in file_list:

        file_name = os.path.basename(current_file)
        directory_name = os.path.dirname(current_file)

        if os.path.basename(directory_name) in {"settings", "standardValueSets", "roles", "corsWhitelistOrigins", "layouts", "quickActions"} or "objects" in directory_name:
            continue

        if "external_id" in file_name.lower() or file_name.lower().startswith("sdo_") or file_name.lower().startswith("xdo_") or file_name.lower().startswith(f"{prefix}") or file_name.lower().startswith("db_") or file_name.lower().startswith("standard-"):
            continue

        old_path = current_file
        new_path = add_prefix(old_path, under_prefix)
        print(f'PROJECT CUSTOM FILE FOUND:\n    Current Path: {old_path}\n    Updated Path: {new_path}')

        old_value = os.path.splitext(os.path.basename(old_path))[0].split('.')[0]
        new_value = os.path.splitext(os.path.basename(new_path))[0].split('.')[0]

        approve_change = False
        if interactive_mode:
            confirmation = input("Are you happy to make this change? (Y/n) : ") or 'y'
            if confirmation.lower() == 'y':
                approve_change = True
            else:
                approve_change = False
        else:
            approve_change = True
        if approve_change:
            paths_to_rename.append((old_path, new_path))
            update_references(old_value, new_value, prefix)

    # Rename all files and Folders where matches were located
    sorted_list = sorted(paths_to_rename, key=lambda x: len(x[1]), reverse=True)
    for path_to_update, new_updated_path in sorted_list:
        os.rename(path_to_update, new_updated_path)
        print(f"FILE OR FOLDER RENAMED:\n    Previous Path: {path_to_update}\n    New Path: {new_updated_path}")

def create_external_id_field(file_path):
    with open(file_path) as file:
        for line in file:
            object_name = line.strip()
            if object_name:
                object_dir = os.path.join("force-app", "main", "default", "objects", object_name)
                fields_dir = os.path.join(object_dir, "fields")
                field_file = os.path.join(fields_dir, "External_ID.field-meta.xml")
                if not os.path.exists(object_dir):
                    os.makedirs(object_dir)
                if not os.path.exists(fields_dir):
                    os.makedirs(fields_dir)
                if not os.path.exists(field_file):
                    with open(field_file, "w") as f:
                        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        f.write('<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">\n')
                        f.write('    <fullName>External_ID</fullName>\n')
                        f.write('    <externalId>true</externalId>\n')
                        f.write('    <label>External ID</label>\n')
                        f.write('    <length>50</length>\n')
                        f.write('    <required>false</required>\n')
                        f.write('    <trackTrending>false</trackTrending>\n')
                        f.write('    <type>Text</type>\n')
                        f.write('    <unique>false</unique>\n')
                        f.write('</CustomField>\n')

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    output, error = process.communicate()

    if error:
        raise Exception(error)
    return output, error
    
def compare_directories(dcmp):
    new_or_changed = []
    for name in dcmp.right_only:
        new_or_changed.append(os.path.join(dcmp.right, name))
    for name in dcmp.diff_files:
        new_or_changed.append(os.path.join(dcmp.right, name))
    for sub_dcmp in dcmp.subdirs.values():
        new_or_changed.extend(compare_directories(sub_dcmp))
    return new_or_changed

def compare_metadata(target_org_alias):

    # Default Org Command
    if os.path.exists('src'):
        shutil.rmtree('src')

    if os.path.exists('mdapipkg'):
        shutil.rmtree('mdapipkg')

    if os.path.exists('upgrade_src'):
        shutil.rmtree('upgrade_src')

    run_command("cci task run dx_convert_from")

    # Retrieve metadata from the target org
    log.info(f"Retrieving metadata from the target org with alias {target_org_alias} (This can take a few minutes..)")
    retrieve_command = f"cci task run dx --command \"force:mdapi:retrieve -r mdapipkg -k src/package.xml\" --org {target_org_alias}"
    run_command(retrieve_command)

    # Unzip the retrieved metadata
    log.info("Unpacking Metadata")
    unzip_command = f"unzip -o mdapipkg/unpackaged.zip -d mdapipkg/unpackaged"
    run_command(unzip_command)

    # Compare the local and target org's metadata
    log.info("Comparing Metadata")
    dcmp = filecmp.dircmp('mdapipkg/unpackaged/unpackaged', 'src')
    new_or_changed = compare_directories(dcmp)

    changes = []

    if len(new_or_changed) > 0:
        log.info(f"{len(new_or_changed)} changes found")
        log.info("Generating new update package in directory: upgrade_src")

        for file_path in new_or_changed:

            if os.path.basename(os.path.dirname(file_path)) in {'settings', 'labels'}:
                log.info(f"Skipping {file_path} as it contains a high risk metadata type. Review the contents individually.")
                continue

            changes.append(file_path)

            # Determine the destination path of the metadata file to copy
            dst_file_path = os.path.join('upgrade_src', file_path.replace('src/', ''))

            # Create the destination directory if it does not exist
            dst_directory = os.path.dirname(dst_file_path)
            if not os.path.exists(dst_directory):
                os.makedirs(dst_directory)

            # Copy the metadata file to the destination directory
            shutil.copy2(file_path, dst_file_path)

        run_command("sfdx force:source:manifest:create --sourcepath upgrade_src --manifestname upgrade_src/package")

    return changes

def push_changes(target_org_alias):

    # Push Changes
    push_command = f"cci task run deploy --path upgrade_src --org {target_org_alias}"
    push_output, push_error = run_command(push_command)

    log.info("Upgrade Pushed!")
    return push_output

def create_permission_set_file(name, label):

    if os.path.exists(f"force-app/main/default/permissionsets/{name}.permissionset-meta.xml"):
        os.remove(f"force-app/main/default/permissionsets/{name}.permissionset-meta.xml")

    # Create the root element
    root = ET.Element("PermissionSet", attrib={"xmlns":"http://soap.sforce.com/2006/04/metadata"})

    # Set the label
    label_element = ET.SubElement(root, "label")
    label_element.text = label

    # Traverse through the object folders
    objects_path = "force-app/main/default/objects"
    if os.path.exists(objects_path):
        for object_folder in os.listdir(objects_path):
            object_folder_path = os.path.join(objects_path, object_folder)
            if os.path.isdir(object_folder_path):
                # Add object permissions
                object_permissions_element = ET.SubElement(root, "objectPermissions")
                ET.SubElement(object_permissions_element, "allowCreate").text = "true"
                ET.SubElement(object_permissions_element, "allowDelete").text = "true"
                ET.SubElement(object_permissions_element, "allowEdit").text = "true"
                ET.SubElement(object_permissions_element, "allowRead").text = "true"
                ET.SubElement(object_permissions_element, "modifyAllRecords").text = "true"
                ET.SubElement(object_permissions_element, "object").text = f"{object_folder}"
                ET.SubElement(object_permissions_element, "viewAllRecords").text = "true"

                # Traverse through the field folders
                fields_folder_path = os.path.join(object_folder_path, "fields")
                if os.path.isdir(fields_folder_path):
                    for field_file in os.listdir(fields_folder_path):
                        if field_file.endswith(".field-meta.xml"):
                            field_name = field_file[:-15]
                            field_permissions_element = ET.SubElement(root, "fieldPermissions")
                            ET.SubElement(field_permissions_element, "editable").text = "true"
                            ET.SubElement(field_permissions_element, "field").text = f"{object_folder}.{field_name}"
                            ET.SubElement(field_permissions_element, "readable").text = "true"

                        # # Add object permissions for lookup fields that reference objects not in the project
                        field_path = os.path.join(fields_folder_path, field_file)
                        with open(field_path, "r") as file:
                            contents = file.read()
                            reference_to_start = contents.find("<referenceTo>")
                            reference_to_end = contents.find("</referenceTo>")
                            if reference_to_start != -1 and reference_to_end != -1:
                                reference_object = contents[reference_to_start + 13:reference_to_end]
                                if reference_object not in os.listdir(objects_path):
                                    object_permissions_element = ET.SubElement(root, "objectPermissions")
                                    ET.SubElement(object_permissions_element, "allowCreate").text = "false"
                                    ET.SubElement(object_permissions_element, "allowDelete").text = "false"
                                    ET.SubElement(object_permissions_element, "allowEdit").text = "false"
                                    ET.SubElement(object_permissions_element, "allowRead").text = "false"
                                    ET.SubElement(object_permissions_element, "modifyAllRecords").text = "false"
                                    ET.SubElement(object_permissions_element, "object").text = f"{reference_object}"
                                    ET.SubElement(object_permissions_element, "viewAllRecords").text = "false"

                # Traverse through the record type files
                record_types_folder_path = os.path.join(object_folder_path, "recordTypes")
                if os.path.isdir(record_types_folder_path):
                    for record_type_file in os.listdir(record_types_folder_path):
                        if record_type_file.endswith(".recordType-meta.xml"):
                            record_type_name = record_type_file[:-20]
                            record_type_permissions_element = ET.SubElement(root, "recordTypeVisibilities")
                            ET.SubElement(record_type_permissions_element, "default").text = "false"
                            ET.SubElement(record_type_permissions_element, "recordType").text = f"{object_folder}.{record_type_name}"
                            ET.SubElement(record_type_permissions_element, "visible").text = "true"

    # Traverse through the Apex class files
    classes_path = "force-app/main/default/classes"
    if os.path.exists(classes_path):
        for class_file in os.listdir(classes_path):
            if class_file.endswith(".cls"):
                class_name = class_file[:-4]
                class_permissions_element = ET.SubElement(root, "classAccesses")
                ET.SubElement(class_permissions_element, "apexClass").text = f"{class_name}"
                ET.SubElement(class_permissions_element, "enabled").text = "true"

    # Traverse through the tab files
    tabs_path = "force-app/main/default/tabs"
    if os.path.exists(tabs_path):
        for tab_file in os.listdir(tabs_path):
            if tab_file.endswith(".tab-meta.xml"):
                tab_name = tab_file[:-14]
                tab_permissions_element = ET.SubElement(root, "tabSettings")
                ET.SubElement(tab_permissions_element, "tab").text = f"{tab_name}"
                ET.SubElement(tab_permissions_element, "visibility").text = "Visible"

    # Traverse through the Application files
    apps_path = "force-app/main/default/applications"
    if os.path.exists(apps_path):
        for apps_file in os.listdir(apps_path):
            if apps_file.endswith(".app-meta.xml"):
                app_name = apps_file[:-14]
                app_permissions_element = ET.SubElement(root, "applicationVisibilities")
                ET.SubElement(app_permissions_element, "application").text = f"{app_name}"
                ET.SubElement(app_permissions_element, "visible").text = "true"

    # Create the file
    if not os.path.exists("force-app/main/default/permissionsets"):
        os.makedirs("force-app/main/default/permissionsets")

    file_path = f"force-app/main/default/permissionsets/{name}.permissionset-meta.xml"
    with open(file_path, "w", encoding="utf-8") as file:
        xml_string = ET.tostring(root, encoding="unicode")
        xml_dom = minidom.parseString(xml_string)
        formatted_xml = xml_dom.toprettyxml(indent="  ", encoding="utf-8")
        file.write(formatted_xml.decode("utf-8"))