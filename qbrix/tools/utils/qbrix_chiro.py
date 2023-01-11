import json
import os
import re
import sys
import subprocess
import keyring
import hashlib
import shutil

from abc import abstractmethod

from cumulusci.core.config import ScratchOrgConfig
from cumulusci.tasks.command import Command
from cumulusci.core.exceptions import TaskOptionsError
from cumulusci.core.exceptions import CommandException
from cumulusci.core.keychain import BaseProjectKeychain


# class used to track os list as part of the process
class OmniScript:
    def __init__(self, type, subtype, language, id, updated=False):
        self.type = type
        self.subtype = subtype
        self.language = language
        self.id = id
        self.name = f"{type}{subtype}{language}".lower()
        self.disklocation = ""
        self.foldername = ""
        self.updated = updated


class OmniscriptAlign(Command):
    keychain_class = BaseProjectKeychain

    task_docs = """
    Repairs known issues with OmniScript LWC components. If you use these in your project, make sure this task is run before they are deployed.
    """

    task_options = {
        "org": {
            "description": "Value to replace every instance of the find value in the source file.",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(Command, self)._init_options(kwargs)

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

        if ("org" in self.options and not self.options["org"] is None) and self.keychain is None:
            self._load_keychain()
            self.logger.info("Org passed in but no keychain found in runtime")

        if not self.org_config.access_token is None:
            self.accesstoken = self.org_config.access_token

        if not self.org_config.instance_url is None:
            self.instanceurl = self.org_config.instance_url

    def _run_task(self):
        self._prepruntime()
        self.createworkingarea(self.accesstoken)
        self.retrievelwcs(self.accesstoken)

        targetnamespace = self.determinenamespace(self.accesstoken)
        oslist = self.getoslist(self.accesstoken, targetnamespace)

        if len(oslist) == 0 and targetnamespace != "omnistudio":
            oslist = self.getoslist(self.accesstoken, "omnistudio")

        if len(oslist) > 0:
            self.updatelwcsondisk(self.accesstoken, oslist)

        self.pushlwcs(self.accesstoken)

    def _handle_returncode(self, returncode, stderr):
        if returncode:
            message = "Return code: {}".format(returncode)
            if stderr:
                message += "\nstderr: {}".format(stderr.read().decode("utf-8"))
            self.logger.error(message)
            raise CommandException(message)

    def getqbrixdir(self, qbrixreponame: str):

        if (os.path.isdir(".qbrix") == False):
            os.mkdir(".qbrix")

        return f".qbrix/{qbrixreponame}"

    ###
    # Creates a starting sfdx working project directory to do the work in
    ###
    def createworkingarea(self, username: str):

        """Creates a temp working area on disk to update the lwc definitions."""

        hashname = hashlib.md5(username.encode()).hexdigest()
        qbrixtempdir = self.getqbrixdir(hashname)

        # whack any existing dir to get ensure latest is pulled
        if (os.path.isdir(qbrixtempdir)):
            shutil.rmtree(qbrixtempdir)

        subprocess.run([f"sfdx force:project:create --projectname {hashname} --json"], shell=True, capture_output=True,
                       cwd=".qbrix")

        subprocess.run([f"sfdx force:config:set defaultusername={username} --json"], shell=True, capture_output=True,
                       cwd=qbrixtempdir)

        subprocess.run([f"sfdx force:config:set instanceUrl={self.instanceurl} --json"], shell=True,
                       capture_output=True,
                       cwd=qbrixtempdir)

    ###
    # Download the compiled LWCs that are already in the org.
    ###
    def retrievelwcs(self, username: str):

        """Get all the LWCs locally to modify their contents."""

        try:

            hashname = hashlib.md5(username.encode()).hexdigest()
            qbrixtempdir = self.getqbrixdir(hashname)

            # now we need to inject a sfdx session and into the cci runtimee for that temp dir
            subprocess.run([
                               f"export SFDX_ACCESS_TOKEN='{self.accesstoken}' && sfdx force:auth:accesstoken:store --instanceurl {self.instanceurl} -a {hashname} --noprompt --json --loglevel DEBUG  && sfdx force:source:retrieve -u {hashname} -m LightningComponentBundle"],
                           shell=True, capture_output=True, cwd=qbrixtempdir)

        except BaseException as err:
            self.logger.error(f"Pull LWCs-> Unexpected {err}")

    def pushlwcs(self, username: str):

        """Push up the modified LWCs back up to the org."""

        try:

            hashname = hashlib.md5(username.encode()).hexdigest()
            qbrixtempdir = self.getqbrixdir(hashname)

            # now we need to inject a sfdx session and into the cci runtimee for that temp dir
            subprocess.run([f"sfdx force:source:deploy -u {hashname} -m LightningComponentBundle"], shell=True,
                           capture_output=True, cwd=qbrixtempdir)

        except BaseException as err:
            self.logger.error(f"Pull LWCs-> Unexpected {err}")

    ###
    #
    ###
    def getoslist(self, username: str, namespaceprefix: str):
        """Get the list of all OmniScripts to use for matching."""

        result = None

        hashname = hashlib.md5(username.encode()).hexdigest()
        qbrixtempdir = self.getqbrixdir(hashname)

        if namespaceprefix != "omnistudio":
            result = subprocess.run([
                f"sfdx force:data:soql:query -u {username} -q \"SELECT Id,Name,{namespaceprefix}__type__c,{namespaceprefix}__subtype__c,{namespaceprefix}__Language__c FROM {namespaceprefix}__Omniscript__c where {namespaceprefix}__IsActive__c=true and {namespaceprefix}__IsLwcEnabled__c=true and {namespaceprefix}__IsProcedure__c=false \" --json"],
                shell=True, capture_output=True, cwd=qbrixtempdir)

        else:
            result = subprocess.run([
                f"sfdx force:data:soql:query -u {username} -q \"SELECT Id,Name,Type,SubType,Language FROM OmniProcess  where IsActive=true and IsWebCompEnabled=true and IsTestProcedure=false \" --json"],
                shell=True, capture_output=True, cwd=qbrixtempdir)

        jsondata = json.loads(result.stdout)
        oslistdata = {}

        # todo: move out to seperate method
        for token in jsondata["result"]["records"]:
            if namespaceprefix != "omnistudio":

                try:
                    objectdata = OmniScript(token[f"{namespaceprefix}__Type__c"],
                                            token[f"{namespaceprefix}__SubType__c"],
                                            token[f"{namespaceprefix}__Language__c"], token["Id"])
                    oslistdata[objectdata.name] = objectdata
                except:
                    self.logger.error("Fail on getting the Industry metadata")

            else:
                try:
                    objectdata = OmniScript(token[f"Type"], token[f"SubType"],
                                            token[f"Language"], token["Id"])
                    oslistdata[objectdata.name] = objectdata
                except:
                    self.logger.error("Fail on getting the DPA metadata")

        return oslistdata

    ###
    #
    ###
    def determinenamespace(self, username: str):

        hashname = hashlib.md5(username.encode()).hexdigest()
        qbrixtempdir = self.getqbrixdir(hashname)

        result = subprocess.run([
            f"sfdx force:data:soql:query -u {username} -q \"SELECT NamespacePrefix FROM PackageLicense where NamespacePrefix in ('omnistudio','vlocity_cmt','vlocity_ps','vlocity_ins') LIMIT 1\" --json"],
            shell=True, capture_output=True, cwd=qbrixtempdir)

        if result is None: return "omnistudio"

        print(result.stdout)
        jsonresult = json.loads(result.stdout)

        if jsonresult["result"]["totalSize"] == 1:
            return jsonresult["result"]["records"][0]["NamespacePrefix"]

        # fallback
        return "omnistudio"

    def updatelwcsondisk(self, username: str, oslist):
        if oslist is None or len(oslist) == 0: return;
        try:

            hashname = hashlib.md5(username.encode()).hexdigest()
            qbrixtempdir = self.getqbrixdir(hashname)

            for i in os.listdir(f"{qbrixtempdir}/force-app/main/default/lwc"):
                if oslist.keys().__contains__(f"{i}".lower()):

                    oslist[f"{i}".lower()].disklocation = f"{qbrixtempdir}/force-app/main/default/lwc/{i}"
                    oslist[f"{i}".lower()].foldername = f"{i}"

                    try:
                        self.updateoslwcid(oslist[f"{i}".lower()])
                    except Exception as e:
                        self.logger.error(e)

        except Exception as e:
            self.logger.error(e)

        return oslist

    def updateoslwcid(self, omniscript: OmniScript):

        if isinstance(omniscript, OmniScript) and os.path.exists(
                f"{omniscript.disklocation}/{omniscript.foldername}_def.js"):

            with open(f"{omniscript.disklocation}/{omniscript.foldername}_def.js", "r") as tmpFile:
                defcontents = tmpFile.read()
                tmpFile.close()

                # ignore encoded chunk files.
                if defcontents.find("decodeURIComponent(atob(def))") == -1:
                    defcontentsmodified = defcontents.replace("export const OMNIDEF = ", "")

                    # trim off trailing \n if present to get a pure json def
                    if defcontentsmodified[len(defcontentsmodified) - 1] == "\n":
                        defcontentsmodified = defcontentsmodified.rstrip("\n")

                    # trim off trailing ; if present to get a pure json def
                    if defcontentsmodified[len(defcontentsmodified) - 1] == ";":
                        defcontentsmodified = defcontentsmodified.rstrip(";")

                    defjson = json.loads(defcontentsmodified)

                    try:

                        if defjson["sOmniScriptId"] != omniscript.id:
                            defjson["sOmniScriptId"] = omniscript.id
                            tmpdata = "export const OMNIDEF = " + json.dumps(defjson) + ";"

                            with open(f"{omniscript.disklocation}/{omniscript.foldername}_def.js", "w") as tmpFile:
                                tmpFile.write(tmpdata)
                                tmpFile.close()

                    except:
                        self.logger.error("fail on reading os def.js contents")
