import base64
import json
import os
import pathlib
import subprocess
import yaml
from abc import ABC
from typing import Optional
from datetime import datetime, timedelta

import click
from cumulusci.core.config import ScratchOrgConfig
from cumulusci.core.config.org_config import OrgConfig
from cumulusci.core.dependencies.dependencies import PackageVersionIdDependency, PackageNamespaceVersionDependency, \
    BaseGitHubDependency, UnmanagedGitHubRefDependency
from cumulusci.core.dependencies.resolvers import dependency_filter_ignore_deps, get_static_dependencies
from cumulusci.core.exceptions import CumulusCIException
from cumulusci.tasks.salesforce.update_dependencies import UpdateDependencies
from cumulusci.tasks.sfdx import SFDXOrgTask
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger, run_command
from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.core.utils import process_bool_arg, process_list_of_pairs_dict_arg
from cumulusci.tasks.salesforce.users.photos import UploadProfilePhoto

log = init_logger()
now = datetime.now()


def salesforce_query(soql, org_config, raw_return=False):
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

            if result.stderr:
                error_detail = result.stderr.decode("UTF-8")
                log.error(f"Salesforce Query Error - Details: {error_detail}")
            else:
                log.error("Salesforce Query Failed, although no error detail was returned.")

            return None

        json_result = json.loads(result.stdout)

        if json_result["result"]["totalSize"] >= 1:
            if raw_return:
                return json_result
            else:
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


class CreateUser(BaseSalesforceApiTask, ABC):
    salesforce_task = True
    

    task_docs = """
    Overview: Creates a user or multiple user records in a target org.

    There are two modes for this task:

    Single Record: Within the step, add a task with options set for 'data', 'role', 'profile' and optionally 'permission_set_api_names', 'permission_set_group_api_names' and 'user_profile_image'. The 'path' option must not be defined as this will enable bulk mode and ignore anything you have set for the options mentioned.

    Bulk Mode: Create a .yml file within your project and provide the relative path to the file, within the 'path' option. If the path is left blank, single record mode will be used.

    Note: For both modes above, the option for 'upsert_field' must be set if you are not using External_ID__c

    See https://confluence.internal.salesforce.com/display/QNEXTGENDEMOS/User+Manager for additional help and templates.

    """

    task_options = {
        "org": {
            "description": "Org Alias for the target org",
            "required": False
        },
        "data": {
            "description": "Dictionary of Fields and Related Values. Use the API name for the field and then set the value accordingly.",
            "required": False
        },
        "role": {
            "description": "Name of the Role which the new user should have, e.g. CEO",
            "required": False
        },
        "profile": {
            "description": "Name of the Profile the new user should have. e.g. System Administrator",
            "required": False
        },
        "permission_set_api_names": {
            "description": "List of API names for the Permission Sets you want to apply to the newly created User",
            "required": False
        },
        "permission_set_group_api_names": {
            "description": "List of API names for the Permission Set Groups you want to apply to the newly created User",
            "required": False
        },
        "user_profile_image": {
            "description": "Local file location for the image you want to assign to the user profile. (BETA) Use the keyword AUTO to automatically generate an image for the user.",
            "required": False
        },
        "upsert_field": {
            "description": "API Name of the field you wish to use for upserts. Must be a unique field on the object. Defaults to External_ID__c",
            "required": False
        },
        "path": {
            "description": "Path to yml file containing user record entries. Setting this will ignore anything set for other options. Setting this enables bulk mode and ignores other options.",
            "required": False
        },
    }

    def _init_options(self, kwargs):
        super(CreateUser, self)._init_options(kwargs)
        self.data = process_list_of_pairs_dict_arg(self.options["data"]) if "data" in self.options else None
        self.role = self.options["role"] if "role" in self.options else None
        self.profile = self.options["profile"] if "profile" in self.options else None
        self.permission_set_api_names = list(
            self.options["permission_set_api_names"]) if "permission_set_api_names" in self.options else None
        self.permission_set_group_api_names = list(self.options[
                                                       "permission_set_group_api_names"]) if "permission_set_group_api_names" in self.options else None
        self.user_profile_image = self.options["user_profile_image"] if "user_profile_image" in self.options else None
        self.upsert_field = self.options["upsert_field"] if "upsert_field" in self.options else "External_ID__c"
        self.path = self.options["path"] if "path" in self.options else None
    
    def _time_since_modified(self, path):
        
        """
        Returns the time since the target file was last modified
        """
        
        timestamp = os.path.getmtime(str(path))
        last_modified = datetime.fromtimestamp(timestamp)
        return datetime.now() - last_modified

    def _get_user_desc(self, tmp_file_location = ".qbrix/user_object_desc.json"):

        """
        Gets the Object Describe information for the User Object in the target org. This is also cached via a file in .qbrix directory.
        """

        TTL = timedelta(minutes=10)

        if os.path.exists(tmp_file_location) and self._time_since_modified(tmp_file_location) <= TTL:
            log.info("Loading cached File...")
            with open(tmp_file_location, "r") as user_detail_file:
                return json.load(user_detail_file)
        else:
            log.info("Loading info from org and creating cached File...")
            api = self.sf
            user_details = api.User.describe()
            if not os.path.exists(".qbrix"):
                os.mkdir(".qbrix")
            with open (tmp_file_location, "w") as user_detail_file:
                json.dump(user_details,user_detail_file)
            return user_details

    def _remove_missing_field_schema(self, submitted_dict, field_names):
        """
        Removes keys and related values from a submitted dict containing User fields and values, which are not present in the target org.
        """

        submitted_fields = list(submitted_dict.keys())
        for key in submitted_fields:
            if key not in field_names:
                log.debug(f"The field with api name '{key}' has been removed from this deployment, as it is not present (or accessible) in the target org.")
                del submitted_dict[key]
        return submitted_dict

    def _ensure_required_fields(self, submitted_dict, field_names, role, profile):
        """
        Checks that all required fields have a value, even if none were passed in, except for FirstName and LastName which are required.
        """

        if "FirstName" not in submitted_dict.keys() or "LastName" not in submitted_dict.keys():
            raise Exception("You must provide at least a FirstName and LastName.")

        if "External_ID__c" not in submitted_dict.keys() and "External_ID__c" in field_names:
            log.debug("External ID (API Name External_ID__c) missing for User. It is HIGHLY recommended that an External ID is provided for all user records you are created. Please review your configuration.")

        if "Key_User__c" not in submitted_dict.keys() and "Key_User__c" in field_names:
            log.debug("Key User Field has not been defined and this is recommended for Key Demo Persona records by setting the Key_User__c field.")

        if "Alias" not in submitted_dict.keys():
            generated_alias = str(submitted_dict.get("FirstName"))[0:1].lower() + str(submitted_dict.get("LastName"))[0:4].lower()
            submitted_dict.update({"Alias": generated_alias})

        if "DefaultGroupNotificationFrequency" not in submitted_dict.keys():
            submitted_dict.update({"DefaultGroupNotificationFrequency": "N"})

        if "DigestFrequency" not in submitted_dict.keys():
            submitted_dict.update({"DigestFrequency": "N"})

        if "Email" not in submitted_dict.keys():
            generated_email = f"{submitted_dict.get('FirstName').lower()}.{submitted_dict.get('LastName').lower()}{now.strftime('%H%M%S')}@example.com"
            submitted_dict.update({"Email": generated_email})

        if "Username" not in submitted_dict.keys():
            generated_username = f"{submitted_dict.get('FirstName').lower()}{now.strftime('%m%Y%H%M%S')}@example.com"
            submitted_dict.update({"Username": generated_username})

        if "EmailEncodingKey" not in submitted_dict.keys():
            submitted_dict.update({"EmailEncodingKey": "UTF-8"})

        if "LanguageLocaleKey" not in submitted_dict.keys():
            submitted_dict.update({"LanguageLocaleKey": "en_US"})

        if "LocaleSidKey" not in submitted_dict.keys():
            submitted_dict.update({"LocaleSidKey": "en_US"})

        if "TimeZoneSidKey" not in submitted_dict.keys():
            submitted_dict.update({"TimeZoneSidKey": "America/Los_Angeles"})

        if "UserPermissionsInteractionUser" not in submitted_dict.keys():
            submitted_dict.update({"UserPermissionsInteractionUser": True})

        if "UserPermissionsMarketingUser" not in submitted_dict.keys():
            submitted_dict.update({"UserPermissionsMarketingUser": True})

        if "UserPermissionsOfflineUser" not in submitted_dict.keys():
            submitted_dict.update({"UserPermissionsOfflineUser": False})

        api = self.sf

        # Lookup Role
        role_id = api.query(f"SELECT Id FROM UserRole WHERE Name = '{role}' LIMIT 1")["records"][0]["Id"]
        if not role_id:
            raise Exception("User Creation Failed to get Role ID for provided Role: " + role)
        if "UserRoleId" not in submitted_dict.keys():
            submitted_dict.update({"UserRoleId": role_id})

        # Lookup Profile
        profile_id = api.query(f"SELECT Id FROM Profile WHERE Name = '{profile}' LIMIT 1")["records"][0]["Id"]
        if not profile_id:
            raise Exception("User Creation Failed to get Profile ID for provided Profile: " + profile)
        if "ProfileId" not in submitted_dict.keys():
            submitted_dict.update({"ProfileId": profile_id})

        return submitted_dict

    def _load_data(self, submitted_dict):

        """
        Loads User Record from submitted dict with User field and value data. Returns a UserId if successful.
        """

        api = self.sf

        # Check If Upsert Can be Used
        if self.upsert_field in submitted_dict.keys():
            upsert_result = api.upsert(self.upsert_field, submitted_dict)
            if str(upsert_result).startswith("2"):
                log.info("Upsert Completed! Loading record information...")
                user_info = api.query(f"SELECT Id FROM User WHERE {self.upsert_field} = '{submitted_dict.get(self.upsert_field)}' AND IsActive = True LIMIT 1")
                if user_info["totalSize"] == 0:
                    log.error("User Upsert Failed. Skipping user...")
                    return
                else:
                    return user_info["records"][0]["Id"]
            else:
                log.error("Upsert Failed. Skipping Record...")
                return

        # Check for Existing User and create or update a record as required
        user_lookup = api.query(f"SELECT Id FROM User WHERE FirstName = '{submitted_dict.get('FirstName')}' AND LastName = '{submitted_dict.get('LastName')}' AND IsActive = True LIMIT 1")
        if user_lookup["totalSize"] == 0:
            log.info("Creating new User record...")
            result = api.User.create(submitted_dict)
            if result["id"]:
                log.info("Record Created with ID: " + result["id"])
                return result["id"]
            else:
                log.error("Record Failed to Create.")
                return
        else:
            user_id = user_lookup["records"][0]["Id"]
            result = api.User.update(user_id, submitted_dict)
            if str(result).startswith("2"):
                log.info("Record Updated!")
                return user_id
            else:
                log.error("Record Failed to Update. User ID: " + user_id)
                return 
    
    def _upload_user_profile_image(self, user_id, path_to_image):
        """
        Uploads and assigns a user profile image
        """

        if str(path_to_image).upper() == "AUTO":
            return 

        if not os.path.exists(path_to_image):
            log.error(f"Image file path ({path_to_image}) does not exist. Please check file path and try again.")
        else:
            try:
                api = self.sf
                path = pathlib.Path(path_to_image)
                photo_id = api.ContentVersion.create(
                    {
                        "PathOnClient": path.name,
                        "Title": path.stem,
                        "VersionData": base64.b64encode(path.read_bytes()).decode("utf-8"),
                    }
                )

                content_version_id = photo_id["id"]
                content_document_id = api.query(f"SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = '{content_version_id}'")["records"][0]["ContentDocumentId"]

                api.restful(
                    f"connect/user-profiles/{user_id}/photo",
                    data=json.dumps({"fileId": content_document_id}),
                    method="POST",
                )
            except Exception as e:
                log.error(f"Upload Failed. Error details: {e}")

            log.info("Image Uploaded and assigned!")

    def _assign_permission(self, mode, user_id, api_names):

        match str(mode).upper():
            case "PERMISSIONSET":
                object_name = "PermissionSet"
                message_name = "Permission Set"
                lookup_field = "Name"
                assignment_field = "PermissionSetId"
            case "PERMISSIONSETGROUP":
                object_name = "PermissionSetGroup"
                message_name = "Permission Set Group"
                lookup_field = "DeveloperName"
                assignment_field = "PermissionSetGroupId"
            case _:
                return False

        # Loop Through Permission Set Names
        for perm in list(api_names):

            api = self.sf

            # Check for labels and non api names
            if " " in perm:
                log.debug(f"{message_name} {perm} is not a valid api name for a {message_name}. Please check the api names are valid and try again. Continuing to next record.")
                continue

            # Check Permission Set Exists
            permission_set_query = api.query(f"SELECT Id FROM {object_name} WHERE {lookup_field} = '{perm}' LIMIT 1")
            if permission_set_query["totalSize"] == 0:
                log.debug(f"{message_name} with api name {perm} was not found in the target org, skipping assignment.")
                continue
            else:
                permission_set_id = permission_set_query["records"][0]["Id"]

            # Check for existing Permission Set Assignment
            permission_set_assignment_query = api.query(f"SELECT Id FROM PermissionSetAssignment WHERE AssigneeId = '{user_id}' AND {assignment_field} = '{permission_set_id}' LIMIT 1")
            if permission_set_assignment_query["totalSize"] == 1:
                log.info(f"{message_name} with api name {perm} has already been assigned to the user. Skipping...")
                continue

            # Create Permission Set Assignment
            permset_creation_result = api.PermissionSetAssignment.create(
                {
                    "AssigneeId": user_id,
                    str(assignment_field): permission_set_id
                }
            )
            if permset_creation_result["id"]:
                log.info(f"{message_name} (With API Name: {perm}) has been assigned (ID: {permset_creation_result['id']})!")
            else:
                log.error(f"{message_name} (With API Name: {perm}) failed to assign. Moving onto next {message_name} (if any). Details: {permset_creation_result}")
                return False

        return True

    def _process_user_record(self, user_record_data, field_names):

        data = user_record_data["data"]
        role = user_record_data["role"]
        profile = user_record_data["profile"]
        user_profile_image = user_record_data["user_profile_image"]
        permission_set_api_names = user_record_data["permission_set_api_names"]
        permission_set_group_api_names = user_record_data["permission_set_group_api_names"]

        log.info(f"Creating User with the following details: \n{json.dumps(data, indent=1, sort_keys=True)}")
        log.info("Preparing Data for User Record")

        # Clean Up Fields which are not available on the User object
        self._remove_missing_field_schema(data, field_names)

        # Check and Update Required Fields
        self._ensure_required_fields(data, field_names, role, profile)
        log.info("Data Ready to upload")

        # Load Data
        final_user_id = self._load_data(data)

        log.info("Final User Record ID: " + final_user_id)

        # Handle Profile Image Upload
        if user_profile_image:
            log.info("Adding User Profile Image...")
            self._upload_user_profile_image(final_user_id, user_profile_image)
            
        # Handle Permissions
        if permission_set_api_names:
            log.info("Assigning Permission Sets...")
            self._assign_permission("PermissionSet", final_user_id, permission_set_api_names)

        if permission_set_group_api_names: 
            log.info("Assigning Permission Set Groups...")
            self._assign_permission("PermissionSetGroup", final_user_id, permission_set_group_api_names)


    def _run_task(self):
        

        api = self.sf

        if api is not None:

            # Check for invalid configuration
            if self.path and self.data:
                log.debug("A Path has been specified, which enabled Bulk Mode and ignores other settings which have been defined. Check help pages and update as required. Will continue running in Bulk Mode")

            # Get User Fields for Target Org
            user_desc = self._get_user_desc()
            field_names = [field['name'] for field in user_desc['fields']]

            # Enable bulk mode if path provided
            if self.path:
                log.info("BULK MODE ENABLED")

                if not os.path.exists(self.path):
                    raise Exception("Path to file cannot be found.")

                with open(self.path, "r") as file:
                    user_data = yaml.load(file, Loader=yaml.FullLoader)
                for user in user_data["users"]:
                    user_record_data = user_data["users"][user]
                    if user_record_data:
                        self._process_user_record(user_record_data, field_names)
            else:

                log.info("SINGLE RECORD MODE ENABLED")

                if not self.data or not self.profile or not self.role:
                    log.error("When running in Single Record mode, you must provide values for the options data, role and profile as a minimum requirement.")
                else:
                    log.info(f"Creating User with the following details: \n{json.dumps(self.data, indent=1, sort_keys=True)}")
                    log.info("Preparing Data for User Record")

                    # Clean Up Fields which are not available on the User object
                    self._remove_missing_field_schema(self.data, field_names)

                    # Check and Update Required Fields
                    self._ensure_required_fields(self.data, field_names, self.role, self.profile)
                    log.info("Data Ready to upload")

                    # Load Data
                    final_user_id = self._load_data(self.data)

                    log.info("Final User Record ID: " + final_user_id)

                    # Handle Profile Image Upload
                    if self.user_profile_image:
                        log.info("Adding User Profile Image...")
                        self._upload_user_profile_image(final_user_id, self.user_profile_image)
                        
                    # Handle Permissions
                    if self.permission_set_api_names:
                        log.info("Assigning Permission Sets...")
                        self._assign_permission("PermissionSet", final_user_id, self.permission_set_api_names)

                    if self.permission_set_group_api_names: 
                        log.info("Assigning Permission Set Groups...")
                        self._assign_permission("PermissionSetGroup", final_user_id, self.permission_set_group_api_names)

        else:
            log.error("Failed to connect to Salesforce Org, please try again.")


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
