from genericpath import isfile
import json
import os
import re
import sys
import subprocess
from abc import abstractmethod

from cumulusci.core.config import ScratchOrgConfig
from cumulusci.tasks.sfdx import SFDXBaseTask
from cumulusci.core.exceptions import TaskOptionsError
from cumulusci.core.exceptions import CommandException
from cumulusci.core.keychain import BaseProjectKeychain


LOAD_COMMAND = "sfdx force:apex:execute "


class BatchAnonymousApex(SFDXBaseTask):

    keychain_class = BaseProjectKeychain
    task_options={
        
        "filepaths": {
            "description": "When mode is set to File, each file is executed in order",
            "required": False
        }
        ,
          "org": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        }
    }

    def _setprojectdefaults(self, instanceurl):
        subprocess.run([f"sfdx config:set instanceUrl={instanceurl}"], shell=True,capture_output=True)

    def _init_options(self, kwargs):
        super(BatchAnonymousApex, self)._init_options(kwargs)
        self.env = self._get_env()
        self.keychain = None


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

    def _prepruntime(self,a):
        
        if "org" not in self.options or not self.options["org"]:
            self._load_keychain()

        #if not passed in - fall back to the key ring data
        if "targetusername" not in self.options or not self.options["targetusername"]:
            
            if not isinstance(self.org_config, ScratchOrgConfig):
                self.targetusername = self.org_config.access_token
            else:
                self.targetusername = self.org_config.username
        else:
            self.targetusername = self.options["targetusername"]

        #if not passed in - fall back to the key ring data
        if "accesstoken" not in self.options or not self.options["accesstoken"]:
            self.accesstoken = self.org_config.access_token
        else:
            self.accesstoken = self.options["accesstoken"]

        #if not passed in - fall back to the key ring data
        if "instanceurl" not in self.options or not self.options["instanceurl"]:
            self.instanceurl = self.org_config.instance_url
        else:
            self.instanceurl = self.options["instanceurl"]
            
            
        #iterate the files
        if "filepaths" in self.options and self.options["filepaths"]:
            
            #cast to a dictionary
            self.filepaths = self.options["filepaths"]

            
    def _run_task(self):
    
        try:
            self._prepruntime(self)
            self._setprojectdefaults(self.instanceurl)
        except:
            self.logger.info('An Error has occurred.')

        for i,v in enumerate(self.filepaths):
            if os.path.isfile(v):
                runthiscmd =f"{LOAD_COMMAND} -f {v} -u {self.accesstoken} --json"
                self.logger.info(f'Running Apex Script in {v}')
                resp=subprocess.run([runthiscmd],shell=True, capture_output=True, cwd=self.options.get("dir"))
                self.logger.info(resp.stdout)

    
    def _handle_returncode(self, returncode, stderr):
        if returncode:
            message = "Return code: {}".format(returncode)
            if stderr:
                message += "\nstderr: {}".format(stderr.read().decode("utf-8"))
            self.logger.error(message)
            raise CommandException(message)