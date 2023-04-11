import base64
import glob
import gzip
import json
import math
import os
import subprocess
import json
import csv
import io
import requests
from abc import ABC
from pathlib import Path
import shlex
from time import sleep
from cumulusci.tasks.salesforce.BaseSalesforceApiTask import BaseSalesforceApiTask

from qbrix.tools.shared.qbrix_console_utils import init_logger

log = init_logger()


def cleanup_null_values(file_location):
    if not str(file_location).endswith(".json"):
        log.error(f"The file provided was not a json file. File Location: {file_location}")
        return

    with open(file_location, 'r') as f:
        data = json.load(f)

    if data is not None:
        for o in data["objects"][0]["fields"]:
            if "defaultValue" in o and "type" in o and o["type"] == "Numeric":
                o["defaultValue"] = "0" if o["defaultValue"].lower() == "null" else o["defaultValue"]

        with open(file_location, 'w') as f:
            json.dump(data, f)


def get_app_name(file_location):
    if not file_location:
        log.error("File was not passed. Skipping file")
        return None

    if not os.path.exists(file_location):
        log.error(f"The file provided doesn't exist or you do not have permissions to access it. File location: {file_location}")
        return None

    if not str(file_location).endswith(".wds-meta.xml"):
        log.debug(f"A file has been passed to an Analytics method, which is not in the expected file format (i.e. File Extension should be .wds-meta.xml). This method will continue to review the file although there may be unexpected results. Please check the file {file_location}")

    with open(file_location, 'r') as file:
        file.seek(0)
        file_data = file.read()

    start_pos = file_data.find("<application>") + len("<application>")
    end_pos = file_data.find("</application>")

    if start_pos > -1 and end_pos > -1:
        return file_data[start_pos:end_pos]
    else:
        return ""


class AnalyticsManager(BaseSalesforceApiTask, ABC):
    task_docs = """
    Q Brix Analytics Manager handles data which is contained within Analytics CRM Dataset Files. It downloads the data to csv files within the datasets/analytics folder.

    You can run the task in 3 modes by setting the 'mode' option to one of the following: \n
    Download (or d): Which Downloads and Cleans Up The Datasets (Note: You still need to download json files when you have uploaded your initial csv, see docs for notes) \n
    Upload (or u): Which Uploads the datasets \n
    Clean (or c): Which cleans existing files \n
    Share (or s): Which updates sharing for Analytics Apps in your force-app/main/default/wave directory \n
    """

    task_options = {
        "dataset_folder": {
            "description": "Path to folder which contains your analytics datasets. Defaults to datasets/analytics",
            "required": False
        },
        "mode": {
            "description": "(optional) Data Options are Download (d), Upload (u) or clean (c).",
            "required": False
        },
        "org": {
            "description": "(optional) Org Alias for target org when not running this task within a flow",
            "required": False
        },
        "share_to_all_internal_users": {
            "description": "(optional) If set to True, this will auto share the analytics apps to all internal users. Default False",
            "required": False
        },
        "share_to_all_portal_users": {
            "description": "(optional) If set to True, this will auto share the analytics apps to all portal/community users. Default False",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(AnalyticsManager, self)._init_options(kwargs)
        self.dataset_folder = self.options["dataset_folder"] if "dataset_folder" in self.options else "datasets/analytics"
        self.mode = self.options["mode"] if "mode" in self.options else "upload"
        self.share_to_all_internal_users = self.options["share_to_all_internal_users"] if "share_to_all_internal_users" in self.options else False
        self.share_to_all_portal_users = self.options["share_to_all_portal_users"] if "share_to_all_portal_users" in self.options else False

    def run_cleaners(self):
        wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
        for wave in wave_files:
            cleanup_null_values(wave)

    def download_datasets(self):
        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Analytics Folder Found. Skipping Dataset Download.")
            return

        wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

        self.logger.info("Starting Download of dataset files")

        if not os.path.exists(self.dataset_folder):
            self.logger.info("Creating Dataset Directory")
            os.makedirs(self.dataset_folder)

        org_datasets = self.get_datasets_from_org()

        for file in wave_dataset_files:
            dataset_name = Path(file).stem.replace(".wds-meta", "")

            if dataset_name in org_datasets:
                dataset_details = org_datasets.get(dataset_name)
                self.generate_csv_from_wave_dataset_version(dataset_details["id"], 'datasets/analytics', dataset_name, dataset_details["version"])
                self.logger.info(f"Dataset {dataset_name} has been downloaded to {self.dataset_folder}")
            else:
                self.logger.info(f"{dataset_name} is not present in the target org. Skipping.")

    def upload_dataset_data(self):
        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Source Analytics Folder Found at the expected location (force-app/main/default/wave). Skipping Dataset Deployment.")
            return

        if not os.path.exists(self.dataset_folder):
            log.debug(f"No Analytics Datasets Folder Found at expected location ({self.dataset_folder}). Skipping Dataset Deployment.")
            return

        self.run_cleaners()

        wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=True)

        if len(wave_dataset_files) > 0:
            for file in wave_dataset_files:
                dataset_name = Path(file).stem.replace(".wds-meta", "")
                data_file_location = f"{self.dataset_folder}/{dataset_name}.csv"
                app_name = get_app_name(file)

                if os.path.exists(data_file_location):
                    self.logger.info(f"Uploading {data_file_location}...")

                    if app_name != "":
                        self.logger.info(f"Dataset will be related to Analytics App: {app_name}")

                    related_json_file = f"{self.dataset_folder}/{dataset_name}.json"

                    try:
                        if os.path.exists(related_json_file):
                            self.logger.info(f"Dataset will use local json file: {related_json_file}")
                            self.upload_csv_to_external_data_part(data_file_location, dataset_name, related_json_file, app_name)
                        else:
                            self.upload_csv_to_external_data_part(data_file_location, dataset_name, {}, app_name)
                    except Exception as e:
                        self.logger.error(f"Upload Failed: {e}")

                else:
                    log.error(
                        f"Expected to find dataset file at {data_file_location} and it was missing. Please check you have downloaded the dataset data files. Skipping this file.")

    def create_insights_external_data(self, data_part_name, json_file=None, app_name=None):
        # Create the InsightsExternalData object
        insights_external_data = {
            "EdgemartLabel": data_part_name,
            "Format": "Csv",
            "EdgemartAlias": data_part_name,
            "Operation": "Overwrite",
            "NotificationSent": "Never",
            "FileName": "QBrixUploadFile"
        }

        if json_file:
            with open(json_file, "r") as json_file:
                json_data = json.load(json_file)

            metadata_json = base64.b64encode(json.dumps(json_data).encode("utf-8")).decode("ascii")

            insights_external_data.update({"MetadataJson": metadata_json})

        if app_name:
            insights_external_data.update({"EdgemartContainer": app_name})

        insights_external_data_id = self.sf.InsightsExternalData.create(insights_external_data)["id"]
        return insights_external_data_id

    def update_insights_external_data_action(self, insights_external_data_id):
        # Update the InsightsExternalData record
        self.sf.InsightsExternalData.update(insights_external_data_id, {"Action": "Process"})

    def upload_chunk_to_external_data_part(self, insights_external_data_id, chunk_data, part_number):
        # Convert the chunk data to a Base64-encoded string
        encoded_chunk_data = base64.b64encode(chunk_data).decode("ascii")

        # Create the InsightsExternalDataPart object
        insights_external_data_part = {
            "CompressedDataLength": len(chunk_data),
            "DataFile": encoded_chunk_data,
            "DataLength": len(chunk_data),
            "InsightsExternalDataId": insights_external_data_id,
            "PartNumber": part_number
        }
        insights_external_data_part_id = self.sf.InsightsExternalDataPart.create(insights_external_data_part)["id"]
        return insights_external_data_part_id

    def upload_csv_to_external_data_part(self, csv_file_path, data_part_name, json_file=None, app_name=None):
        chunk_size = 10000000  # 10MB

        # Create the InsightsExternalData object
        title_message = f"Creating Dataset Called: {data_part_name}"

        self.logger.info("=" * len(title_message))
        self.logger.info(f"Creating Dataset Upload Job for: {data_part_name}")
        self.logger.info("=" * len(title_message))
        insights_external_data_id = self.create_insights_external_data(data_part_name, json_file, app_name)
        self.logger.info(f"Upload Job created with ID: {insights_external_data_id}")

        # Compress the CSV file
        self.logger.info(f"Checking csv file: {csv_file_path}")
        with open(csv_file_path, "rb") as csv_file:
            csv_data = csv_file.read()
            compressed_csv_data = gzip.compress(csv_data)

        # Upload the compressed CSV data in chunks if it's larger than 10MB
        num_chunks = math.ceil(len(compressed_csv_data) / chunk_size)
        if num_chunks > 1:
            for i in range(num_chunks):
                start_index = i * chunk_size
                end_index = min((i + 1) * chunk_size, len(compressed_csv_data))
                chunk_data = compressed_csv_data[start_index:end_index]
                self.logger.info(f"Uploading Data (Chunk {i}/{num_chunks}) for: {data_part_name}")
                self.upload_chunk_to_external_data_part(insights_external_data_id, chunk_data, i + 1)
        else:
            self.logger.info(f"Uploading Data for: {data_part_name}")
            self.upload_chunk_to_external_data_part(insights_external_data_id, compressed_csv_data, 1)

        self.logger.info(f"Data Upload Complete! Starting Analytics Upload Processing for: {data_part_name}")
        self.update_insights_external_data_action(insights_external_data_id)

        while True:
            insights_external_data = self.sf.InsightsExternalData.get(insights_external_data_id)
            status = insights_external_data["Status"]
            status_message = insights_external_data["StatusMessage"]
            if status == "Completed" or status == "CompletedWithWarnings":
                break
            elif status in ["Aborted", "Failed"]:
                raise Exception(f"Job failed with status '{status}' and status message: {status_message}.")
            else:
                self.logger.info(f"Job status is '{status}'. Sleeping for 5 seconds...")
                sleep(5)

        self.logger.info("Upload Complete!")

    def remove_user_shares(self, folder_shares):
        # Use a list comprehension to filter out any shares with a shareType of "User"
        return [share for share in folder_shares if share.get("shareType") != "user"]
    
    def remove_unused_keys(self, folder_shares):
        # Use a list comprehension with a dictionary comprehension to remove any unused keys
        return [{key: share[key] for key in ("accessType", "shareType")} for share in folder_shares]

    def update_folder_sharing(self, folder_name):

        if not self.share_to_all_internal_users or not self.share_to_all_portal_users:
            self.logger.info("Running as Sharing Mode although no sharing specified. Check the options for the task.")
            return
        
        self.logger.info(f"Checking sharing settings for Analytics App: {folder_name}")

        # Query for the folder's ID based on its name
        folder_query = f"SELECT Id FROM Folder WHERE Name = '{folder_name}' and Type = 'Insights'"
        folder_id = self.sf.query(folder_query)["records"][0]["Id"]

        # Retrieve the metadata for the folder
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json"
        }
        endpoint = f"wave/folders/{folder_id}"
        response = self.sf.restful(endpoint, headers=headers, method="GET")

        folder_metadata = dict(response)
        folder_shares = []

        if response["shares"]:
            folder_shares = self.remove_user_shares(response["shares"])
            folder_shares = self.remove_unused_keys(folder_shares)
            
            if self.share_to_all_internal_users:
                if len([share for share in folder_shares if share.get("shareType") == "organization"]) < 1:
                    folder_shares.append({'accessType': 'manage', 'shareType': 'organization'})
                else:
                    self.logger.info("Application Already Shared with Organization")

            if self.share_to_all_portal_users:
                # Share to community users
                if len([share for share in folder_shares if share.get("shareType") == "allcspusers"]) < 1:
                    folder_shares.append({'accessType': 'view', 'shareType': 'allcspusers'})
                else:
                    self.logger.info("Application Already Shared with Community Users")

                # Share to Partner Community Users
                if len([share for share in folder_shares if share.get("shareType") == "allprmusers"]) < 1:
                    folder_shares.append({'accessType': 'view', 'shareType': 'allprmusers'})
                else:
                    self.logger.info("Application Already Shared with Partner Community Users")

        folder_metadata.update({"shares": folder_shares})

        body = {
            "shares": folder_shares,
        }

        self.sf.restful(
            endpoint,
            data=json.dumps({
              "shares": folder_shares
            }),
            method="PATCH",
        )

        self.logger.info(f"Sharing Updated for {folder_name}")

    def update_sharing_for_applications(self):
        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Source Analytics Folder Found at the expected location (force-app/main/default/wave). Skipping Dataset Deployment.")
            return

        wave_app_files = glob.glob("force-app/main/default/wave" + "/*.wapp-meta.xml", recursive=True)

        if len(wave_app_files) == 0:
            self.logger.info("No Wave Application Files found. Skipping.")
            return

        for app in wave_app_files:
            filename = os.path.basename(app)
            app_name = filename[:-len(".wapp-meta.xml")]
            self.update_folder_sharing(app_name)

    def generate_csv_from_wave_dataset_version(self, dataset_id, target_folder, target_filename, version_id=''):
        # get the requested datasetVersion
        dataset_version_endpoint = f'wave/datasets/{dataset_id}/versions/{version_id}'
        dataset_version = self.sf.restful(dataset_version_endpoint, method="GET")

        # get fields from dates
        fields_from_dates = [d["fields"] for d in dataset_version["xmdMain"]["dates"]]

        # filter out fields that are not in fields from dates
        field_names = []
        for dim in dataset_version["xmdMain"]["dimensions"]:
            if dim["field"]:        
                if dim["field"] not in fields_from_dates:
                    field_names.append(dim["field"])
        for measure in dataset_version["xmdMain"]["measures"]:
            if measure["field"]:
                if measure["field"] not in fields_from_dates:
                    field_names.append(measure["field"])

        # generate query string to load dataset and select specific fields
        select_clause = ", ".join(["'{}' as '{}'".format(f, f) for f in field_names])
        base_query = 'q = load "{}"; q = foreach q generate {};'.format(dataset_id+"/"+version_id, select_clause)
        base_query = base_query + ' q = limit q 1000000000;'

        # Clean Up List Field Names
        # field_names = [s.replace('.', '_').replace(' ', '_') for s in field_names]
        # field_names = list(set(field_names))

        # create output file
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        out_file = os.path.join(target_folder, target_filename + ".csv")

        # execute the query and stream the results to the input stream
        query_url = "{}wave/query".format(self.sf.base_url)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.sf.session_id)}
        query_params = {"query": base_query}

        query_response = requests.post(query_url, headers=headers, data=json.dumps(query_params))

        if query_response.status_code == 200:
            data = json.loads(query_response.content.decode('utf-8'))

            if data and data['results']['records']:
                with open(out_file, 'w', encoding='utf-8', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    for record in data['results']['records']:
                        writer.writerow(record)

        else:
            self.logger.error("Request Failed")
            self.logger.info(json.loads(query_response.content.decode('utf-8')))

        

    def get_datasets_from_org(self):

        # Retrieve the list of datasets
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json"
        }
        endpoint = f"wave/datasets/"
        response = self.sf.restful(endpoint, method="GET")

        org_dataset_dict = {}

        if response:
            for dataset_dict in list(response["datasets"]):


                
                dataset = dict(dataset_dict)
                dataset_version = dataset.get("currentVersionId")

                if not dataset_version:
                    dataset_version = ''

                org_dataset_dict.update({dataset["label"]: {"id": dataset["id"], "version": dataset_version}})


                # if dataset_name == "ClientTransactionsRB_Investments":

                #     self.generate_csv_from_wave_dataset_version(dataset_id, 'test_dir', dataset_name, dataset_version)
                #     self.logger.info(f"Data for {dataset_name} Downloaded!")

   
        return org_dataset_dict      


    def _run_task(self):
        self.logger.info("================================")
        self.logger.info("Starting QBrix Analytics Manager")
        self.logger.info("================================")

        if not self.mode or self.mode.lower() == "upload" or self.mode.lower() == "u":
            self.logger.info("Running in Upload Mode")
            self.upload_dataset_data()

        if self.mode.lower() == "download" or self.mode.lower() == "d":
            self.logger.info("Running in Download Mode")
            self.download_datasets()
            self.run_cleaners()

        if self.mode.lower() == "clean" or self.mode.lower() == "c":
            self.logger.info("Running in Clean Only Mode")
            self.run_cleaners()

        if self.mode.lower() == "share" or self.mode.lower() == "s":
            self.logger.info("Running in Sharing Mode")
            self.update_sharing_for_applications()

        if self.mode.lower() == "t":
            self.get_datasets_from_org()

        self.logger.info("=======================================")
        self.logger.info("Q Brix Manager has completed all tasks!")
        self.logger.info("=======================================")
