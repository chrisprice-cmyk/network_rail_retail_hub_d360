import json
import os
from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask
from qbrix.robot.QbrixToolingKeywords import QbrixToolingKeywords
from Browser.utils.data_types import SelectionType
from qbrix.tools.shared.qbrix_authentication import (
    generate_mfa_code,
    get_secure_setting,
)


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixMarketingKeywords(QbrixRobotTask):

    """Marketing Cloud Keywords for Robot"""

    def __init__(self):
        super().__init__()
        self._toolinglibrary = None

    @property
    def toolinglibrary(self):
        """Loads Q Robot Shared Keywords and Methods"""

        if self._toolinglibrary is None:
            self._toolinglibrary = QbrixToolingKeywords()
        return self._toolinglibrary

    def enable_pardot_setting(self):
        """Enables Pardot Setting"""
        self.builtin.log_to_console("\nEnable Pardot Setting")
        self.shared.go_to_setup_admin_page("PardotSetupAssistant/home")
        self.browser.wait_for_elements_state(
            "div:text-is('B2B Marketing Setup Assistant')", ElementState.visible, "15s"
        )
        self.builtin.log_to_console("\n -> Loaded Pardot Setup Page")
        self.builtin.log_to_console("\n -> Checking setting...")
        self.browser.click(".slds-button:has-text('Send Your First Email')")
        self.browser.wait_for_elements_state(
            "span:text-is('Complete the required steps to send your first Account Engagement email.')",
            ElementState.visible,
            "15s",
        )
        checked = "checked" in self.browser.get_element_states(
            ":nth-match(span.slds-checkbox_faux,1)"
        )
        if not checked:
            self.builtin.log_to_console(
                "\n -> Setting not enabled. Clicking toggle now..."
            )
            self.browser.click(":nth-match(span.slds-checkbox_faux,1)")
            sleep(1)
        self.builtin.log_to_console("\n -> Setting Enabled!")

    def enable_pardot_app(self):
        """Enables Pardot Connected App Settings"""
        self.builtin.log_to_console(
            "\nEnable admin permissions for the Pardot Connected App..."
        )
        self.toolinglibrary.enable_admin_auth_for_connected_app("b2bma_canvas")

    def create_pardot_template(self):
        """Enables Demo Configuration of Pardot Email Templates"""
        self.builtin.log_to_console(
            "\nCreating Demo Configuration of Pardot Email Templates"
        )
        self.browser.go_to(
            f"{self.cumulusci.org.instance_url}/lightning/o/EmailTemplate/home"
        )
        self.browser.wait_for_elements_state(
            "a:has-text('New Email Template')", ElementState.visible, "30s"
        )
        self.builtin.log_to_console("\n -> Loaded Email Templates Page")
        self.browser.click("a:has-text('All Email Templates')")
        sleep(5)

        self.builtin.log_to_console("\n -> Checking for demo Email Template...")
        visible = "visible" in self.browser.get_element_states(
            ".slds-table:has-text('Annual Customer Conference Invitation')"
        )
        if not visible:
            self.builtin.log_to_console("\n -> Template not found. Creating...")
            self.browser.click("a:has-text('New Email Template')")
            self.browser.wait_for_elements_state(
                "h2:has-text('New Email Template')", ElementState.visible, "30s"
            )
            self.browser.fill_text(
                ".forcePageBlockItem:has-text('Email Template Name') >> input",
                "Annual Customer Conference Invitation",
            )
            self.browser.fill_text(
                ".forcePageBlockItem:has-text('Description') >> input",
                "Pardot - Annual Customer Conference Invitation",
            )
            self.browser.fill_text(
                ".forcePageBlockItem:has-text('Subject') >> input",
                "Join us for our annual conference",
            )
            self.browser.click("button[title='Save']")
            sleep(5)
        self.builtin.log_to_console("\n -> Template Configured!")

    def enable_territory_management(self):
        """Enables Maps Territory Planning Settings"""
        self.builtin.log_to_console("\nEnabling Maps Territory Planning...")
        self.shared.go_to_setup_admin_page("Territory2Settings/home")
        sleep(5)
        self.builtin.log_to_console(
            "\n -> Territory Settings Page Loaded. Checking to see if setting is enabled..."
        )
        visible = "visible" in self.browser.get_element_states(
            ":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')"
        )
        if visible:
            self.builtin.log_to_console(
                "\n -> Setting not enabled. Enabling setting now..."
            )
            button_to_click = self.browser.get_element(
                ":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')"
            )
            self.browser.click(button_to_click)
            sleep(1)
        self.builtin.log_to_console("\n -> Setting Enabled!")

    def connect_to_marketing_cloud_distributed_marketing(
        self,
        marketing_cloud_username=None,
        marketing_cloud_password=None,
        marketing_cloud_secret=None,
        business_unit_label=None,
    ):
        """Configures the Distributed Marketing connection in a target Salesforce Org. This Assumes that the package has already been installed.

        Args:
            marketing_cloud_username (str): Name of Secure Setting from Q Labs for the username
            marketing_cloud_password (str): Name of the Secure Settings from Q Labs for the Marketing Cloud Password
            marketing_cloud_secret (str): Name of the secure setting from Q Labs for the MFA Seed Key
            business_unit_label (str): Name you want to use for the Business Unit Connection Name. Defaults to Distributed Marketing.

        All parameters will default to the Distributed Marketing Demo instance defaults if not overridden.
        """

        self.builtin.log_to_console(
            "\nConnecting Marketing Cloud -> Distributed Marketing..."
        )

        # Use Default Creds if None are supplied
        if not marketing_cloud_username:
            marketing_cloud_username = get_secure_setting("Q__DM_MARKETING_CLOUD_UUN")
        else:
            marketing_cloud_username = get_secure_setting(marketing_cloud_username)

        if not marketing_cloud_password:
            marketing_cloud_password = get_secure_setting("Q__DM_MARKETING_CLOUD_PASS")
        else:
            marketing_cloud_password = get_secure_setting(marketing_cloud_password)

        if not marketing_cloud_secret:
            marketing_cloud_secret = get_secure_setting("Q__DM_MARKETING_CLOUD_SEED")
        else:
            marketing_cloud_secret = get_secure_setting(marketing_cloud_secret)

        if not business_unit_label:
            business_unit_label = "Distributed Marketing"

        self.builtin.log_to_console("\n -> Running with these parameters:")
        self.builtin.log_to_console(f"\n -> Username: {marketing_cloud_username}")
        self.builtin.log_to_console(f"\n -> Business Unit: {business_unit_label}")
        self.builtin.log_to_console("\n -> Note: Password and secret remain hidden.")

        # Go To Admin Page
        self.shared.go_to_app("Sales")
        self.browser.go_to(
            f"{self.cumulusci.org.instance_url}/lightning/n/mcdm_15__Distributed_Marketing_Administration",
            timeout="30s",
        )
        self.browser.wait_until_network_is_idle("15s")
        self.builtin.log_to_console("\n -> Loaded Sales Configuration Page")

        # Check if Already Connected
        self.builtin.log_to_console(
            "\n -> Checking if already connected and enabled..."
        )
        count = 0
        while count <= 20:
            if (
                self.browser.get_element_count(
                    "p:has-text('No connected business units'):visible"
                )
                == 1
            ):
                break
            if (
                self.browser.get_element_count("table >> tr") >= 1
                and self.browser.get_element_count(
                    f"table >> tr:has-text('{business_unit_label}')"
                )
                == 0
            ):
                break
            if (
                self.browser.get_element_count(
                    f"table >> tr:has-text('{business_unit_label}')"
                )
                >= 1
            ):
                self.builtin.log_to_console("\nAlready Connected")
                return
            count += 1
            sleep(1)

        # Create Distributed Marketing Business Unit
        self.builtin.log_to_console("\n -> Creating Business Unit...")
        self.shared.wait_and_click(
            f"{self.shared.iframe_handler()} a.slds-button:text-is('Add Business Unit')"
        )

        # Enter Name for Connection
        self.browser.wait_for_elements_state(
            "iframe >>> div.step-container:has-text('Business Unit Display Name')",
            ElementState.visible,
            "20s",
        )
        self.browser.fill_text(
            "iframe >>> div.step-container:has-text('Business Unit Display Name') >> input[type='text']",
            "Distributed Marketing",
        )
        self.browser.click("iframe >>> input.btn[value='Get Started']")

        # Enter Marketing Cloud Username
        self.browser.wait_for_elements_state(
            "iframe >>> div.step-container:has-text('Marketing Cloud Username')",
            ElementState.visible,
            "20s",
        )
        self.browser.fill_text(
            "iframe >>> div.step-container:has-text('Marketing Cloud Username') >> input[type='text']",
            marketing_cloud_username,
        )
        self.browser.click(
            "iframe >>> div.step-container:has-text('Marketing Cloud Username') >> :nth-match(input.btn[value='Next'], 1)"
        )

        # Auto-Generate Connection Records
        sleep(3)
        self.browser.click(
            "iframe >>> div.step-container:has-text('Create the authentication settings records.') >> :nth-match(input.btn[value='Next'], 1)"
        )
        sleep(3)
        self.browser.click(
            "iframe >>> div.step-container:has-text('create the remote site settings, authentication provider, and named credential record.') >> :nth-match(input.btn[value='Next'], 1)"
        )

        # Login To Marketing Cloud
        self.builtin.log_to_console("\n -> Logging into Marketing Cloud...")
        self.browser.click("iframe >>> a:text-is('Log In')")
        sleep(1)
        original_page = self.browser.switch_page("NEW")
        self.browser.fill_text("input[id='username']", marketing_cloud_username)
        self.browser.click("input[id='submit-btn']")
        sleep(1)
        self.browser.fill_text("input[id='password']", marketing_cloud_password)
        self.browser.click("input[id='submit-btn']")
        sleep(2)
        if (
            self.browser.get_element_count(
                "p:text-is('Use Salesforce Authenticator to approve the request.'):visible"
            )
            > 0
        ):
            self.browser.click("button:text-is('Didn't receive a notification?')")
            sleep(2)
        if (
            self.browser.get_element_count(
                "div.slds-form-element__control >> input[type='text']"
            )
            > 0
        ):
            self.browser.fill_text(
                "div.slds-form-element__control >> input[type='text']",
                generate_mfa_code(marketing_cloud_secret),
            )
            self.browser.click("button:has-text('Verify')")
        else:
            raise Exception("No input found for MFA code.")

        # Switch Back to Setup
        self.builtin.log_to_console("\n -> Finalising Configuration")
        sleep(3)
        self.browser.switch_page(original_page)
        self.browser.go_to(
            f"{self.cumulusci.org.instance_url}/lightning/n/mcdm_15__Distributed_Marketing_Administration",
            timeout="30s",
        )
        self.browser.wait_for_elements_state(
            "button.slds-button:has-text('Update Connection Information')",
            ElementState.visible,
            "20s",
        )

        # Wait for Connected Status
        self.builtin.log_to_console("\n -> Waiting for connection to complete...")
        retry_count = 0
        while retry_count <= 5:
            self.browser.click(
                "button.slds-button:has-text('Update Connection Information')"
            )
            sleep(10)
            if (
                self.browser.get_element_count(
                    "table >> tr:has-text('Distributed Marketing') >> td.cellContainer:has-text('Connected')"
                )
                == 1
            ):
                self.builtin.log_to_console("\n -> Connected!")
                break
            retry_count += 1

    def connect_campaigns_for_distributed_marketing(self, file_path):
        """Connects a given list of Campaigns to the Related Journeys in Marketing Cloud"""

        if not os.path.exists(file_path):
            raise ValueError("File Path does not exist.")

        self.builtin.log_to_console("\nConnecting Campaigns for Distributed Marketing")

        with open(file_path, encoding="utf-8", mode="r") as config_file:
            config_data = json.load(config_file)

        campaigns = config_data["campaignsToLink"]

        self.builtin.log_to_console("\n -> Campaigns to link:")
        self.builtin.log_to_console(f"\n -> {campaigns}")

        if len(campaigns) == 0:
            raise Exception("No campaigns defined in config file.")

        self.shared.go_to_app("Distributed Marketing")
        self.builtin.log_to_console("\n -> Opened Distributed Marketing App")
        campaign_ids = [campaign["campaignExId"] for campaign in campaigns]
        campaigns_dict = {
            campaign["campaignExId"]: campaign["journeyName"] for campaign in campaigns
        }

        # Get Campaign Record Information
        self.builtin.log_to_console("\n -> Getting Campaign Information")
        campaign_ids_list = ", ".join([f"'{id_}'" for id_ in campaign_ids])
        campaign_lookup = self.salesforceapi.soql_query(
            f"SELECT Id, Name, External_ID__c FROM Campaign WHERE External_ID__c IN ({campaign_ids_list})"
        )
        print(campaign_lookup)

        # Loop Through Records
        self.builtin.log_to_console("\n -> Configuring Campaigns...")
        if campaign_lookup["totalSize"] > 0:
            for campaign in campaign_lookup["records"]:
                self.builtin.log_to_console(
                    f"\n -> Configuring Campaign with ID: {campaign['Id']}..."
                )

                # Open The Campaign record Page
                self.browser.go_to(
                    f"{self.cumulusci.org.instance_url}/lightning/r/Campaign/{campaign['Id']}/view",
                    timeout="90s",
                )
                self.browser.wait_until_network_is_idle("30s")

                journey = campaigns_dict.get(campaign["External_ID__c"], None)
                print(journey)
                if not journey:
                    self.builtin.log_to_console("\nNo journey found for External ID")
                    continue

                # Click The Connect Campaign Button if Present
                self.browser.wait_for_elements_state(
                    "span:text-is('Campaign Messages')", ElementState.visible, "20s"
                )
                sleep(5)
                if (
                    self.browser.get_element_count("button:text-is('Connect Campaign')")
                    > 0
                ):
                    self.builtin.log_to_console("\n -> Connecting Campaign...")
                    self.browser.click("button:text-is('Connect Campaign')")
                    self.shared.wait_and_click(
                        "input.uiInputTextForAutocomplete[placeholder='Search for a journey']"
                    )
                    self.browser.fill_text(
                        "input.uiInputTextForAutocomplete[placeholder='Search for a journey']",
                        journey,
                    )
                    sleep(5)
                    self.shared.wait_and_click(
                        f"div.listContent >> ul >> li.lookup__item >> :nth-match(a:has-text('{journey}'), 1)"
                    )
                    sleep(3)
                    self.shared.wait_and_click(
                        "div.modal-footer >> button:text-is('Save')"
                    )
                    sleep(5)
                    self.browser.go_to(
                        f"{self.cumulusci.org.instance_url}/lightning/r/Campaign/{campaign['Id']}/view",
                        timeout="90s",
                    )
                    self.browser.wait_until_network_is_idle("30s")
                self.builtin.log_to_console("\n -> Campaign Configured")

    def go_to_quick_send_page(self):
        """Enables Quick Sends for Distributed Marketing Demos"""

        self.browser.go_to(
            f"{self.cumulusci.org.instance_url}/lightning/n/mcdm_15__Distributed_Marketing_Administration",
            timeout="30s",
        )
        self.browser.wait_until_network_is_idle("30s")
        self.shared.wait_and_click("a.slds-nav-vertical__action:text-is('Quick Send')")
        self.browser.wait_until_network_is_idle("30s")
        self.browser.wait_for_elements_state(
            "button[title='Enable the selected journeys for Quick Send']",
            ElementState.visible,
            "30s",
        )

        self.builtin.log_to_console("\n -> Loaded Quick Send Configuration Page")

    def enable_option_for_quick_send(self, option=None):
        """Assumes you are on the Quick Send Configuration page and have already connected Marketing Cloud. Add Options you want to select for Quick Send from the availiable journeys list."""

        self.builtin.log_to_console(f"\nEnabling Option [{option}] for Quick Send")

        if option:
            if option in self.browser.get_select_options(
                ":nth-match(select.journey-select,2)"
            ):
                self.builtin.log_to_console("\nAlready selected option")
                return

            if (
                len(
                    self.browser.select_options_by(
                        ":nth-match(select.journey-select,1)",
                        SelectAttribute.label,
                        option,
                    )
                )
                > 0
            ):
                self.shared.wait_and_click(
                    "button[title='Enable the selected journeys for Quick Send']"
                )
                self.shared.wait_and_click("button:text-is('Apply Changes')")
                sleep(5)
                self.builtin.log_to_console("\n -> Enabled")
            else:
                self.builtin.log_to_console(
                    f"\nOption [{option}] was not found in the select. Skipping"
                )
        else:
            self.builtin.log_to_console("\nNo option was provided. Skipping")

    def check_and_enable_uma_marketing_cloud(self):
        """Enables Marketing Cloud Unified Marketing Automation Setting"""
        self.builtin.log_to_console("\nEnabling the marketing cloud setting for Unified Marketing Automation")
        retries = 0
        while retries < 5:
            retries += 1
            self.shared.go_to_setup_admin_page("UnifiedMarketingGettingStarted/home", force_reload= True)
            sleep(3)
            if "visible" not in self.browser.get_element_states("lightning-button[data-id='umaEnableButton'] button.slds-button:has-text('Enable Marketing Cloud'):disabled"):
                self.builtin.log_to_console("\n -> Found Button")
                self.shared.wait_and_click("lightning-button[data-id='umaEnableButton'] button.slds-button:has-text('Enable Marketing Cloud')")
                break
            elif self.browser.get_element_count("setup_marketing_unifiedmarketing-uma-enablement-expandable-step div.slds-progress-ring__content") > 0: 
                self.builtin.log_to_console("Marketing Cloud activation is in process")
                break
            else:
                self.builtin.log_to_console(f"Button didn't load, we are retrying the activation: {retries}")     
                sleep(3)           
            
        if self.shared.wait_on_element("setup_marketing_unifiedmarketing-uma-enablement-expandable-step:nth-child(1) div.slds-progress-ring__content span.slds-icon-utility-success", 240):
            self.builtin.log_to_console("Marketing Cloud was enabled successfully.")
                
            
    def create_identity_resolution(self, ir_name): 
        """Create an Identity Resolution"""
        
        self.builtin.log_to_console(f"\nCreate an Identity Resolution...")
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/o/IdentityResolution/home", timeout="30s")
        self.shared.wait_for_page_to_load()
        self.shared.clear_popups()
        # self.shared.wait_on_element(".slds-page-header--object-home a.forceActionLink:has-text('New')")
            
        self.shared.wait_and_click("div.slds-page-header--object-home a.forceActionLink:has-text('New')")
        self.shared.wait_on_element("div.slds-modal__container header.slds-modal__header:has-text('New Ruleset')")
        
        self.browser.click("lightning-combobox.slds-form-element[data-tid='dataSpace'] div.slds-dropdown-trigger_click")
        self.shared.wait_and_click("lightning-combobox.slds-form-element[data-tid='dataSpace'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('default')")
            
        self.browser.click("lightning-combobox.slds-form-element[data-tid='entity'] div.slds-dropdown-trigger_click")
        self.shared.wait_and_click("lightning-combobox.slds-form-element[data-tid='entity'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Individual')")
        
        self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Next')")
        
        
        self.shared.wait_on_element("input.slds-input[placeholder='Enter a name...']")
        self.browser.fill_text("input.slds-input[placeholder='Enter a name...']",ir_name)
        
        self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Save')")
        
        if self.shared.wait_on_element(f"div.toastContainer:has-text('Ruleset {ir_name} was created')", 25):
            self.builtin.log_to_console("\n -> Identity Resolution Created!")
        else:
            raise Exception("Identity Resolution couldn't be created, please contact you adminstrator for details")
        
    def create_ir_matching_rule(self, ir_name): 
        """Create a Custom Matching Rule for the Identity Resolution"""
        self.builtin.log_to_console(f"\nCreate a Custom Matching Rule for the Identity Resolution...")
        
        # query = "SELECT Id FROM IdentityResolution Where Name = 'test' LIMIT 1"
        query = f"SELECT Id FROM IdentityResolution Where Name = '{ir_name}' LIMIT 1"
        
        ir_lookup = self.salesforceapi.soql_query(query)
        lookup_size = ir_lookup.get("totalSize", 0)
        if lookup_size > 0:
            ir_id = ir_lookup.get("records", {})[0].get("Id")
            
            # Load IdentityResolutions Page
            self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/r/IdentityResolution/{ir_id}/view", timeout="30s")
            self.shared.wait_for_page_to_load()
            self.shared.clear_popups()
            
            self.shared.wait_and_click("div[data-component-id='runtime_cdp_identityResolutionRuleConfiguration'] slot[name='actions'] button:has-text('Configure')")
            self.shared.wait_on_element("div.slds-modal__container div.greybackground div.subHeader:has-text('Match Rule 1')" )
            self.shared.wait_and_click("div.slds-modal__container div.greybackground button:has-text('Configure')")
            
            self.shared.wait_on_element("table.slds-table tbody tr:has(span:has-text('Custom Rule'))" )
            self.browser.check_checkbox(f"table.slds-table tbody tr:has(span:has-text('Custom Rule')) span.slds-radio_faux")
            self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Next')")
                        
            self.shared.wait_on_element("div.slds-modal__container div.identity-resolution-match-rules-wizard div.subHeader:has-text('Match Rule Criteria')" )
            
            #1st Rule
            self.browser.click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Individual')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('First Name')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(1) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Fuzzy - Medium Precision')")
            
            #Adding an additional criteria to the rule.
            self.browser.click("button:has-text('Add Criteria')")            
            
            #2nd Rule
            self.browser.click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Individual')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Last Name')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(2) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Exact')")
            
            #Adding an additional criteria to the rule.
            self.browser.click("button:has-text('Add Criteria')")            
            
            #3 Rule
            self.browser.click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-dmo'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Contact Point Email')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-field'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Email Address')")
            
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click")
            self.shared.wait_and_click("div[data-tid='match-rule-criteria']:nth-child(3) lightning-combobox[data-tid='select-match-method'] div.slds-dropdown-trigger_click div.slds-listbox lightning-base-combobox-item span.slds-truncate:has-text('Exact Normalized')")
            
            sleep(5)
            self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Next')")
            self.shared.wait_and_click("footer.slds-modal__footer button:has-text('Save')")
            
    def publish_scoring_rules(self, retries=0):
        """Selecting Unified Individual and Publishing Scoring Rules"""
        self.builtin.log_to_console(f"\nSelecting Unified Individual and Publishing Scoring Rules...")
        
        # self.shared.go_to_setup_admin_page("PeopleScoringSetup/home", force_reload= True)
        self.shared.go_to_setup_admin_page("UnifiedMarketingCustomSettings/home", force_reload= True)
        
        self.shared.wait_and_click("lightning-tab-bar li.slds-tabs_default__item a:has-text('Customer Lifecycle')")
        self.shared.wait_and_click("div.uma-marketing-setup-button-title button.slds-button:has-text('Enable Lead Scoring')")
        
        self.browser.switch_page(self.browser.get_page_ids(SelectionType["ALL"])[0])
        sleep(3)
        if self.browser.get_element_count("setup_scoring_peoplescoring-people-score-details button.slds-button:has-text('Select Unified Individual')") > 0:
            self.builtin.log_to_console("\n -> Found Select Unified Individual Button")
            self.browser.click("setup_scoring_peoplescoring-people-score-details button.slds-button:has-text('Select Unified Individual')")
            self.shared.wait_on_element("h1.slds-modal__title:has-text('Select Your Unified Individual')" )
            
            self.browser.click("div.select-unified-individual-modal-body div.slds-dropdown-trigger_click")
            if self.browser.get_element_count("div.select-unified-individual-modal-body div.slds-dropdown-trigger_click lightning-base-combobox-item span.slds-truncate") > 0: 
                self.shared.wait_and_click("div.select-unified-individual-modal-body div.slds-dropdown-trigger_click lightning-base-combobox-item span.slds-truncate:nth-child(1)")
            else:
                if retries < 5:
                    sleep(3)
                    self.publish_scoring_rules(retries+1)
                    return
                else:
                    raise Exception("Unified Individual couldnt be found. Please configure this manually or contact your administrator")
            
            self.shared.wait_and_click("div.slds-modal__footer button:has-text('Save')")
            
            if "visible" not in self.browser.get_element_states("button.slds-button:has-text('Publish'):disabled"):
                self.builtin.log_to_console("\n -> Found Publish Button")
                self.browser.click("button.slds-button:has-text('Publish')")
                self.shared.wait_and_click("div.slds-modal__footer button:has-text('Publish')")
                # sleep(15)
                self.builtin.log_to_console("\n -> Scoring Rules were published")
            else:
                self.builtin.log_to_console("\n -> Scoring Rules were already published")
            return
            
        else:
            self.builtin.log_to_console("\n -> Unified Individual was already selected")
        
    
    def activate_co_create_with_einstein(self):
        """Activates Co-Create with Einstein"""
        self.builtin.log_to_console(f"\nActivating Co-Create with Einstein...")
        
        self.shared.go_to_setup_admin_page("EinsteinCoCreate/home")
        if "visible" in self.browser.get_element_states("button.slds-button:has-text('Activate')"):
            self.builtin.log_to_console("\n -> Found Activate Button")
            self.browser.click("button.slds-button:has-text('Activate')")
            
            if self.shared.wait_on_element("p.coCreateActivationStatusLabel span:has-text('Activated')", 15):
                self.builtin.log_to_console("\n -> Co-Create with Einstein is now ON")
        else:
            self.builtin.log_to_console("\n -> Co-Create with Einstein is already active.")
    
    def activate_einstein_sto(self):
        """Activates Einstein Send Time Optimization (STO)"""
        self.builtin.log_to_console(f"\nActivates Einstein Send Time Optimization (STO)...")
        
        self.shared.go_to_setup_admin_page("UmaSto/home")
        if "visible" in self.browser.get_element_states("button.slds-button:has-text('Activate')"):
            self.builtin.log_to_console("\n -> Found Activate Button")
            self.browser.click("button.slds-button:has-text('Activate')")
            
            self.builtin.log_to_console("\n -> Einstein Send Time Optimization is now ON")
            # if self.shared.wait_on_element("p.stoActivationStatusLabel span:has-text('Activated')", 15): 
            #     self.builtin.log_to_console("\n -> Einstein Send Time Optimization is now ON")
        else:
            self.builtin.log_to_console("\n -> Einstein Send Time Optimization is already active.")
    
    def enable_einstein_metrics_guard(self):
        """Enable Einstein Metrics Guard"""
        self.builtin.log_to_console(f"\nEnable Einstein Metrics Guard...")
        
        self.shared.go_to_setup_admin_page("E360EmailFeatures/home")
        if "visible" in self.browser.get_element_states("h2.slds-card__header-title span:has-text('Einstein Metrics Guard')"):
            checked = "checked" in self.browser.get_element_states(
                "span.slds-checkbox_faux"
            )
            if not checked:
                self.builtin.log_to_console(
                    "\n -> Setting not enabled. Clicking toggle now..."
                )
                self.browser.click("span.slds-checkbox_faux")
                sleep(1)
            if self.shared.wait_on_element("div.toastContainer:has-text('This option has successfully been updated')", 15):
                self.builtin.log_to_console("\n -> Einstein Metrics Guard Setting is NOW Enabled!")
        else:
            self.builtin.log_to_console("\n -> Einstein Metrics Guard Setting is already active.")
            
