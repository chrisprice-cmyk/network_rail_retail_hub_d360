from time import sleep
from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI


class QbrixFINSKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
        self.shared = QbrixSharedKeywords()
        self._salesforceapi = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    @property
    def salesforceapi(self):
        if self._salesforceapi is None:
            self._salesforceapi = SalesforceAPI()
        return self._salesforceapi

    def enable_interest_tagging(self):
        """
        Enables Interest Tagging for FINS Cloud
        """
        enable_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("InterestTaggingSettings/home")
        self.browser.wait_for_elements_state("p:text-is('Let users access interest tags feature')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(enable_toggle)
        if visible:
            self.browser.click(enable_toggle)
            sleep(2)
