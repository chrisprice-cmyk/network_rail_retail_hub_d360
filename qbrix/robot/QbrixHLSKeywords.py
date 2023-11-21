from time import sleep

from Browser import ElementState
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixHLSKeywords(QbrixRobotTask):

    """Shared Keywords for HLS"""

    def enable_care_gaps(self):
        """
        Enables Care Gaps for HLS
        """
        self.builtin.log_to_console("\n[HLS] Enabling Care Gaps...")
        # Go to setup page
        self.shared.go_to_setup_admin_page("IntegratedCareManagementSettings/home")
        care_gap_selector = "h3.slds-card__header-title:has-text('Care Gap')"
        self.browser.wait_for_elements_state(
            care_gap_selector, ElementState.visible, "30s"
        )
        if not "checked" in self.browser.get_element_states(care_gap_selector):
            self.browser.click(care_gap_selector)

    def generate_decision_tables(self):
        """
        Generate Decision Tables for HLS
        """
        self.builtin.log_to_console("\n[HLS] Generating Decision Tables...")
        self.shared.go_to_setup_admin_page("AdvancedTherapyManagementSettings/home")
        # make sure iframe is considered
        my_iframe_handler = self.shared.iframe_handler()
        # expand that panel, only if it's not expanded already
        if self.browser.get_element_count(
            f"{my_iframe_handler} .slds-setup-assistant__item:has-text('Configure Decision Tables') button.slds-button_icon[aria-expanded='false']"
        ):
            self.builtin.log_to_console(
                "\n[HLS] Found Generate Decision Tables not expanded"
            )
            self.browser.click(
                f"{my_iframe_handler} .slds-setup-assistant__item:has-text('Configure Decision Tables') button.slds-button_icon[aria-expanded='false']"
            )
            if self.browser.get_element_count(
                f"{my_iframe_handler} .slds-setup-assistant__item:has-text('Generate Decision Tables to Override Default Settings'):visible"
            ):
                self.builtin.log_to_console("\n[HLS] -> Expanded!")
        # click the button whose text is Generate Decision Tables
        self.shared.wait_and_click(
            f"{my_iframe_handler} button.slds-button:text-is('Generate Decision Tables')"
        )
        # confirm to generate decision tables
        if self.browser.get_element_count(
            f"{my_iframe_handler} button.slds-button:text-is('Generate')"
        ):
            self.shared.wait_and_click(
                f"{my_iframe_handler} button.slds-button:text-is('Generate')"
            )
            self.builtin.log_to_console("\n[HLS] Decision Tables Generated")
        self.builtin.log_to_console("\n[HLS] Decision Tables Step Complete")

    def enable_advanced_scheduling(self):
        """
        Enables Advanced Scheduling Settings for HLS
        """
        self.builtin.log_to_console("\n[HLS] Enabling Advanced Scheduling Settings...")
        self.shared.go_to_setup_admin_page("AdvancedTherapyManagementSettings/home")
        # make sure iframe is considered
        my_iframe_handler = self.shared.iframe_handler()
        # expand that panel, only if it's not expanded already
        if self.browser.get_element_count(
            f"{my_iframe_handler} .slds-setup-assistant__item:has-text('Activate Advanced Scheduling Settings') button.slds-button_icon[aria-expanded='false']"
        ):
            self.builtin.log_to_console(
                "\n Found Activate Advanced Scheduled Settings not expanded"
            )
            self.browser.click(
                f"{my_iframe_handler} .slds-setup-assistant__item:has-text('Activate Advanced Scheduling Settings') button.slds-button_icon[aria-expanded='false']"
            )
        # click the button whose text is Activate Advanced Scheduling
        self.shared.wait_and_click(
            f"{my_iframe_handler} button.slds-button:text-is('Activate Advanced Scheduling')"
        )
        # confirm to activate
        if self.browser.get_element_count(
            f"{my_iframe_handler} button.slds-button:text-is('Activate')"
        ):
            self.shared.wait_and_click(
                f"{my_iframe_handler} button.slds-button:text-is('Activate')"
            )
            self.builtin.log_to_console("\n[HLS] -> Advanced Scheduling Enabled!")
        self.builtin.log_to_console("\n[HLS] -> Advanced Scheduling Step Complete!")

    def enable_care_plans(self):
        """
        Enables Care Plans for HLS
        """
        self.builtin.log_to_console("\n[HLS] Enabling Care Plans...")
        self.shared.go_to_setup_admin_page("CarePlanSettings/home")
        self.browser.wait_for_elements_state(
            "p:text-is('Care Plans')", ElementState.visible, "30s"
        )
        if "checked" not in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 1)"
        ):
            self.browser.click(":nth-match(label:has-text('Disabled'), 1)")
            sleep(1)
        self.builtin.log_to_console("\n[HLS] -> Care Plans Enabled!")

    def enable_assessments(self):
        """
        Enables Assessments for HLS
        """
        self.builtin.log_to_console("\n[HLS] Enabling Assessments...")
        self.shared.go_to_setup_admin_page("AssessmentSettings/home")
        self.browser.wait_for_elements_state(
            "h3:text-is('Guest User Assessments')", ElementState.visible, "30s"
        )
        if "checked" not in self.browser.get_element_states(
            ".toggle:has-text('Disabled')"
        ):
            self.browser.click(".toggle:has-text('Disabled')")
            self.shared.wait_and_click("button:has-text('Turn On')", post_click_sleep=5)
        self.builtin.log_to_console("\n[HLS] -> Enabled!")

    def enable_care_plans_grantmaking(self):
        """
        Enables Care Plans Grantmaking for HLS
        """
        self.builtin.log_to_console("\n[HLS] Enabling Care Plan Grantmaking...")
        self.shared.go_to_setup_admin_page("CarePlanSettings/home")
        self.browser.wait_for_elements_state(
            "p:text-is('Care Plans')", ElementState.visible, "30s"
        )
        if "checked" not in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 1)"
        ):
            self.browser.click(":nth-match(label:has-text('Disabled'), 1)")
            sleep(1)

        if "checked" not in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 2)"
        ):
            self.browser.click(":nth-match(label:has-text('Disabled'), 2)")
            sleep(2)
            if "visible" in self.browser.get_element_states(
                "button:has-text('Enable')"
            ):
                self.shared.click_button_with_text("Enable")
                sleep(5)
        self.builtin.log_to_console("\n[HLS] -> Enabled!")
