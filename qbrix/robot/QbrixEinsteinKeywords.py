from time import sleep
from Browser import ElementState
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QbrixEinsteinKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
        self.shared = QbrixSharedKeywords()

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def enable_einstein_analytics_crm(self):
        """
        Enable Einstein Analytics CRM within Salesforce Org
        """
        self.shared.go_to_setup_admin_page("InsightsSetupGettingStarted/home")
        self.browser.wait_for_elements_state("h1:has-text('Getting Started')", ElementState.visible, '60s')
        sleep(10)
        if "visible" in self.browser.get_element_states("button:has-text('Enable CRM Analytics')"):
            QbrixSharedKeywords().click_button_with_text("Enable CRM Analytics")
            sleep(30)

    def go_to_campaign_insights_setup_page(self):
        """
        Go directly to the Campaign Insights setup page
        """
        self.shared.go_to_setup_admin_page("CampaignInsights/home")
        sleep(10)

    def go_to_opportunity_insights_setup_page(self):
        """
        Go directly to the Opportunity Insights setup page
        """
        self.shared.go_to_setup_admin_page("OpportunityInsights/home")

    def go_to_account_insights_setup_page(self):
        """
        Go directly to the Account Insights setup page
        """
        self.shared.go_to_setup_admin_page("AccountInsights/home")

    def go_to_relationship_insights_setup_page(self):
        """
        Go directly to the Relationships Insights setup page
        """
        self.shared.go_to_setup_admin_page("EinsteinSmartTags/home")

    def go_to_key_account_insights_setup_page(self):
        """
        Go directly to the Key Accounts Insights setup page
        """
        self.shared.go_to_setup_admin_page("EKAI/home")

    def go_to_lead_scoring_setup_page(self):
        """
        Go directly to the Lead Scoring setup page
        """
        self.shared.go_to_setup_admin_page("LeadIQ/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Lead Scoring')", ElementState.visible, '30s')
        sleep(5)
        checked = "checked" in self.browser.get_element_states("label:has-text('Off')")
        if not checked:
            self.browser.click("label:has-text('Off')")
            sleep(3)
            self.browser.click("label:has-text('Default')")
            sleep(3)
            self.browser.click(".slds-button:has-text('Save')")
            sleep(2)

    def go_to_oppty_scoring_setup_page(self):
        """
        Go directly to the Opportunity Scoring setup page
        """
        self.shared.go_to_setup_admin_page("OpportunityIQSetupHome/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Opportunity Scoring')", ElementState.visible, '30s')
        sleep(5)
        enabled = "enabled" in self.browser.get_element_states(".slds-button:has-text('Set Up')")
        if enabled:
            self.browser.click(".slds-button:has-text('Set Up')")
            sleep(2)
            self.browser.click(".slds-button:has-text('Next')")
            sleep(2)
            self.browser.click(".slds-button:has-text('Next')")
            sleep(2)
            self.browser.click(".slds-button:has-text('Next')")
            sleep(2)
            self.browser.click(".slds-button:has-text('Next')")
            sleep(2)
            self.browser.click(".slds-button:has-text('Start')")
            sleep(4)

    def enable_automated_data_capture(self):
        """Go directly to the Opportunity Scoring setup page"""
        self.shared.go_to_setup_admin_page("AutomatedDataCapture/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Automated Contacts')", ElementState.visible, '30s')
        sleep(5)
        checked = "checked" in self.browser.get_element_states(":nth-match(span.slds-checkbox--faux,1)")
        if not checked:
            self.browser.click(":nth-match(span.slds-checkbox--faux,1)")
            sleep(1)
        checked2 = "checked" in self.browser.get_element_states(":nth-match(span.slds-checkbox--faux,2)")
        if not checked2:
            self.browser.click(":nth-match(span.slds-checkbox--faux,2)")
            sleep(5)

    def enable_einstein_prediction_builder(self):
        """ Enable Einstein Prediction Builder """
        self.shared.go_to_setup_admin_page("EinsteinBuilder/home")
        self.shared.click_button_with_text("Get Started")
        sleep(2)
        self.shared.set_lightning_toggle("on")

    def enable_einstein_activity_capture(self):
        self.shared.go_to_setup_admin_page("ActivitySyncEngineSettingsMain/home")
        self.browser.wait_for_elements_state(".einsteinTitle:has-text('Einstein Activity Capture')",
                                             ElementState.visible, '30s')
        sleep(2)
        enabled = "enabled" in self.browser.get_element_states(".slds-button:has-text('Get Started')")
        if enabled:
            self.browser.click(".slds-button:has-text('Get Started')")
            sleep(5)

    def enable_einstein_forecasting(self):
        self.shared.go_to_setup_admin_page("ForecastingPrediction/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Forecasting')", ElementState.visible, '30s')
        sleep(2)
        enabled = "enabled" in self.browser.get_element_states(".slds-button:has-text('Enable')")
        if enabled:
            self.browser.click(".slds-button:has-text('Enable')")
            sleep(20)

    def enable_call_coaching_eci(self):
        self.shared.go_to_setup_admin_page("CallCoachingSettings/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Conversation Insights')", ElementState.visible,
                                             '30s')
        sleep(5)
        checked = "checked" in self.browser.get_element_states(":nth-match(span.slds-checkbox_faux,1)")
        if not checked:
            self.browser.click(":nth-match(span.slds-checkbox_faux,1)")
            sleep(10)
            
            #deal with popup
            self.browser.click(".slds-button:has-text('Got It')")
            sleep(4)

    def enable_einstein_classification(self):
        self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home")
        self.browser.wait_for_elements_state("h1:has-text('Einstein Classification')", ElementState.visible, '10s')
        sleep(2)
        checked = "checked" in self.browser.get_element_states(
            "div.case-classification-pref >> label.slds-checkbox_toggle:text-is('Einstein Classification Apps')")
        if not checked:
            self.browser.click("label.slds-checkbox_toggle:has-text('Einstein Classification Apps')")
            sleep(5)
