from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QbrixServiceKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
        self.shared = QbrixSharedKeywords()

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def enable_incident_management(self):
        """" Enables Incident Management """
        self.shared.go_to_setup_admin_page("IncidentManagement/home")
        sleep(8)
        checked = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Customer Service Incident Management'), 2)")
        if not checked:
            toggle_switch = self.browser.get_element(
                ":nth-match(label:has-text('Customer Service Incident Management'), 2)")
            self.browser.click(toggle_switch)
            sleep(1)

    def enable_slack_integration(self):
        """ Enables Slack Integration with the target org """
        self.shared.go_to_setup_admin_page("SlackSetupAssistant/home")
        sleep(2)
        checked = "checked" in self.browser.get_element_states("label:has-text('Unaccepted')")
        if not checked:
            self.browser.click("label:has-text('Unaccepted')")
            sleep(3)
        self.browser.wait_for_elements_state("label:has-text('Accepted')", ElementState.visible, '15s')
        checked = "checked" in self.browser.get_element_states("label:has-text('Disabled')")
        if not checked:
            self.browser.click("label:has-text('Disabled')")

    def enable_case_swarming(self):
        self.enable_slack_integration()
        self.shared.go_to_setup_admin_page("SlackServiceApp/home")
        checked = "checked" in self.browser.get_element_states("span.slds-checkbox_faux")
        if not checked:
            self.browser.click("span.slds-checkbox_faux")
            sleep(1)
        self.shared.go_to_setup_admin_page("CaseSwarming/home")
        self.shared.set_lightning_toggle("on")

    def create_chat_button(self):
        self.shared.go_to_setup_admin_page("LiveChatButtonSettings/home")
        sleep(4)
        self.browser.get_element_states(".button:has-text('New')")
        sleep(5)
