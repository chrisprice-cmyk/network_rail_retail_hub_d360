import subprocess
import requests
from qbrix.tools.shared.qbrix_cci_tasks import run_cci_task
from qbrix.tools.shared.qbrix_project_tasks import check_and_update_setting
from qbrix.tools.shared.qbrix_console_utils import init_logger
from cumulusci.cli.utils import (get_cci_upgrade_command,
                                 get_installed_version,
                                 get_latest_final_version, timestamp_file)
from qbrix.tools.shared.qbrix_cci_tasks import run_cci_task


# Einstein Checks
def run_einstein_checks():
    # Check Bot Settings Exist in force-app folder
    check_and_update_setting(
        "force-app/main/default/settings/Bot.settings-meta.xml",
        "BotSettings",
        "enableBots",
        "true"
    )


# Experience Cloud Checks
def run_experience_cloud_checks():
    # Check Experience Cloud Settings Exist in force-app folder
    check_and_update_setting(
        "force-app/main/default/settings/Communities.settings-meta.xml",
        "CommunitiesSettings",
        "enableNetworksEnabled",
        "true"
    )
    check_and_update_setting(
        "force-app/main/default/settings/ExperienceBundle.settings-meta.xml",
        "ExperienceBundleSettings",
        "enableExperienceBundleMetadata",
        "true"
    )


def run_crm_analytics_checks(org_name):
    # Check that datasets are downloaded
    if org_name:
        run_cci_task("analytics_manager", org_name, mode="d", generate_metadata_desc=True)

def cumulusci_update_check():
    log = init_logger()
    log.info(" -> Checking for updates to CumulusCI")
    try:
        latest_version = get_latest_final_version()
    except requests.exceptions.RequestException:
        log.error("There was an issue retrieving the latest CumulusCI version. Skipping task")

    result = latest_version > get_installed_version()
    if result:
        try:
            subprocess.run(get_cci_upgrade_command(), shell=True, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as update_error:
            error_output = update_error.stderr.strip()
            log.error(" -X Error executing command to update CumulusCI: %s", error_output)

def update_salesforce_cli():
    log = init_logger()
    log.info(" -> Checking for salesforce CLI Updates")
    try:
        # Check if @salesforce/cli is installed globally
        subprocess.run(["npm", "list", "-g", "@salesforce/cli"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # If the command above completes without errors, @salesforce/cli is installed
        log.info("@salesforce/cli is installed. Updating...")
        subprocess.run(["npm", "install", "--global", "@salesforce/cli"], check=True)
    except subprocess.CalledProcessError:
        # If @salesforce/cli is not installed, run sfdx update
        log.info("@salesforce/cli is not installed. Running sfdx update...")
        # Uninstall sfdx-cli
        subprocess.run(["npm", "uninstall", "sfdx-cli", "--global"], check=True)
        # Install @salesforce/cli
        subprocess.run(["npm", "install", "@salesforce/cli", "--global"], check=True)

def check_python_library_dependencies():
    log = init_logger()
    log.info(" -> Checking for required QBrix Python libraries")
    run_cci_task("command", org_name=None, command="pip install --upgrade pandas pandasql robotframework-browser")

def check_and_update_nodejs():
    log = init_logger()
    try:
        # Check if Node.js is installed
        result = subprocess.run(["node", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        installed_version = result.stdout.strip().replace('v','')

        log.info(f" -> Node.js is installed. Installed version: {installed_version}")

        # Check the latest LTS version from the Node.js website
        latest_lts_version_cmd = subprocess.run(["npm", "view", "node", "dist-tags.lts"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        latest_lts_version = latest_lts_version_cmd.stdout.strip()

        log.info(f" -> Latest LTS version: {latest_lts_version}")

        if installed_version < latest_lts_version:
            log.info(" -> Updating Node.js to the latest LTS version...")
            subprocess.run(["npm", "install", "--global", f"node@{latest_lts_version}"], check=True)
            log.info(" -> Node.js updated successfully!")
        else:
            log.info(" -> Node.js is already on the latest LTS version.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log.info(" -> Node.js is not installed or an error occurred while checking/updating.")
