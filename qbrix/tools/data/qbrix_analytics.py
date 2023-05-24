import base64
import csv
import glob
import gzip
import io
import json
import math
import os
import re
from abc import ABC
from pathlib import Path
from time import sleep

import requests
from cumulusci.tasks.salesforce.BaseSalesforceApiTask import BaseSalesforceApiTask

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

        self.approved_formats = [
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
            'HH:mm:ss dd/MM/yy',
            'yyyy-MM-dd',
            'yyyy-M-d',
            'yy-MM-dd',
            'yy-M-d',
            'dd.MM.yyyy',
            'dd.MM.yy',
            'dd/MM/yyyy',
            'dd/MM/yy',
            'dd-MM-yyyy',
            'dd-MM-yy',
            'MM/dd/yyyy',
            'MM/dd/yy',
            'MM-dd-yyyy',
            'MM-dd-yy'
            'M-d-yy',
            'M-d-yyyy',
            'M/d/yyyy',
            'd-M-yy',
            'd-M-yyyy',
            'd/M/yy',
            'd/M/yyyy',
            'd.M.yy',
            'd.M.yyyy'
        ]

        self.derived_date_field_extensions = ["", "_day_epoch", "_sec_epoch", "_Second", "_Minute", "_Hour", "_Day", "_Week", "_Month", "_Quarter", "_Year"]

    def run_cleaners(self):
        wave_files = glob.glob(self.dataset_folder + "/*.json", recursive=True)
        for wave in wave_files:
            cleanup_null_values(wave)

    def get_dataset_name(self, dataset_file_path: str = None):
        if not dataset_file_path:
            return
        return Path(dataset_file_path).stem.replace(".wds-meta", "")

    def download_datasets(self):
        if not os.path.exists("force-app/main/default/wave"):
            log.debug("No Analytics Folder Found. Skipping Dataset Download.")
            return

        wave_dataset_files = glob.glob("force-app/main/default/wave/*.wds-meta.xml", recursive=False)

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

        wave_dataset_files = glob.glob("force-app/main/default/wave/*.wds-meta.xml", recursive=False)

        if len(wave_dataset_files) > 0:
            for file in wave_dataset_files:
                dataset_name = self.get_dataset_name(file)
                data_file_location = f"{self.dataset_folder}/{dataset_name}.csv"
                app_name = get_app_name(file)

                if os.path.exists(data_file_location) or os.path.exists(f"{data_file_location}__PART__1"):
                    self.logger.info(f"\nUploading Dataset: {dataset_name}")

                    large_file_mode = False
                    if os.path.exists(f"{data_file_location}__PART__1"):
                        self.logger.info(" -> Large File Mode Enabled")
                        large_file_mode = True

                    if app_name != "":
                        self.logger.info(f" -> Dataset will be related to Analytics App: {app_name}")

                    related_json_file = f"{self.dataset_folder}/{dataset_name}.json"

                    try:
                        if os.path.exists(related_json_file):
                            self.logger.info(f" -> Upload will use local json file: {related_json_file}")
                            self.upload_csv_to_external_data_part(data_file_location, dataset_name, related_json_file, app_name, large_file_mode)
                        else:
                            self.upload_csv_to_external_data_part(data_file_location, dataset_name, {}, app_name, large_file_mode)
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

    def read_large_csv_parts(self, directory, base_filename, file_mode='rb'):
        """
        Read in all the parts of a large CSV file that has been split into parts.

        The filename should include "__PART__" and an incrementing number.
        """

        # Initialize a buffer to store the combined data
        combined_data_buffer = io.StringIO()

        # Initialize a writer to write the combined data to the buffer
        writer = csv.writer(combined_data_buffer, quoting=csv.QUOTE_NONNUMERIC)

        # Loop over the files in the directory
        for filename in os.listdir(directory):
            if filename.startswith(base_filename) and filename.endswith('__PART__1'):
                # Open the first part file for reading
                with open(os.path.join(directory, filename), 'rb') as f:
                    # Read the contents of the file as bytes and decode to a string
                    file_data = f.read().decode('utf-8')

                    # Create a reader for the decoded string
                    reader = csv.reader(file_data.splitlines())

                    # Read the header row
                    header = next(reader)
                    writer.writerow(header)

                    # Write the data from the first part file to the combined data buffer
                    for row in reader:
                        writer.writerow(row)

                    # Loop over the remaining part files and write their data to the combined data buffer
                    for part_num in range(2, 1000):
                        part_filename = f'{base_filename}__PART__{part_num}'
                        if part_filename in os.listdir(directory):
                            with open(os.path.join(directory, part_filename), 'rb') as f:
                                # Read the contents of the file as bytes and decode to a string
                                file_data = f.read().decode('utf-8')

                                # Create a reader for the decoded string
                                reader = csv.reader(file_data.splitlines())
                                next(reader)  # Skip the header row
                                for row in reader:
                                    writer.writerow(row)
                        else:
                            break

        # Get the contents of the combined data buffer
        combined_data_str = combined_data_buffer.getvalue()

        # Convert the string to bytes if the file mode is 'rb'
        if file_mode == 'rb':
            combined_data_bytes = combined_data_str.encode('utf-8')
            return combined_data_bytes
        else:
            return combined_data_str

    def upload_csv_to_external_data_part(self, csv_file_path, data_part_name, json_file=None, app_name=None, large_file=False):
        chunk_size = 10000000  # 10MB

        # Create the InsightsExternalData object
        insights_external_data_id = self.create_insights_external_data(data_part_name, json_file, app_name)
        self.logger.info(f" -> Upload Job created with ID: {insights_external_data_id}")

        # Compress the CSV file
        self.logger.info(f" -> Checking csv file: {csv_file_path}")
        csv_data = None

        if large_file:
            self.logger.info(" -> Combining File Chunks")
            csv_data = self.read_large_csv_parts(os.path.join("datasets", "analytics"), os.path.basename(csv_file_path))
        else:
            with open(csv_file_path, "rb") as csv_file:
                csv_data = csv_file.read()

        if not csv_data:
            print(csv_data)
            raise Exception(f"Unable to read CSV File. {csv_file_path}")

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

        wave_app_files = glob.glob("force-app/main/default/wave/*.wapp-meta.xml", recursive=False)

        if len(wave_app_files) == 0:
            self.logger.info("No Wave Application Files found. Skipping.")
            return

        for app in wave_app_files:
            filename = os.path.basename(app)
            app_name = filename[:-len(".wapp-meta.xml")]
            self.update_folder_sharing(app_name)

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

    def update_references_in_wave_files(self, find_value, replace_value, include_fuzzy=True):
        if find_value == replace_value:
            return

        wave_dashboard_files = glob.glob("force-app/main/default/wave/*.wdash", recursive=False)
        for dash in wave_dashboard_files:
            # print(f"\nChecking {dash}")

            # Load Dashboard JSON
            with open(dash, 'r') as json_file:
                data = json.load(json_file)

            update_made = False

            if data:
                # Check and Update FieldNames
                # print(f"\nChecking Data sources")
                data_sources = data["dataSourceLinks"]
                for data_source in data_sources:
                    fields = data_source.get("fields")
                    if fields:
                        for f in fields:
                            if f["fieldName"] == find_value:
                                # print(f" -> Found Reference to {find_value}, replacing with {replace_value}")
                                f["fieldName"] = replace_value
                                update_made = True

                # Check Filters
                # print(f"\nChecking Filters")
                filters = data.get("filters")
                if filters:
                    for dashboard_filter in filters:
                        if dashboard_filter.get("fields") and find_value in dashboard_filter.get("fields"):
                            # print(f" -> Found Reference to {find_value}, replacing with {replace_value}")
                            dashboard_filter["fields"] = [s.replace(find_value, replace_value) for s in list(dashboard_filter.get("fields"))]
                            update_made = True

                # Check and Update Query Step References
                # print(f"\nChecking Step Queries")
                steps = data.get("steps")
                if steps:
                    for s in dict(steps).values():
                        if s.get("query") and isinstance(s.get("query"), str):
                            # print(f" -> Found Reference to {find_value}, replacing with {replace_value}")
                            s["query"] = s["query"].replace(find_value, replace_value)
                            update_made = True
                        if s.get("query") and isinstance(s.get("query"), dict) and s["query"].get("query"):
                            # print(s.get("query"))
                            # print(f" -> Found Reference to {find_value}, replacing with {replace_value}")
                            s["query"]["query"] = s["query"].get("query").replace(find_value, replace_value)
                            update_made = True

                # Check and Update Widgets References
                # print(f"\nChecking Widgets")
                widgets = data.get("widgets")
                if widgets:
                    for w in dict(widgets).values():
                        if w.get("parameters") and w["parameters"].get("measureField") and w["parameters"].get("measureField") == find_value:
                            # print(f" -> Found Reference to {find_value}, replacing with {replace_value}")
                            w["parameters"]["measureField"] = replace_value
                            update_made = True

                if update_made:
                    with open(dash, 'w') as json_file:
                        json.dump(data, json_file)

        wave_xmd_files = glob.glob("force-app/main/default/wave/*.xmd-meta.xml", recursive=False)
        for xmd in wave_xmd_files:
            replace_file_text(file_location=xmd, search_string=f"{find_value}</field>", replacement_string=f"{replace_value}</field>", show_info=False)

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

        # Get the Current Dataset Version Data
        self.logger.info(f"Getting information for {target_filename} Dataset ID [{dataset_id}] version [{version_id}] (Note Version can be blank)")
        dataset_version = self.sf.restful(f'wave/datasets/{dataset_id}/versions/{version_id}', method="GET")

        if not dataset_version:
            raise Exception(f"No data was returned for dataset id {dataset_id}")

        # Capture Created Date for Time Shift
        if dataset_version.get("createdDate"):
            with open(os.path.join(target_folder, target_filename + ".txt"), 'w', encoding='utf-8') as qbrix_data_file:
                qbrix_data_file.write(dataset_version["createdDate"])

        # Get Fields from Org
        self.logger.info("\nGATHERING FIELD DATA")
        fields = []
        before_after_field_list = []

        # Date Fields
        self.logger.info("\nGathering Date Fields:")
        date_fields = []
        fields_from_dates_list = []
        for date_fields_dict in dataset_version["xmdMain"]["dates"]:
            date_field = date_fields_dict["fields"].get("fullField")
            date_field_label = date_fields_dict.get('label')
            date_field_formatting = date_fields_dict.get("format")

            if date_field:
                # Add Field to Query Fields in Original Format
                date_fields.append(date_field)

                # Clean Up Field Name for new CSV Dataset
                date_field_name = self.clean_field_name(date_field)
                before_after_field_list.append((date_field, date_field_name))

                # Add catch for weird spacing only on date fields
                updated_date_field = re.sub(r'(?<=[a-z])([A-Z])', r'_\1', date_field)

                # Generate Metadata Description for Field
                date_field_metadata = {
                    "fullyQualifiedName": date_field_name,
                    "name": date_field_name,
                    "type": "Date",
                    "label": date_field_label,
                    "isSystemField": False,
                    "isUniqueId": False,
                    "isMultiValue": False,
                }

                # Add Field and Derived Variations to Exclusion List
                for d in self.derived_date_field_extensions:
                    fields_from_dates_list.append(f"{date_field}{d}")
                    before_after_field_list.append((f"{updated_date_field}{d}", f"{date_field}{d}"))

                if not date_field_formatting:
                    date_field_metadata.update({"format": "yyyy-MM-dd HH:mm:ss"})
                else:
                    clean_date_format = date_field_formatting.replace("&#39;", "'")
                    date_field_metadata.update({"format": clean_date_format})

                # Adjust Offset
                if date_fields_dict.get("fiscalMonthOffset"):
                    date_field_metadata.update({"fiscalMonthOffset": date_fields_dict.get("fiscalMonthOffset")})

                fields.append(date_field_metadata)

                self.logger.info(f" -> Processed Date Field ({date_field}): Renamed to {date_field_name} with label {date_field_label}")

        # Get Dimensions Fields
        self.logger.info("\nGathering Dimension Fields:")
        dimension_field_names = []
        for dimension_dict in dataset_version["xmdMain"]["dimensions"]:
            if dimension_dict.get("field"):
                # Get Dimension Field Information
                dimension_field_name = dimension_dict["field"]
                dimension_field_label = dimension_dict["label"]

                # Check that Dimension is not in excluded date field list
                if dimension_field_name in fields_from_dates_list:
                    self.logger.debug(f" -> SKIPPED: {dimension_field_name} - Found Field in Date Exclusion List")
                    continue
                else:
                    # Add to Query Fields in original Format
                    dimension_field_names.append(dimension_field_name)

                    # Generate Metadata Field Description
                    clean_dimension_field_name = self.clean_field_name(dimension_field_name)
                    before_after_field_list.append((dimension_field_name, clean_dimension_field_name))

                    fields.append({
                        "fullyQualifiedName": clean_dimension_field_name,
                        "name": clean_dimension_field_name,
                        "type": "Text",
                        "label": dimension_field_label,
                        "isMultiValue": False,
                        "isSystemField": False
                    })

                    self.logger.info(f" -> Processed Dimension Field ({dimension_field_name}): Renamed to {clean_dimension_field_name} with label {dimension_field_label}")

        # Get Measures
        self.logger.info("\nGathering Measure Fields:")
        measure_field_names = []
        for measure_dict in dataset_version["xmdMain"]["measures"]:
            if measure_dict.get("field"):
                # Get Measure Field Information
                measure_field_name = measure_dict["field"]
                measure_field_label = measure_dict["label"]
                decimal_places = measure_dict["format"].get("decimalDigits", 0)

                # Check to Ensure Measure is not in date field exclusion list
                if measure_field_name in fields_from_dates_list:
                    self.logger.debug(f" -> SKIPPED: {measure_field_name} - Found Field in Date Exclusion List")
                    continue
                else:
                    # Add field to Query fields in original format
                    measure_field_names.append(measure_field_name)

                    # Generate Metadata for Field
                    clean_measure_field_name = self.clean_field_name(measure_field_name)
                    before_after_field_list.append((measure_field_name, clean_measure_field_name))

                    measure_field_metadata = {
                        "fullyQualifiedName": clean_measure_field_name,
                        "name": clean_measure_field_name,
                        "type": "Numeric",
                        "label": measure_field_label,
                        "precision": 18,
                        "defaultValue": "null",
                        "scale": decimal_places,
                        "isMultiValue": False,
                        "isSystemField": False
                    }

                    if decimal_places > 0:
                        measure_field_metadata.update({"decimalSeparator": "."})

                    if decimal_places == 0:
                        measure_field_metadata.update({"format": "0"})

                    fields.append(measure_field_metadata)

                    self.logger.info(f" -> Measure: {measure_field_name} - Renamed to {clean_measure_field_name} with label {measure_field_label}")

        # Combine Field Names into single list for Query
        field_names = date_fields + dimension_field_names + measure_field_names

        self.logger.info("\nGenerating CRM Analytics Query")

        # Build Query
        select_clause = ", ".join(["'{}' as '{}'".format(f, f) for f in field_names])
        base_query = 'q = load "{}"; q = foreach q generate {};'.format(dataset_id + "/" + version_id, select_clause)
        # base_query = base_query + 'q = offset q 0; q = limit q 100000;'

        # self.logger.info(f"Generated Query:\n{base_query}")

        # Ensure CSV Output File Directory Exists
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        dataset_csv_output_file = os.path.join(target_folder, target_filename + ".csv")

        # Run Query and download results
        query_url = "{}wave/query".format(self.sf.base_url)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(self.sf.session_id)}

        # self.logger.info("\nRunning Query against CRM Analytics for data")

        # query_response = requests.post(query_url, headers=headers, data=json.dumps(query_params))

        # Generate the Dataset Data File
        self.logger.info(f"\nGenerating local CSV file at: {dataset_csv_output_file}")
        row_count = 0
        with open(dataset_csv_output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            # Download the data in batches of 100,000 records
            batch_count = 1
            for offset in range(0, 5000000, 100000):
                self.logger.info(f" -> Downloading Batch {batch_count} containing rows {offset} to {batch_count * 100000}")

                # Add the limit and offset parameters to the SOQL query
                paged_query = f'{base_query} q = offset q {offset}; q = limit q 100000;'
                query_params = {"query": paged_query}

                # Make a POST request to the Wave query endpoint with the modified query
                response = requests.post(query_url, headers=headers, data=json.dumps(query_params))
                data = json.loads(response.content.decode('utf-8'))

                if 'results' in data:
                    for row in data['results']['records']:
                        writer.writerow(row)
                        row_count += 1
                    if len(data['results']['records']) < 100000:
                        break
                else:
                    self.logger.info(" -> No More Results to Process")
                    break

                batch_count += 1

        self.logger.info(f" -> Loaded {row_count} rows into csv")

        # Check Dashboard References
        self.logger.info("\nRunning Check to update old field references in Wave metadata:")
        for original_field, updated_field in before_after_field_list:
            self.update_references_in_wave_files(original_field, updated_field, False)

        seen = set()
        for item in fields:
            if item['name'] in seen:
                fields.remove(item)
                self.remove_column_from_csv(item["label"], dataset_csv_output_file)
            else:
                seen.add(item['name'])
            item["label"] = item["name"]
        self.logger.info("\nCheck Complete!")

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
            self.logger.info(f"\nWriting metadata file to {os.path.join(target_folder, target_filename + '.json')}")
            with open(os.path.join(target_folder, target_filename + ".json"), 'w', encoding='utf-8') as file:
                json.dump(metadata, file, indent=4)

        self.process_large_csv_files("datasets/analytics")

    def get_datasets_from_org(self, endpoint=f"wave/datasets?pageSize=25", org_dataset_dict=None):
        """
        Get List of all Datasets in target org
        """

        # Retrieve the list of datasets
        if org_dataset_dict is None:
            org_dataset_dict = {}

        response = self.sf.restful(endpoint, method="GET")

        if response and response.get("datasets"):
            for dataset_dict in list(response["datasets"]):
                dataset = dict(dataset_dict)
                dataset_version = dataset.get("currentVersionId")

                if not dataset_version:
                    dataset_version = ''

                org_dataset_dict.update({dataset["name"]: {"id": dataset["id"], "version": dataset_version}})

            if response["nextPageUrl"]:
                org_dataset_dict = self.get_datasets_from_org(response['nextPageUrl'].replace(f'/services/data/v{self.project_config.project__package__api_version}/', ''), org_dataset_dict)

        return org_dataset_dict

    def process_large_csv_files(self, directory):
        """
        Check a directory for CSV files over 99MB and split them into parts.

        Each part should have the same file name with "__PART__" and an incrementing number as the file name.
        """
        self.logger.info("\n Checking File Sizes")
        # Set the maximum file size (in bytes) for each split file
        max_file_size = 99000000

        # Loop over the files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                filepath = os.path.join(directory, filename)

                # Get the size of the file in bytes
                file_size = os.path.getsize(filepath)

                # If the file is over the maximum size, split it into parts
                if file_size > max_file_size:
                    print(f' -> Splitting {filename} into parts...')

                    # Open the original CSV file for reading
                    with open(filepath, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)

                        # Read the header row
                        header = next(reader)

                        # Initialize variables for tracking the current file size and split file number
                        current_file_size = 0
                        file_num = 1

                        # Open the first split file for writing
                        out_file = open(f'{filepath}__PART__{file_num}', 'w', newline='', encoding='utf-8')
                        writer = csv.writer(out_file)

                        # Write the header row to the first split file
                        writer.writerow(header)

                        # Loop over the rows in the original CSV file
                        for row in reader:
                            # Calculate the size of the current row in bytes
                            row_size = len(','.join(row).encode('utf-8'))

                            # If adding the current row would exceed the maximum file size, close the current file and open a new one
                            if current_file_size + row_size > max_file_size:
                                out_file.close()
                                file_num += 1
                                out_file = open(f'{filepath}__PART__{file_num}', 'w', newline='', encoding='utf-8')
                                writer = csv.writer(out_file)
                                writer.writerow(header)
                                current_file_size = 0

                            # Write the current row to the current split file
                            writer.writerow(row)
                            current_file_size += row_size

                        # Close the last split file
                        out_file.close()

                        print(f' -> Split {filename} into {file_num} parts.')

                        os.remove(filepath)
                else:
                    print(f' -> Skipping {filename}. File size is {file_size / 1000000:.2f} MB.')

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
            self.process_large_csv_files("datasets/analytics")

        self.logger.info("=================================================")
        self.logger.info("Q Brix Analytics Manager has completed all tasks!")
        self.logger.info("=================================================")
