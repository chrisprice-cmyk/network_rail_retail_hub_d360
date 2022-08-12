import json
import os
import re
import sys
import subprocess
import keyring
from abc import abstractmethod

from cumulusci.core.config import ScratchOrgConfig
from cumulusci.tasks.command import Command
from cumulusci.core.exceptions import TaskOptionsError
from cumulusci.core.exceptions import CommandException
from cumulusci.core.keychain import BaseProjectKeychain



class FART(Command):


    keychain_class = BaseProjectKeychain
    
    task_options={
        "srcfile": {
            "description": "Directory path to the export.json to upload",
            "required": True
        },
        "mode": {
            "description": "Run mode: Text or Between or SOQL",
            "required": False,
            "default": "Text"
        },
          "soql": {
            "description": "For run mode of SQOL, the soql statement to use in scalar mode to.",
            "required": False
        },
          "find": {
            "description": "Text pattern to locate in the source file.",
            "required": False
        }
          ,
          "findleft": {
            "description": "Left pattern string to locate in the text of the source file.",
            "required": False
        }
          
          ,
          "findright": {
            "description": "Right side of pattern to find in the text of the source file.",
            "required": False
        }
          ,
          "replacewith": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        }
          ,
          "org": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        }
    }
   
    def _init_options(self, kwargs):
        super(Command, self)._init_options(kwargs)
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
        
    def _prepruntime(self):
        
        if "org" not in self.options or not self.options["org"]:
            self._load_keychain()
            
        if "srcfile" not in self.options or not self.options["srcfile"]:
            raise ValueError('No source file provided to analyze.')
        else:
            self.fartpath = self.options["srcfile"]
            
        if "mode" not in self.options or not self.options["mode"]:
            self.fartmode = "Text"
        else:
            self.fartmode = self.options["mode"]
            
        #universal
        if "replacewith" not in self.options or not self.options["replacewith"]:
            self.fartreplacewith = None
        else:
            self.fartreplacewith = self.options["replacewith"]

        #universal
        if "find" not in self.options or not self.options["find"]:
                self.fartfind= None
        else:
            self.fartfind = self.options["find"]
        
        if self.fartmode=="Between" or self.fartmode=="SOQL-Between":
            if "findleft" not in self.options or not self.options["findleft"]:
                self.fartfindleft = None
            else:
                self.fartfindleft = self.options["findleft"]
                
            if "findright" not in self.options or not self.options["findright"]:
                self.fartfindright = None
            else:
                self.fartfindright = self.options["findright"]

        if self.fartmode=="SOQL" or self.fartmode=="SOQL-Between":
            
            if "soql" not in self.options or not self.options["soql"]:
                self.soql = None
            else:
                self.soql = self.options["soql"]

            if not self.org_config.access_token is None:
                self.accesstoken = self.org_config.access_token
                
            if not self.org_config.instance_url is None:
                self.instanceurl =self.org_config.instance_url
        

    def run(self):
        if self.fartmode =="Text":
            self.runwithtext()
            
        if self.fartmode =="Between":
            self.runtextbetween()
            
        if self.fartmode =="SOQL":
            self.runwithsoql()
            
        if self.fartmode =="SOQL-Between":
            self.runwithsoqlbetween()
            
    def runwithtext(self):
        self.fart(self.fartpath, self.fartfind, self.fartreplacewith)
        
    def runtextbetween(self):
        self.fartbetween(self.fartpath, self.fartfindleft, self.fartfindright, self.fartreplacewith)

    def runwithsoql(self):
        if(self.soql is None or self.soql==""):
            return
        
        subprocess.run([f"sfdx config:set instanceUrl={self.instanceurl}"], shell=True,capture_output=True)
 
        self.fartsoql(self.fartpath,self.fartfind, self.accesstoken, self.soql)
        
    def runwithsoqlbetween(self):
        
        if(self.soql is None or self.soql==""):
            return
        
        if(self.fartfindleft is None or self.fartfindright is None):
            return
        
        subprocess.run([f"sfdx config:set instanceUrl={self.instanceurl}"], shell=True,capture_output=True)

        self.fartsoqlbetween(self.fartpath, self.fartfindleft, self.fartfindright, self.accesstoken, self.soql)

    def _run_task(self):
        self._prepruntime()
        self.run()

    def _handle_returncode(self, returncode, stderr):
        if returncode:
            message = "Return code: {}".format(returncode)
            if stderr:
                message += "\nstderr: {}".format(stderr.read().decode("utf-8"))
            self.logger.error(message)
            raise CommandException(message)
        
        
    def fart(self,srcfile: str, find: str, replacewith: str):
        
        
        if os.path.isfile(srcfile):
            with open(f"{srcfile}", "r") as tmpFile:
                defcontents = tmpFile.read()
                tmpFile.close()
                
                print(defcontents)

                #if defcontents.find(find) == -1:
                defcontentsmodified = defcontents.replace(find, replacewith)

                with open(f"{srcfile}", "w") as tmpFile:
                    tmpFile.write(defcontentsmodified)
                    tmpFile.close()
                
        else:
            print("Provided Source File cannot be found:")
                        
    def fartbetween(self,srcfile: str, left: str, right: str, replacewith: str):
        if os.path.isfile(srcfile):
            with open(f"{srcfile}", "r") as tmpFile:
                defcontents = tmpFile.read()
                tmpFile.close()

                if defcontents.index(left) == -1:
                    return

                startIndex = defcontents.index(left) + len(left)
                endIndex = defcontents.index(right, startIndex)
                if endIndex == -1:
                    return

                midContents = defcontents[startIndex:endIndex]
                defcontentsmodified = defcontents.replace(f"{left}{midContents}{right}", f"{left}{replacewith}{right}")

                with open(f"{srcfile}", "w") as tmpFile:
                    tmpFile.write(defcontentsmodified)
                    tmpFile.close()
                    
    def getsoqldata(self,sfdxuser: str, soql: str):
        if sfdxuser is None or soql is None:
            return None

        result = subprocess.run([
            f"sfdx force:data:soql:query -u {sfdxuser} -q \"{soql}\" --json"], shell=True, capture_output=True)

        if result is None:
            return None

        jsonresult = json.loads(result.stdout)

        if jsonresult["result"]["totalSize"] == 1:
            print(jsonresult["result"]["records"][0][list(jsonresult["result"]["records"][0].keys())[1]])
            # we want the first key (1) after attributes(0). That is the first column and all we want
            return jsonresult["result"]["records"][0][list(jsonresult["result"]["records"][0].keys())[1]]

        # fallback
        return None


    def fartsoql(self, srcfile: str, find: str, sfdxaccesstoken: str, soql: str):
        replacewith = self.getsoqldata(sfdxaccesstoken, soql)
        if replacewith is None:
            return 
        self.fart(srcfile, find, replacewith)


    def fartsoqlbetween(self, srcfile: str, left: str, right: str, sfdxaccesstoken: str, soql: str):
        replacewith = self.getsoqldata(sfdxaccesstoken, soql)
        if replacewith is None:
            return
        self.fartbetween(srcfile, left, right, replacewith)