from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask
from qbrix.tools.shared.qbrix_authentication import generate_mfa_code, get_secure_setting


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixMarketingKeywords(QbrixRobotTask):

    """Marketing Cloud Keywords for Robot"""

    def enable_pardot_setting(self):
        """ Enables Pardot Setting"""
        self.shared.go_to_setup_admin_page("PardotSetupAssistant/home")
        self.browser.wait_for_elements_state("div:text-is('B2B Marketing Setup Assistant')", ElementState.visible,
                                             '15s')
        self.browser.click(".slds-button:has-text('Send Your First Email')")
        self.browser.wait_for_elements_state(
            "span:text-is('Complete the required steps to send your first Account Engagement email.')", ElementState.visible,
            '15s')
        checked = "checked" in self.browser.get_element_states(":nth-match(span.slds-checkbox_faux,1)")
        if not checked:
            self.browser.click(":nth-match(span.slds-checkbox_faux,1)")
            sleep(1)

    def enable_pardot_app(self):
        """ Enables Pardot Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        self.browser.click("iframe >>> a:text-is('b2bma_canvas')")
        sleep(5)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(5)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(4)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(1)

    def create_pardot_template(self):
        """ Enables Pardot Connected App Settings"""
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/o/EmailTemplate/home")
        self.browser.wait_for_elements_state("a:has-text('New Email Template')", ElementState.visible, '30s')
        self.browser.click("a:has-text('All Email Templates')")
        sleep(5)
        visible = "visible" in self.browser.get_element_states(
            ".slds-table:has-text('Annual Customer Conference Invitation')")
        if not visible:
            self.browser.click("a:has-text('New Email Template')")
            self.browser.wait_for_elements_state("h2:has-text('New Email Template')", ElementState.visible, '30s')
            self.browser.fill_text(".forcePageBlockItem:has-text('Email Template Name') >> input",
                                   "Annual Customer Conference Invitation")
            self.browser.fill_text(".forcePageBlockItem:has-text('Description') >> input",
                                   "Pardot - Annual Customer Conference Invitation")
            self.browser.fill_text(".forcePageBlockItem:has-text('Subject') >> input",
                                   "Join us for our annual conference")
            self.browser.click("button[title='Save']")
            sleep(5)

    def enable_territory_management(self):
        """ Enables Maps Territory Planning Settings"""
        self.shared.go_to_setup_admin_page("Territory2Settings/home")
        sleep(5)
        visible = "visible" in self.browser.get_element_states(":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')")
        if visible:
            button_to_click = self.browser.get_element(":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')")
            self.browser.click(button_to_click)
            sleep(1)

    def connect_to_marketing_cloud_distributed_marketing(self, marketing_cloud_username = None, marketing_cloud_password = None, marketing_cloud_secret = None):

        if not marketing_cloud_username:
            marketing_cloud_username = get_secure_setting("Q_DM_MARKETING_CLOUD_UUN")

        if not marketing_cloud_password:
            marketing_cloud_password = get_secure_setting("Q_DM_MARKETING_CLOUD_PW")

        if not marketing_cloud_secret:
            marketing_cloud_secret = get_secure_setting("Q_DM_MARKETING_CLOUD_KEY")

        # Go To Admin Page
        self.shared.go_to_app('Sales')
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/n/mcdm_15__Distributed_Marketing_Administration", timeout='30s')

        # Create Distributed Marketing Business Unit
        try:
            self.browser.wait_for_elements_state("table", ElementState.visible, "10s")
            if self.browser.get_element_count("table >> tr:has-text('Distributed Marketing')") >= 1:
                print("Already Connected")
                return
        except Exception as e:
            print(e)
        create_business_unit_button = f"{self.shared.iframe_handler()} a.slds-button:text-is('Add Business Unit')"
        self.browser.wait_for_elements_state(create_business_unit_button, ElementState.visible, "30s")
        self.browser.click(create_business_unit_button)

        # Enter Name for Connection
        self.browser.wait_for_elements_state("iframe >>> div.step-container:has-text('Business Unit Display Name')", ElementState.visible, "20s")
        self.browser.fill_text("iframe >>> div.step-container:has-text('Business Unit Display Name') >> input[type='text']", "Distributed Marketing")
        self.browser.click("iframe >>> input.btn[value='Get Started']")

        # Enter Marketing Cloud Username
        self.browser.wait_for_elements_state("iframe >>> div.step-container:has-text('Marketing Cloud Username')", ElementState.visible, "20s")
        self.browser.fill_text("iframe >>> div.step-container:has-text('Marketing Cloud Username') >> input[type='text']", marketing_cloud_username)
        self.browser.click("iframe >>> div.step-container:has-text('Marketing Cloud Username') >> :nth-match(input.btn[value='Next'], 1)")

        # Auto-Generate Connection Records
        sleep(3)
        self.browser.click("iframe >>> div.step-container:has-text('Create the authentication settings records.') >> :nth-match(input.btn[value='Next'], 1)")
        sleep(3)
        self.browser.click("iframe >>> div.step-container:has-text('create the remote site settings, authentication provider, and named credential record.') >> :nth-match(input.btn[value='Next'], 1)")

        # Login To Marketing Cloud
        self.browser.click("iframe >>> a:text-is('Log In')")
        sleep(1)
        original_page = self.browser.switch_page('NEW')
        self.browser.fill_text("input[id='username']", marketing_cloud_username)
        self.browser.click("input[id='submit-btn']")
        sleep(1)
        self.browser.fill_text("input[id='password']", marketing_cloud_password)
        self.browser.click("input[id='submit-btn']")
        sleep(2)
        if self.browser.get_element_count("p:text-is('Use Salesforce Authenticator to approve the request.'):visible") > 0:
            self.browser.click("button:text-is('Didn't receive a notification?')")
            sleep(2)
        if self.browser.get_element_count("div.slds-form-element__control >> input[type='text']") > 0:
            self.browser.fill_text("div.slds-form-element__control >> input[type='text']", generate_mfa_code(marketing_cloud_secret))
            self.browser.click("button:has-text('Verify')")
        else:
            raise Exception("No input found for MFA code.")

        # Switch Back to Setup
        sleep(3)
        self.browser.switch_page(original_page)
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/n/mcdm_15__Distributed_Marketing_Administration", timeout='30s')
        self.browser.wait_for_elements_state("button.slds-button:has-text('Update Connection Information')", ElementState.visible, "20s")

        # Wait for Connected Status
        retry_count = 0
        while retry_count <= 5:
            self.browser.click("button.slds-button:has-text('Update Connection Information')")
            sleep(10)
            if self.browser.get_element_count("table >> tr:has-text('Distributed Marketing') >> td.cellContainer:has-text('Connected')") == 1:
                break
            retry_count += 1


