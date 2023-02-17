import json
import requests

from abc import abstractmethod
from cumulusci.core.config import ScratchOrgConfig
from cumulusci.tasks.sfdx import SFDXBaseTask
from cumulusci.core.exceptions import CommandException
from cumulusci.core.keychain import BaseProjectKeychain


class NGAbort(SFDXBaseTask):
    task_options = {

        "message": {
            "description": "Message to capture when condition is found",
            "required": False
        }
    }
    
    def _init_options(self, kwargs):
        super(NGAbort, self)._init_options(kwargs)
        self.abortmessage=None
        
    def _prepruntime(self):

        # if not passed in - fall back to the key ring data
        if "message" not in self.options or not self.options["message"]:
            self.abortmessage ='The when codition was met'
        else:
            self.abortmessage =self.options["message"]
        
    def _run_task(self):
        self._prepruntime()
        raise Exception(f'This QBrix was stopped due to :: {self.abortmessage}')
        
        
    

class NGOrgConfig(SFDXBaseTask):
    keychain_class = BaseProjectKeychain
    task_options = {

        "org": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        }
    }

    task_docs = """
    Gathers additional information from the source org and adds/updates the org_config collection so that you can then use these throughout your flow steps to define where clauses for tasks.
    """

    def _init_options(self, kwargs):
        super(NGOrgConfig, self)._init_options(kwargs)
        self.env = self._get_env()

    @property
    def keychain_cls(self):
        klass = self.get_keychain_class()
        return klass or self.keychain_class

    @abstractmethod
    def get_keychain_class(self):
        return None

    @property
    def keychain_key(self):
        return self.get_keychain_key()

    @abstractmethod
    def get_keychain_key(self):
        return None

    def _load_keychain(self):
        if self.keychain is not None:
            return

        keychain_key = self.keychain_key if self.keychain_cls.encrypted else None

        if self.project_config is None:
            self.keychain = self.keychain_cls(self.universal_config, keychain_key)
        else:
            self.keychain = self.keychain_cls(self.project_config, keychain_key)
            self.project_config.keychain = self.keychain

    def _prepruntime(self, a):

        if ("org" in self.options and not self.options["org"] is None) and self.keychain is None:
            self._load_keychain()
            self.logger.info("Org passed in but no keychain found in runtime")

        # if not passed in - fall back to the key ring data
        if "targetusername" not in self.options or not self.options["targetusername"]:

            if not isinstance(self.org_config, ScratchOrgConfig):
                self.targetusername = self.org_config.access_token
            else:
                self.targetusername = self.org_config.username
        else:
            self.targetusername = self.options["targetusername"]

        # if not passed in - fall back to the key ring data
        if "accesstoken" not in self.options or not self.options["accesstoken"]:
            self.accesstoken = self.org_config.access_token
        else:
            self.accesstoken = self.options["accesstoken"]

        # if not passed in - fall back to the key ring data
        if "instanceurl" not in self.options or not self.options["instanceurl"]:
            self.instanceurl = self.org_config.instance_url
        else:
            self.instanceurl = self.options["instanceurl"]

        self._inject_max_runtime()

    def _inject_max_runtime(self):

        if self.org_config.max_org_api_version is None:
            self.org_config.max_org_api_version = self._get_org_max_api_version()

        if self.org_config.is_qbrix_installed is None:
            self.org_config.is_qbrix_installed = self._is_qbrix_installed
            
        if self.org_config.is_object_in_org is None:
            self.org_config.is_object_in_org = self._is_object_present_in_org
            
        if self.org_config.is_psl_in_org is None:
            self.org_config.is_psl_in_org = self._is_psl_present_in_org
            
        if self.org_config.is_namespace_installed is None:
            self.org_config.is_namespace_installed = self._is_package_namespace_installed


    def _is_qbrix_installed(self, qbrixname):

        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+MasterLabel+from+xDO_Base_QBrix_Register__mdt+where+MasterLabel='{qbrixname}'"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        # print(response.text)
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
        # print(response.text)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1
    
    def _is_object_present_in_org(self, targetobject):
        
        #SELECT  QualifiedApiName FROM EntityDefinition Where QualifiedApiName=

        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+QualifiedApiName+from+EntityDefinition+where+QualifiedApiName='{targetobject}' LIMIT 1"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        # print(response.text)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1
    
    def _is_psl_present_in_org(self, psl):
        
        #e.g. 
        #SELECT  id,MasterLabel,DeveloperName from PermissionSetLicense where (Masterlabel='OmniStudioDesigner' or DeveloperName='OmniStudioDesigner')

        url = f"{self.instanceurl}/services/data/v56.0/query/?q=select+Id+from+PermissionSetLicense+where(Masterlabel='{psl}' or DeveloperName='{psl}') LIMIT 1"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        # print(response.text)
        data = json.loads(response.text)
        self.logger.info(data["totalSize"])
        return data["totalSize"] == 1

    def _get_org_max_api_version(self):

        url = f"{self.instanceurl}/services/data/"
        headers = {
            'Authorization': f'Bearer {self.accesstoken}',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        self.logger.info(response.text)

        return float(data[-1]['version'])

    def _run_task(self):

        self._prepruntime(self)

    def _handle_returncode(self, returncode, stderr):
        if returncode:
            message = "Return code: {}".format(returncode)
            if stderr:
                message += "\nstderr: {}".format(stderr.read().decode("utf-8"))
            self.logger.error(message)
            raise CommandException(message)
