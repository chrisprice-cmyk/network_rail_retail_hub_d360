from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.qbrix_shared_keywords import QbrixSharedKeywords


class QbrixVraKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def create_vra_service_channel(self):
        """ Creates the VRA Service Channel """
        QbrixSharedKeywords.go_to_setup_admin_page("ServiceChannelSettings/home")
        self.browser.wait_for_elements_state("iframe >>> .btn:has-text('New')", ElementState.visible,
                                             '15s')
        visible = "visible" in self.browser.get_element_states("iframe >>> .listRelatedObject:has-text('SDO_VRA_End_User_Session_Request')")
        if not visible:
            self.browser.click("iframe >>> .btn:has-text('New')")
            self.browser.fill_text("iframe >>> tr:has-text('Service Channel Name') >> input", "VRA - End User Session Request")
            self.browser.fill_text("iframe >>> tr:has-text('Developer Name') >> input", "")
            sleep(1)
            self.browser.fill_text("iframe >>> tr:has-text('Developer Name') >> input", "SDO_VRA_End_User_Session_Request")
            sleep(1)
            self.browser.select_options_by("iframe >>> tr:has-text('Salesforce Object') >> select", SelectAttribute.value,
                                            "tspa__Visual_Support_Request__c")
            sleep(2)
            self.browser.click("iframe >>> :nth-match(.saveBtn:has-text('Save'),1)")
            sleep(1)
