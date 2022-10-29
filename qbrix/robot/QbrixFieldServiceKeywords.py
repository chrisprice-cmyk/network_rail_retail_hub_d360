from time import sleep

from Browser import ElementState
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QbrixFieldServiceKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
        self.shared = QbrixSharedKeywords()

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def enable_field_service(self):
        self.shared.go_to_setup_admin_page("FieldServiceSettings/home")
        sleep(15)
        checked = "checked" in self.browser.get_element_states("label:has-text('Field Service')")
        if not checked:
            toggle_switch = self.browser.get_element("label:has-text('Field Service')")
            self.browser.click(toggle_switch)
            sleep(10)

    def go_to_field_service_admin_page(self):
        """Go directly to the Field Service admin page"""
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/n/FSL__Field_Service_Settings")
        self.browser.wait_for_elements_state(":nth-match(iframe,1) >>> h1:has-text('Getting Started')",
                                             ElementState.visible, '120s')

    def enable_all_field_service_permission_sets(self):
        self.go_to_field_service_admin_page()
        self.browser.click(":nth-match(iframe,1) >>> div.settings-tab:has-text('Permission Sets')")
        sleep(30)
        elements = self.browser.get_elements(":nth-match(iframe,1) >>> div:text-is('Create Permissions')")
        for elem in elements:
            visible = "visible" in self.browser.get_element_states(elem)
            if visible:
                self.browser.click(elem)
                sleep(30)
        elements = self.browser.get_elements(":nth-match(iframe,1) >>> div:text-is('Update Permissions')")
        for elem in elements:
            visible = "visible" in self.browser.get_element_states(elem)
            if visible:
                self.browser.click(elem)
                sleep(30)

    def disable_field_service_status_transitions(self):
        self.go_to_field_service_admin_page()
        self.browser.click(":nth-match(iframe,1) >>> span:text-is('Service Appointment Life Cycle')")
        self.browser.wait_for_elements_state(":nth-match(iframe,1) >>> h1:text-is('Service Appointment Life Cycle')",
                                             ElementState.visible, '15s')
        self.browser.click(":nth-match(iframe,1) >>> div.settings-tab:has-text('Status Transitions')")
        self.browser.wait_for_elements_state(
            ":nth-match(iframe,1) >>> div:text-is('Service Appointment Status Transitions')", ElementState.visible,
            '15s')
        visible = "visible" in self.browser.get_element_states(
            ":nth-match(iframe,1) >>> :nth-match(span.innerCheckboxValue.unchecked, 1)")
        if not visible:
            toggle_switch = self.browser.get_element(
                ":nth-match(iframe,1) >>> :nth-match(span.innerCheckboxValue.checked, 1)")
            self.browser.click(toggle_switch)
            self.browser.click(":nth-match(iframe,1) >>> .ng-scope:nth-child(2) >> #SettingContainer .save-button")
            self.browser.wait_for_elements_state(
                ":nth-match(iframe,1) >>> .ng-scope:nth-child(2) >> span:text-is('Your changes were saved.')",
                ElementState.visible, '10s')

    def disable_field_service_integration(self):
        self.shared.go_to_setup_admin_page("FieldServiceSettings/home")
        sleep(2)
        checked = "checked" in self.browser.get_element_states(
            "label:has-text('Permissions to access data needed for optimization, automatic scheduling, and service appointment bundling.')")
        if checked:
            toggle_switch = self.browser.get_element(
                "label:has-text('Permissions to access data needed for optimization, automatic scheduling, and service appointment bundling.')")
            self.browser.click(toggle_switch)
            sleep(5)
            self.browser.click("button:text-is('Save')")
            sleep(5)

