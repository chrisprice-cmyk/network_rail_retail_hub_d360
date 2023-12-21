import json
import os
import time
from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixDataCloud(QbrixRobotTask):

    """Keywords for Data Cloud"""

    def enable_data_cloud(self, wait_for_completion=False):
        """Load Setup Page and ensure that Data Cloud is enabled"""

        # Ensure Permission Set is applied
        self.assign_data_cloud_permission()

        # Load Setup Page
        self.shared.go_to_setup_admin_page("CdpEnablement/home")
        self.builtin.log_to_console("\nLoaded Data Cloud Setup Page")

        # Click Getting Started if visible
        if (
            self.browser.get_element_count("button.slds-button:has-text('Get Started')")
            == 1
        ):
            self.builtin.log_to_console("\nData Cloud Not Enabled...")
            self.browser.click("button.slds-button:has-text('Get Started')")

            if wait_for_completion:
                self.builtin.log_to_console(
                    "\nWaiting on Data Cloud Setup... (This could take 15-20 minutes)"
                )
                timeout = 0
                timeout_reached = True
                while timeout < 1200:
                    if (
                        self.browser.get_element_count(
                            "div.location:has-text('Your instance is located on')"
                        )
                        == 1
                    ):
                        timeout_reached = False
                        self.builtin.log_to_console("\nSetup Complete!")
                        break
                    timeout += 1
                    self.builtin.log_to_console(
                        f"\nWaiting...{timeout} / 1200 seconds (20 Min)..."
                    )
                    sleep(1)

                if timeout_reached:
                    self.builtin.log_to_console(
                        "\nTimeout reached for Data Cloud Setup. Please check your org configuration."
                    )
                    return
            else:
                self.builtin.log_to_console(
                    "\nSetup has been started but may take 15-20 minutes. Robot has chosen not to wait and is moving onto the next task (if any)"
                )
                return

        self.builtin.log_to_console("\nData Cloud Enabled!")

    def assign_data_cloud_permission(self):
        """Assigns the Data Cloud Admin Permission Set to the current user"""
        self.builtin.log_to_console(
            "\nChecking that the current user has permissions for Data Cloud."
        )
        self.cumulusci.run_task(
            task_name="assign_permission_sets", api_names="GenieAdmin"
        )

    def create_data_stream(self, name, data_bundle_name, source_name):
        """Create a Data Stream if it does not already exist"""

        self.builtin.log_to_console("\nChecking if datastream exists...")

        query = ""
        if data_bundle_name.lower() == "sales":
            query = "SELECT Id FROM DataStream Where Name LIKE 'Account%' LIMIT 1"
        elif data_bundle_name.lower() == "service":
            query = "SELECT Id FROM DataStream Where Name LIKE 'Case%' LIMIT 1"
        datastream_lookup = self.salesforceapi.soql_query(query)

        if datastream_lookup.get("totalSize", 0) > 0:
            datastream_id = datastream_lookup.get("records", {})[0].get("Id")
            self.builtin.log_to_console(f"\nDataStream Already Exists: {datastream_id}")
        else:
            self.builtin.log_to_console(
                f"\nDataStream Does Not Exist. Creating Data Stream..."
            )

            # Load DataStreams Page
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/o/DataStream/home",
                timeout="30s",
            )

            # Click New
            self.shared.wait_and_click(
                "ul.branding-actions >> a.forceActionLink:has-text('New')"
            )

            # Define Settings
            self.shared.wait_and_click(f"h2:has-text('{source_name}')")
            self.browser.click("button.slds-button:has-text('Next')")

            # Salesforce CRM Settings
            self.shared.wait_and_click(
                f"span.slds-visual-picker__figure >> span.slds-text-title:has-text('{data_bundle_name}')"
            )
            sleep(1)
            self.browser.click("button.slds-button:has-text('Next')")
            self.shared.wait_and_click("button.slds-button:has-text('Next')")
            self.shared.wait_and_click("button.slds-button:has-text('Next')")
            self.shared.wait_and_click("button.slds-button:has-text('Deploy')")
            sleep(3)
