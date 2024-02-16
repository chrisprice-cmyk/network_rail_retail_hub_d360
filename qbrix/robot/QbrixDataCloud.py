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

    def create_data_stream(self, type, data_stream_name, source_name): #Type can be bundle, datakit, or package. will be use to determine the source of the datastream
        """Create a Data Stream if it does not already exist"""
        self.builtin.log_to_console(
            f"\nChecking if Data Streams have been setup for {data_stream_name}..."
        )
        deployment_completed = True
        query = ""
        lookup_size = 0
        if data_stream_name.lower() == "sales":
            query = "SELECT Id FROM DataStream Where Name LIKE 'Account%' LIMIT 1"
        elif data_stream_name.lower() == "service":
            query = "SELECT Id FROM DataStream Where Name LIKE 'Case%' LIMIT 1"
        elif data_stream_name.lower() == "flows":
            query = "SELECT Id FROM DataStream Where Name LIKE 'FlowRecord%' LIMIT 1"
        elif data_stream_name.lower() == "marketingsetup_general":
            query = "SELECT Id FROM DataStream Where Name LIKE 'Campaign%' LIMIT 1"
        elif data_stream_name.lower() == "smsaddon_general":
            query = "SELECT Id FROM DataStream Where Name LIKE 'MessagingChannel%' LIMIT 1"
        
        if data_stream_name != 'All':
            if query:
                datastream_lookup = self.salesforceapi.soql_query(query)
                lookup_size = datastream_lookup.get("totalSize", 0)
            else:
                self.builtin.log_to_console(f"\nWe can't determine if the DataStream ({data_stream_name}) provided is deployed. Please contact the administrator for support.")
                return

        if lookup_size > 0:
            datastream_id = datastream_lookup.get("records", {})[0].get("Id")
            self.builtin.log_to_console(f"\nDataStream Already Exists: {datastream_id}")
            return
        else:
            while deployment_completed:
                try:
                    self.builtin.log_to_console(
                        "\nDataStream Does Not Exist. Creating Data Stream..."
                    )
                    # Load DataStreams Page
                    self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/o/DataStream/home",timeout="30s")
                    self.shared.wait_for_page_to_load()
                    self.shared.clear_popups()

                    # Check for New Button (if not present then Data Cloud is not fully enabled)
                    if not self.shared.wait_on_element("ul.branding-actions >> a.forceActionLink:has-text('New')", 3):
                        self.builtin.log_to_console("\nData Cloud is not fully enabled or your user does not have permission to create Data Streams. Skipping this task.")
                        return

                    # Click New
                    self.shared.wait_and_click("ul.branding-actions >> a.forceActionLink:has-text('New')")

                    # Define Source (Source needs clicked twice sometimes)
                    self.builtin.log_to_console(f"\n -> Selecting Source: {source_name}")
                    if not self.shared.wait_on_element(f"h4:has-text('{source_name}')"):
                        self.builtin.log_to_console(
                            f"\n -X ERROR Failed to locate source name: {source_name}"
                        )
                        return
                    self.shared.wait_and_click(f"h4:has-text('{source_name}')")
                    # self.browser.click(f"h2:has-text('{source_name}')")
                    self.shared.wait_and_click("button.slds-button:has-text('Next')")
                    
                    if type == "bundle":

                        # Select Bundle
                        self.builtin.log_to_console(
                            f"\n -> Selecting Data Bundle: {data_stream_name} from source {source_name}"
                        )
                        self.shared.wait_and_click(
                            f"span.slds-visual-picker__figure >> span.slds-text-title:has-text('{data_stream_name}')"
                        )
                        sleep(3)
                        self.shared.wait_and_click("button.slds-button:has-text('Next')")

                        # Confirm Bundle Objects
                        self.shared.wait_on_element(
                            "button.slds-button:has-text('New Formula Field')"
                        )
                        self.builtin.log_to_console(
                            f"\n -> Accepting default object selection for Data Bundle: {data_stream_name}"
                        )
                        sleep(3)
                        self.shared.wait_and_click("button.slds-button:has-text('Next')")

                        # Confirm Configuration Details
                        self.shared.wait_on_element(
                            "div.slds-text-title_bold:has-text('Data Stream Bundle Configuration Details')"
                        )
                        self.builtin.log_to_console(
                            f"\n -> Confirming Deployment of Bundle: {data_stream_name}"
                        )
                        sleep(5)
                        self.shared.wait_and_click("button.slds-button:has-text('Deploy')")
                        sleep(3)
                        return
                        
                    elif type == "package":
                        
                        if not self.shared.wait_on_element(f"div.slds-tabs_default lightning-tab-bar li[data-tab-value='packages']"):
                            self.builtin.log_to_console(f"\n -X ERROR Failed to locate package tab")
                            return
                        self.shared.wait_and_click( f"div.slds-tabs_default lightning-tab-bar li[data-tab-value='packages']")
                        elements_to_count = "lightning-layout-item lightning-tab[aria-labelledby='packages__item'] ul li.slds-split-view__list-item"
                        
                        # self.builtin.log_to_console(f'ELEMENT COUNT -->{self.browser.get_element_count(elements_to_count)}')
                        if not self.shared.wait_on_element(elements_to_count, 20):
                            self.builtin.log_to_console(f"\n -X ERROR Failed to locate packages items to install")
                            return
                        number_of_packages = self.browser.get_element_count(elements_to_count)
                        self.builtin.log_to_console(f'Number of packages found: {number_of_packages}')
                        package = 1
                        datastream_count = 0
                        while package <= number_of_packages:
                            self.builtin.log_to_console(f'Processing ({package})')
                            # package_name = self.browser.get_text(f"{elements_to_count}:nth-child({package})")
                            package_name = self.browser.get_text(f"{elements_to_count}:nth-child({package}) a div span.slds-text-body_regular")
                            self.builtin.log_to_console(f'Processing ({package_name})')
                            self.shared.wait_and_click(f"{elements_to_count}:nth-child({package})")
                            
                            if not self.shared.wait_on_element(f"lightning-layout-item.detail table tbody tr"):
                                self.builtin.log_to_console(f"\n -X No Datastreams available to deploy for {package_name} package")
                                package += 1
                                continue
                            datastream_count += self.browser.get_element_count("lightning-layout-item.detail table tbody tr")
                            self.builtin.log_to_console(f'Number of datastreams found: {self.browser.get_element_count("lightning-layout-item.detail table tbody tr")}')
                            
                            
                            self.shared.wait_and_click("lightning-layout-item.detail table tbody tr:nth-child(1) lightning-primitive-cell-checkbox")
                            self.shared.wait_and_click("button.slds-button:has-text('Next')")

                            # Confirm Configuration Details
                            self.builtin.log_to_console(f"\n -> Accepting default object selection")
                            self.shared.wait_on_element( "div.slds-text-slds-nav-vertical__title:has-text('Objects to Configure')" )
                            self.shared.wait_and_click("button.slds-button:has-text('Next')")
                            
                            self.builtin.log_to_console(f"\n -> Confirming Deployment of DataStream Package")
                            self.shared.wait_on_element( "h1.slds-text-align_left:has-text('Data Streams to be Deployed')" )
                            self.shared.wait_and_click("button.slds-button:has-text('Deploy')")
                            sleep(3)
                            break
                            
                        self.builtin.log_to_console(f'Total Number of datastreams found: {datastream_count}')
                            
                        if datastream_count == 0:
                            return
                    else: # it is a datakit
                        return
                except Exception as e:
                    self.builtin.log_to_console(f'ERROR! we found an error when creating the Datastreams: {e}')
                    continue
                    

    def enable_einstein_segment_creation(self):
        """Enable Einstein Segment Creation"""
        retries = 0
        while(retries < 3):
            retries += 1
            self.shared.go_to_setup_admin_page("BetaFeaturesSetup/home")
            if self.browser.get_element_count("setup_cdp-beta-feature-row h2:has-text('Einstein Segment Creation')"):
                
                if self.browser.get_element_count("setup_cdp-beta-feature-row:has(h2:has-text('Einstein Segment Creation')) button.slds-not-selected"):
                    self.builtin.log_to_console("\n -> Found Enable Button")
                    if self.shared.wait_on_element("setup_cdp-beta-feature-row:has(h2:has-text('Einstein Segment Creation')) button.slds-button:has-text('Enable'):visible:enabled"):
                        self.shared.wait_and_click("setup_cdp-beta-feature-row:has(h2:has-text('Einstein Segment Creation')) button.slds-button:has-text('Enable'):visible:enabled")
                        self.shared.wait_and_click("lightning-modal-base lightning-button[data-tid='confirm-button']")
                        if self.shared.wait_on_element("div.toastContainer:has-text('Einstein Segment Creation was enabled')", 15):
                            self.builtin.log_to_console("\n -> Einstein Segment Creation Setting is NOW Enabled!")
                        return True
                else:
                    self.builtin.log_to_console("\n -> Einstein Segment Creation Setting is already active.")
            else:
                raise Exception("Einstein Segment Creation is not available for activation, please add the feature to this org and try to enable it again.")
            sleep(10)
        raise Exception("Einstein Segment Creation button couldn't be clicked, needs to be done manually.")
            
    def create_batch_segment(self, segment_name, segment_on):
        """Given Segment Name and where it will be on Creates a Segment"""
        # Load Sements Page
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/o/MarketSegment/home",timeout="30s")
        self.shared.wait_for_page_to_load()
        self.shared.clear_popups()
        
        # Click New
        self.browser.click("ul.branding-actions >> a.forceActionLink:has-text('New')")
        
        # How do you want to create your segment?
        # Check if Create segment using Einstein is available if not Einstein Segment creation is not fully Enable
        if not self.shared.wait_on_element("runtime_cdp-market-segment-creation-type-info-card input[data-tid='Use a Visual Builder']", 3):
            raise Exception("Einstein Segment Creation is not fully enabled or your user does not have permission to create Segments. Skipping this task.")
        
        self.shared.wait_and_click("runtime_cdp-market-segment-creation-type-info-card:has(input[data-tid='Use a Visual Builder']) label")
        self.shared.wait_and_click("runtime_cdp-market-segment-creation-type-info-card:has(input[data-tid='Batch Segment']) label")
        self.shared.wait_and_click("button.slds-button:has-text('Next')")
        
        # Define data space, segment membership and name
        self.shared.wait_and_click("lightning-combobox:has(label:has-text('Segment On')) div.slds-dropdown-trigger_click")
        self.shared.wait_and_click(f"lightning-combobox:has(label:has-text('Segment On')) div.slds-dropdown-trigger_click lightning-base-combobox-item:has-text('{segment_on}')")
        self.browser.fill_text("lightning-input:has(label:has-text('Segment Name')) input",segment_name)
        self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Next')")
        
        # Choose your segment's publish type and schedule.
        self.shared.wait_and_click("runtime_cdp-market-segment-publish-type-info-card:has(input[data-tid='Rapid Publish']) label")
        self.shared.wait_and_click("lightning-combobox:has(label:has-text('Publish Schedule')) div.slds-dropdown-trigger_click")
        self.shared.wait_and_click(f"lightning-combobox:has(label:has-text('Publish Schedule')) div.slds-dropdown-trigger_click lightning-base-combobox-item[data-value='NO_REFRESH']")
        
        # Save Segment
        self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Save')")
        self.shared.wait_on_element("div.toastContainer")
        
        toast_text = self.browser.get_text("div.toastContainer")
        if 'Your Segment was created successfully and will contain your complete population until filters are added' in toast_text:
            self.builtin.log_to_console(f"\n -> {toast_text}")
            
            if self.shared.wait_on_element("runtime_cdp-output-segment-status-lwc div[data-tid='status-value']:has-text('Active')"):
                self.builtin.log_to_console(f"\n -> Segment Status is now Active! Let's save it")
                
                self.shared.wait_and_click("lightning-button[data-tid='save-button'] button")
                
                if self.shared.wait_on_element("div.toastContainer:has-text('Save was successful and recount has been started')"):
                    self.builtin.log_to_console(f"\n -> Save was successful and recount has been started!")
        else:
            raise Exception(toast_text)