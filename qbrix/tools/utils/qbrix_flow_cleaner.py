from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from abc import ABC
import os
import re
import subprocess


class PurgeInactiveFlows(BaseSalesforceApiTask, ABC):
    task_docs = """
    Every time we deploy a flow to an org, it will create a new version of the flow (if it already exists),
    Means if we kept deploying the same QBrix (flows) to the same org, it will keep creating new versions and, soon enough, will get the "reached max version number" error.
    So this task is to purge the flows in the org to prevent this issue.
    For each flow, we will keep 1 version and remove all others:
        - if there is an active version, we keep the active version
        - if there is no active version, we keed the latest version
    We will only purge the flows that we deploy in our QBrix because we don't want to step on other's toes,
        - but we can do if you really want, by setting purge_all_flow to true
    Also, if you want to be sure/safe, you can set ask_before_remove to true so it will ask you to confirm before removing for each flow
    """

    task_options = {
        "purge_all_flow": {
            "description": "If true, then we will purge all flows in the org, rather than just the flows defined in my qbrix",
            "required": False,
        },
        "ask_before_remove": {
            "description": "If true, then we will purge all flows in the org, rather than just the flows defined in my qbrix",
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super(PurgeInactiveFlows, self)._init_options(kwargs)

        # default false
        self.purge_all_flow = True if "purge_all_flow" in self.options and self.options["purge_all_flow"].lower() == "true" else False

        # default false
        self.ask_before_remove = True if "ask_before_remove" in self.options and self.options["ask_before_remove"].lower() == "true" else False


    # try to find all folders that contains flow metadata
    def _get_all_flow_folders(self, base_folder):
        my_folders = []

        if os.path.exists("force-app/main/default/flows"):
            my_folders.append("force-app/main/default/flows")

        unpackaged_path = os.path.join(base_folder,"unpackaged")
        if not os.path.exists(unpackaged_path):
            return my_folders

        for one_unpackaged_folder in os.listdir(unpackaged_path):
            metadata_path = os.path.join(unpackaged_path,one_unpackaged_folder)
            for one_metadata_folder in metadata_path:
                if one_metadata_folder == "flows":
                    my_folders.append(f"unpackaged/{one_unpackaged_folder}/flows")

        return my_folders


    def _run_task(self):

        my_sf_tooling_api = self.tooling

        apiname_filter = ""

        # if not purge_all_flow, let's try to find all flow api names defined in my qbrix, so when we query flows, we only need the ones exist in our qbrix
        if not self.purge_all_flow:
            my_flow_apinames = set()
            flow_folders = self._get_all_flow_folders("./")
            # loop through every folder that might contains flow
            for one_flow_folder in flow_folders:
                #then loop through every file in that folder
                for one_file in os.listdir(one_flow_folder):
                    if one_file.endswith(".flow-meta.xml"):
                        my_flow_apinames.add(re.sub(r'\.flow-meta\.xml$',"",one_file))
            # if not purge_all_flow but no flows found in my qbrix, no need to proceed, let's just return
            if not len(my_flow_apinames):
                print("no flow found in this qbrix, no need to proceed purging flow")
                return
            apiname_filter = f" AND Definition.DeveloperName IN ({str(my_flow_apinames)[1:-1]}) "

        # with this query, we are getting all version of all flows if their status is "Active" or "Obsolete" (deactived), also we filter out the templates and the ones from managed package
        my_query = f"SELECT Id, Definition.DeveloperName, DefinitionId, VersionNumber, Status FROM Flow WHERE Status IN ('Active', 'Obsolete') AND IsTemplate = False AND ManageableState = 'unmanaged' {apiname_filter} ORDER BY Definition.DeveloperName, Status, VersionNumber DESC "

        found_flows = my_sf_tooling_api.query(my_query)

        if not found_flows["totalSize"]:
            print("no flows found")
            return

        # now, let's group these flow versions by flow definition, because we want to keep 1 version per definition
        group_flows = {}
        for one_flow in found_flows["records"]:
            # create key in group_flows if flow definition not found, give default values
            if not one_flow["DefinitionId"] in group_flows:
                group_flows[one_flow["DefinitionId"]] = {
                    "hasActive": False,
                    "name": one_flow['Definition']['DeveloperName'],
                    "flows": []
                }
            # it's possible that there is no active version for a certain flow definition, so let's figure out,
            if one_flow["Status"] == "Active":
                group_flows[one_flow["DefinitionId"]]["hasActive"] = True
            group_flows[one_flow["DefinitionId"]]["flows"].append(one_flow)

        total_versions_deleted = 0
        total_versions_failed_deleting = 0
        total_flow_processed = 0


        # it's possible at this moment, we don't have authentication info in sfdx yet, let's login in sfdx if it's not yet
        try:
            # run command to show our user info
            command = f"sf org display user -o {self.org_config.username}"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            output, error = process.communicate()
            # if no output, probably means not logged in in sfdx yet, let's do the login
            if not output:
                print("sfdx auth info not found, let's login")
                command = f"export SF_ACCESS_TOKEN='{self.org_config.access_token}' && sf org login access-token --instance-url {self.org_config.instance_url} --no-prompt --json"
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                output, error = process.communicate()
        except Exception as e:
            print(f"****\n!!FAILED login -- {e}")
    
        # then, loop through the groups
        for defId in group_flows:
            one_flow_group = group_flows[defId]
            # if there is only 1 version of this flow group (flow definition), we just simply keep it, no need to proceed.
            if len(one_flow_group["flows"]) <= 1:
                # print(f"----\nflow {one_flow_group['name']} has only 1 version, no need to purge")
                continue
            
            # if the option said "let's ask before remove", then we will ask per flow definition to make sure user does want to remove, if not, skip this group
            if self.ask_before_remove and input(f"Would you like to proceed removing {len(one_flow_group['flows']) - 1} versions of flow {one_flow_group['name']}? (Y/n)").lower() == "n":
                continue

            # finally, it's time to remove
            print(f"----\nremoving inactive versions of flow {one_flow_group['name']}")
            idx = 0
            num_deleted = 0
            num_failed = 0
            # loop throw each version of the flow
            for one_flow in one_flow_group["flows"]:
                # if the group has active version, only remove the Obsolete version,
                # or if the group does not have active version, remove all except the first one in list (the latest version)
                if (one_flow_group["hasActive"] and one_flow["Status"] == "Obsolete") or (not one_flow_group["hasActive"] and idx != 0):
                    try:
                        command = f"sf data delete record -s Flow -i {one_flow['Id']} -t -o {self.org_config.username}"
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
                        output, error = process.communicate()
                        # this command is strange, even if it succeed, it still sends an error says "Deleting Record... Success",
                        if error and not error.startswith('Deleting Record... Success'):
                            print(f"****\n!!FAILED DELETING FLOW {one_flow_group['name']}/{one_flow['Id']}: {error}")
                            num_failed += 1
                        else:
                            print(f"Successfully deleted flow: {one_flow_group['name']}/{one_flow['Id']} version {one_flow['VersionNumber']}")
                            num_deleted += 1
                    except Exception as e:
                        print(f"****\n!!FAILED DELETING FLOW {one_flow_group['name']}/{one_flow['Id']} -- {e}")
                idx += 1
            if num_deleted or num_failed:
                print(f"{num_deleted} versions deleted for flow {one_flow_group['name']}")
                total_versions_deleted += num_deleted
                total_versions_failed_deleting += num_failed
                total_flow_processed += 1
        
        if total_flow_processed:
            print(f"{total_flow_processed} flows processed, {total_versions_deleted} versions deleted in total, {total_versions_failed_deleting} versions failed deleting")

  