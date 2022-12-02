from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QbrixToolingKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
        self.shared = QbrixSharedKeywords()

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser
    
    # -----------------------------------------------------------------------------------------------------------------------------------------
    # Q BRANCH TOOLING FUNCTIONS
    # -----------------------------------------------------------------------------------------------------------------------------------------

    def enable_q_passport(self):
        """ Enables Q Passport Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        sleep(10)
        self.browser.click("iframe >>> a:text-is('Q_Passport')")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(10)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(2)

    def enable_demo_boost(self):
        """ Enables Demo Boost Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        sleep(10)
        self.browser.click("iframe >>> a:text-is('Demo Boost')")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(10)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(2)

    def enable_demo_wizard(self):
        """ Enables Demo Wizard Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        sleep(10)
        self.browser.click("iframe >>> a:text-is('Demo Wizard')")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(10)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(2)

    def enable_data_tool(self):
        """ Enables Data Tool Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        sleep(10)
        self.browser.click("iframe >>> a:text-is('NXDO Data Tool')")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(10)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(10)
        self.browser.click("iframe >>> .btn:has-text('Manage Profiles')")
        sleep(10)
        checked = "checked" in self.browser.get_element_states(
            "iframe >>> tr:has-text('System Administrator') >> input")
        if not checked:
            self.browser.click("iframe >>> tr:has-text('System Administrator') >> input")
            sleep(10)
            self.browser.click("iframe >>> .btn:has-text('Save')")
            sleep(2)
