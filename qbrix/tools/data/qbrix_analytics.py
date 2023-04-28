import base64
import datetime
import glob
import gzip
import json
import math
import os
import re
import subprocess
import json
import csv
import io
import requests
from dateutil.parser import parse
from abc import ABC
from pathlib import Path
import shlex
from time import sleep
from cumulusci.tasks.salesforce.BaseSalesforceApiTask import BaseSalesforceApiTask
from datetime import datetime

from qbrix.tools.shared.qbrix_console_utils import init_logger
from qbrix.tools.shared.qbrix_project_tasks import replace_file_text

log = init_logger()


def cleanup_null_values(file_location: str = None):

    """
    Reviews json metadata description files and applies known fixes

    Args:
        file_location (str): The relative path to the .json file in the project.
    """

    if not file_location or not str(file_location).endswith(".json") or not os.path.exists(file_location):
        raise Exception(f"Error: Unable to read the provided file at {file_location}. Ensure it is a valid json file.")

    with open(file_location, 'r') as f:
        data = json.load(f)

    if data:
        for o in data["objects"][0]["fields"]:
            if "defaultValue" in o and "type" in o and o["type"] == "Numeric":
                o["defaultValue"] = "0" if o["defaultValue"].lower() == "null" else o["defaultValue"]

        with open(file_location, 'w') as f:
            json.dump(data, f)


def get_app_name(file_location: str = None):
    """
    Reads the Related Analytics Application Name from the project Dataset files

    Args:
        file_location (str): Relative Path to the dataset file within the project

    Returns:
        str: Application Name if found, otherwise None
    """
    if not file_location:
        log.error("File was not passed. Skipping file")
        return None

    if not os.path.exists(file_location):
        log.error(f"The file provided doesn't exist or you do not have permissions to access it. File location: {file_location}")
        return None

    if not str(file_location).endswith(".wds-meta.xml"):
        log.debug(f"A file has been passed to an Analytics method, which is not in the expected file format (i.e. File Extension should be .wds-meta.xml). This method will continue to review the file although there may be unexpected results. Please check the file {file_location}")
        return None

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
        },
        "generate_metadata_desc": {
            "description": "(optional) If set to True, this will auto-generate the metadata description file for datasets. Default False",
            "required": False
        },
    }

    def _init_options(self, kwargs):
        super(AnalyticsManager, self)._init_options(kwargs)
        self.dataset_folder = self.options["dataset_folder"] if "dataset_folder" in self.options else "datasets/analytics"
        self.mode = self.options["mode"] if "mode" in self.options else "upload"
        self.share_to_all_internal_users = self.options["share_to_all_internal_users"] if "share_to_all_internal_users" in self.options else False
        self.share_to_all_portal_users = self.options["share_to_all_portal_users"] if "share_to_all_portal_users" in self.options else False
        self.generate_metadata_desc = self.options["generate_metadata_desc"] if "generate_metadata_desc" in self.options else False

    def run_cleaners(self):
        wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
        for wave in wave_files:
            cleanup_null_values(wave)

    def get_dataset_name(self, dataset_file_path: str = None):
        if not dataset_file_path:
            return
        
        return Path(dataset_file_path).stem.replace(".wds-meta", "")

        with open(dataset_file_path, 'r') as dataset_file:
            xml_string = dataset_file.read()

        if xml_string:
            match = re.search(r'<masterLabel>(.*?)</masterLabel>', xml_string, re.DOTALL)
            if match:
                return match.group(1)
            else:
                return ""
        return None

    def download_datasets(self):
        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Analytics Folder Found. Skipping Dataset Download.")
            return

        wave_dataset_files = glob.glob("force-app/main/default/wave" + "/*.wds-meta.xml", recursive=False)

        self.logger.info("Starting Download of dataset files")

        if not os.path.exists(self.dataset_folder):
            self.logger.info("Creating Dataset Directory")
            os.makedirs(self.dataset_folder)

        org_datasets = self.get_datasets_from_org()

        for file in wave_dataset_files:
            dataset_name = Path(file).stem.replace(".wds-meta", "")

            # if dataset_name == 'Activity':
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
                dataset_name = self.get_dataset_name(file)
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

            json_bytes = json.dumps(json_data).encode('utf-8')

            metadata_json = base64.b64encode(json_bytes).decode('utf-8')

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
        """
        Remove any User specific shares
        """
        return [share for share in folder_shares if share.get("shareType") != "user"]
    
    def remove_unused_keys(self, folder_shares):
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

    def get_field_type(self, column):
        """
        Determines the field type for a given column.
        Returns "Text", "Numeric", or "Date".
        """

        values = [value for value in column if value.strip() != '']
    
        # Check if all non-blank values in the column are numeric
        is_numeric = all([value.replace('.', '', 1).isdigit() for value in values])
        if is_numeric:
            return "Numeric"
        
        # Check if all non-blank values in the column are dates
        # is_date = all([isinstance(value, datetime.date) for value in values])
        # if is_date:
        #     return "Date"
        
        # Otherwise, assume the field is text
        return "Text"
    
    def clean_field_name(self, field_name):
        # Clean Up List Field Names
        return field_name.replace('.', '_').replace(' ', '_')
    
    def remove_column_from_csv(self, column_to_remove, file_path):
        # set the name of the output file
        # get the file name from the file path
        file_name = os.path.basename(file_path)

        # add the prefix "output_" to the file name
        new_file_name = "output_" + file_name

        # create the new file path by joining the directory and the new file name
        output_file = os.path.join(os.path.dirname(file_path), new_file_name)

        # open the input and output files
        with open(file_path, "r") as infile, open(output_file, "w", newline="") as outfile:
            reader = csv.DictReader(infile)
            fieldnames = [field for field in reader.fieldnames if field != column_to_remove]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                del row[column_to_remove]
                writer.writerow(row)

        os.replace(output_file, file_path)

    def replace_partial_matches(self, file_path, search_string, replacement_string):
        search_words = re.split('[_.]', search_string)
        search_pattern = r"\b{}\b".format("[_.]".join(search_words))

        with open(file_path, 'r') as f:
            content = f.read()

        replaced_content, num_replacements = re.subn(search_pattern, replacement_string, content)

        if num_replacements > 0:
            with open(file_path, 'w') as f:
                f.write(replaced_content)

        return num_replacements

    def find_replace_column_name_indash(self, find_value, replace_value):
        wave_dashboard_files = glob.glob("force-app/main/default/wave" + "/*.wdash", recursive=True)

        for dash in wave_dashboard_files:

            # Find and Replace Exact Matches
            if not replace_file_text(file_location=dash, search_string=find_value, replacement_string=replace_value, show_info=True):

                if "_" in replace_value:
                    #self.logger.info(f"{find_value} was not found in Dashboard File {dash}. Running fuzzy match search to double check for other references.")
                    # Find and Replace Fuzzy Matches
                    self.replace_partial_matches(file_path=dash, search_string=replace_value, replacement_string=replace_value)
            else:
                #self.logger.info(f"{find_value} has been replaced with {replace_value} in Dashboard File {dash}")
                pass

    def get_date_format_string(self, input_string):
        if 'd' in input_string.lower():
            return "d"
        elif 'm' in input_string.lower():
            return "m"
        elif 'yyyy' in input_string.lower():
            return "Y"
        elif 'y' in input_string.lower():
            return "y"
        else:
            return None

    def get_correct_format_string(self, input_format):

        if '-' in input_format or '/' in input_format:
            date_format_sections = re.split('/|-', input_format)

            if '/' in input_format:
                separator = '/'
            elif '-' in input_format:
                separator = '-'

            if len(date_format_sections) == 3:
                return f"%{self.get_date_format_string(date_format_sections[0])}{separator}%{self.get_date_format_string(date_format_sections[1])}{separator}%{self.get_date_format_string(date_format_sections[2])}"
            else:
                self.logger.error(f"Unrecognised Input Format Passed to method: {input_format}")


    def generate_csv_from_wave_dataset_version(self, dataset_id, target_folder, target_filename, version_id=''):
        
        """
        Generates a local csv file from a dataset version
        """

        # Date Formats Accepted in Analytics
        default_format = 'yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\''
        formats = [
            'yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'',
            'yy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'',
            'yyyy-MM-dd\'T\'HH:mm:ss\'Z\'',
            'yy-MM-dd\'T\'HH:mm:ss\'Z\'',
            'yyyy-MM-dd HH:mm:ss',
            'yy-MM-dd HH:mm:ss',
            'dd.MM.yyyy HH:mm:ss',
            'dd.MM.yy HH:mm:ss',
            'dd/MM/yyyy HH:mm:ss',
            'dd/MM/yy HH:mm:ss',
            'dd/MM/yyyy hh:mm:ss a',
            'dd/MM/yy hh:mm:ss a',
            'dd-MM-yyyy HH:mm:ss',
            'dd-MM-yy HH:mm:ss',
            'dd-MM-yyyy hh:mm:ss a',
            'dd-MM-yy hh:mm:ss a',
            'MM/dd/yyyy hh:mm:ss a',
            'MM/dd/yy hh:mm:ss a',
            'MM-dd-yyyy hh:mm:ss a',
            'MM-dd-yy hh:mm:ss a',
            'HH:mm:ss dd/MM/yyyy',
            'HH:mm:ss dd/MM/yy'
        ]
        
        # Get the Dataset Version Information
        self.logger.info(f"Getting information for {target_filename} Dataset ID [{dataset_id}] version [{version_id}] (Note Version can be blank)")
        dataset_version = self.sf.restful(f'wave/datasets/{dataset_id}/versions/{version_id}', method="GET")

        if not dataset_version:
            raise Exception(f"No data was returned for dataset id {dataset_id}")

        # Get Fields for Query
        self.logger.info("Processing fields:")

        # Date Fields
        fields = []
        fields_from_dates = [d["fields"] for d in dataset_version["xmdMain"]["dates"]]

        date_fields = []
        fields_from_dates_list = []
        for field in fields_from_dates:
            for value in field.values():
                fields_from_dates_list.append(value)
                fields_from_dates_list.append(self.clean_field_name(value))

        # Process Date Fields
        date_fields_to_post_process = []
        for dfields in dataset_version["xmdMain"]["dates"]:

            date_field = dfields["fields"].get("fullField")
            date_field_label = dfields.get('label')

            if date_field:

                date_field_name = self.clean_field_name(date_field)

                self.logger.info(f"Date Field ({date_field}): Renamed to {date_field_name} with label {date_field_label}")
                date_fields.append(date_field)

                # Check Date Formatting
                date_field_formatting = dfields.get("format")
                if not date_field_formatting or date_field_formatting.replace("&#39;", "'") not in formats:
                    date_field_formatting = None
                else:
                    date_field_formatting = date_field_formatting.replace("&#39;", "'")

                # Generate Metadata for Field
                date_field_metadata = {
                    "fullyQualifiedName": date_field_name,
                    "name": date_field_name, 
                    "type": "Date", 
                    "label": date_field_label, 
                    "format": date_field_formatting
                    }
                if not date_field_formatting:
                    date_field_metadata.pop("format")
                    date_field_metadata.update({"type": "Text"})

                fields.append(date_field_metadata)             
                
 
        # Get Dimensions
        field_names = []
        dim_field_names = []
        field_names_from_measures = []
        for dim in dataset_version["xmdMain"]["dimensions"]:
            if dim.get("field"):        
                if dim["field"] not in fields_from_dates_list:

                    # Get Field Info and Update
                    clean_dim_field = self.clean_field_name(dim["field"])
                    dim_field = dim["field"]
                    dim_label = dim["label"]

                    dim_field_names.append(dim_field)

                    self.logger.info(f"Dimension: {dim_field} - Renamed to {clean_dim_field} with label {dim_label}")

                    fields.append({"fullyQualifiedName": clean_dim_field, "name": clean_dim_field, "type": "Text", "label": dim_label})

        # Get Measures
        for measure in dataset_version["xmdMain"]["measures"]:
            if measure.get("field"):
                if measure["field"] not in fields_from_dates_list and measure["field"] not in fields_from_dates:

                    # Get Measure Info and Update
                    clean_measure_field = self.clean_field_name(measure["field"])
                    measure_field = measure["field"]
                    measure_label = measure["label"]
                    decimal_places = measure["format"].get("decimalDigits", 0)

                    self.logger.info(f"Measure: {measure_field} - Renamed to {clean_measure_field} with label {measure_label}")

                    measure_field_metadata = {
                        "fullyQualifiedName": clean_measure_field,
                        "name": clean_measure_field,
                        "type": "Numeric",
                        "label": measure_label,
                        "precision": 18,
                        "defaultValue": "null",
                        "scale": decimal_places
                    }

                    if decimal_places and decimal_places > 0:
                        measure_field_metadata.update({"decimalSeparator": "."})

                    if decimal_places == 0:
                        measure_field_metadata.update({"format": "0"})

                    fields.append(measure_field_metadata)

                    field_names_from_measures.append(measure_field)

        field_names = date_fields + dim_field_names + field_names_from_measures

        self.logger.info(f"Querying {len(field_names)} fields related to the dataset.")

        # Build Query
        select_clause = ", ".join(["'{}' as '{}'".format(f, f) for f in field_names])
        base_query = 'q = load "{}"; q = foreach q generate {};'.format(dataset_id+"/"+version_id, select_clause)
        base_query = base_query + ' q = limit q 1000000000;'

        # Ensure CSV Output File Directory Exists
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        out_file = os.path.join(target_folder, target_filename + ".csv")

        # Run Query and download results
        query_url = "{}wave/query".format(self.sf.base_url)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.sf.session_id)}
        query_params = {"query": base_query}

        self.logger.info("Running Query against CRM Analytics for data")
        query_response = requests.post(query_url, headers=headers, data=json.dumps(query_params))

        if query_response.status_code != 200:
            self.logger.info(json.loads(query_response.content.decode('utf-8')))
            raise Exception("CRM Analytics Query Failed!")

        # Process Data Response
        self.logger.info("Processing Data")
        data = json.loads(query_response.content.decode('utf-8'))

        if not data and not data['results']['records']:
            raise Exception("Results were retrieved but not in the expected format.")

        self.logger.info(f"{len(data['results']['records'])} records retrieved")

        # Generate the Data File
        self.logger.info(f"Generating local CSV file at: {out_file}")
        with open(out_file, 'w', encoding='UTF-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for record in data['results']['records']:
                writer.writerow(record)

        # Generate Metadata File and Fix References
        self.logger.info(f"Reading {out_file} to generate metadata json file")
        field_types = {}
        with open(out_file,'r', encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

            if len(date_fields_to_post_process) > 0:
                for row in data:
                    for column_name, old_format in date_fields_to_post_process:
                        if column_name in row.keys():
                            old_value = row[column_name]
                            format_string = self.get_correct_format_string(old_format)
                            if len(old_value) > 0 and format_string:
                                new_value = datetime.strptime(old_value, format_string).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                                row[column_name] = new_value

            for row in reader:
                for key, value in row.items():
                    if key not in field_types:
                        field_types[key] = []
                        field_types[key].append(value)

        if len(date_fields_to_post_process) > 0:
            with open(out_file, mode='w', encoding='UTF-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(data)

        # Check Dashboard References
        self.logger.info("Checking that all references to fields in the dataset have been updated in the dashboard files")
        seen = set()
        for item in fields:
            self.find_replace_column_name_indash(f"\"name\":\"{item['label']}\"", f"\"name\":\"{item['name']}\"")
            if item['name'] in seen:
                fields.remove(item)
                self.remove_column_from_csv(item["label"], out_file)
            else:
                seen.add(item['name'])
            item["label"] = item["name"]

        # Write Metadata File
        metadata = {
        "fileFormat": {
            "charsetName": "UTF-8",
            "fieldsDelimitedBy": ",",
            "fieldsEnclosedBy": f"\"",
            "linesTerminatedBy": f"\r\n"
        },
        "objects": [
            {
                "connector": "CSV",
                "fullyQualifiedName": self.clean_field_name(target_filename + ".csv"),
                "label": target_filename + ".csv",
                "name": self.clean_field_name(target_filename + ".csv"),
                "fields": fields
            }]
        }

        if self.generate_metadata_desc:
            self.logger.info(f"Writing metadata file to {os.path.join(target_folder, target_filename + '.json')}")
            with open(os.path.join(target_folder, target_filename + ".json"), 'w', encoding='utf-8') as file:
                json.dump(metadata, file, indent=4)
        

    def get_datasets_from_org(self, endpoint = f"wave/datasets?pageSize=25", org_dataset_dict = {}):

        # Retrieve the list of datasets
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json"
        }

        response = self.sf.restful(endpoint, method="GET")

        if response and response.get("datasets"):
            for dataset_dict in list(response["datasets"]):
                
                dataset = dict(dataset_dict)
                dataset_version = dataset.get("currentVersionId")

                if not dataset_version:
                    dataset_version = ''

                org_dataset_dict.update({dataset["name"]: {"id": dataset["id"], "version": dataset_version}})

            if response["nextPageUrl"]:
                org_dataset_dict = self.get_datasets_from_org(response['nextPageUrl'].replace(f'/services/data/v56.0/', ''), org_dataset_dict)
   
        return org_dataset_dict      


    def _run_task(self):
        self.logger.info("=================================")
        self.logger.info("Starting QBrix Analytics Manager")
        self.logger.info("=================================")

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

        self.logger.info("=================================================")
        self.logger.info("Q Brix Analytics Manager has completed all tasks!")
        self.logger.info("=================================================")
