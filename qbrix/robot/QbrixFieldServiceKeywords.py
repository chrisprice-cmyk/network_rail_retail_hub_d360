from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI


class QbrixFieldServiceKeywords(BaseLibrary):

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

    def enable_field_service(self):
        """
        Enables Field Service Setting in Salesforce Setup
        """

        # Go To Field Service Setup
        self.shared.go_to_setup_admin_page("FieldServiceSettings/home", 10)

        # Enable Field Service Setting
        field_service_toggle_selector = "span.slds-form-element__label:has-text('Field Service')"
        self.browser.wait_for_elements_state(field_service_toggle_selector, ElementState.visible, '30s')
        if not "checked" in self.browser.get_element_states(field_service_toggle_selector):
            self.browser.click(field_service_toggle_selector)
            sleep(10)

    def go_to_field_service_admin_page(self):
        """Go directly to the Field Service admin page"""
        self.shared.go_to_app("Field Service Admin")
        # Go To Field Service Package Settings Page
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/n/FSL__Field_Service_Settings", timeout='30s')
        self.browser.wait_for_elements_state("iframe >>> h1:has-text('Getting Started'):visible", ElementState.visible,
                                             '120s')

    def field_service_sdo_config(self):
        """ Go to Field Service Settings and configure additional settings for demo use """

        # Go to Field Service Settings
        self.go_to_field_service_admin_page()

        # Enable Schedule Bundling

        menu_scheduling_selector = ":nth-match(iframe,1) >>> id=SettingsMenu >> div.menuItem >> span:text-is('Scheduling'):visible"
        tabs_bundling_selector = ":nth-match(iframe,1) >>> div.settings-tab:has-text('Bundling')"
        checkbox_bundling_selector = ":nth-match(iframe,1) >>> div.setting-row-container:has-text('Bundle your service appointments') >> div.slds-checkbox"
        save_button_selector = ":nth-match(iframe,1) >>> div.save-footer >> div.save-button:visible"

        self.browser.click(menu_scheduling_selector)
        sleep(2)
        self.browser.click(tabs_bundling_selector)
        sleep(2)
        if "visible" not in self.browser.get_element_states(
                ":nth-match(iframe,1) >>> p:has-text('Service appointment bundles are active.')"):
            self.browser.click(checkbox_bundling_selector)
            self.browser.click(save_button_selector)
            sleep(2)

        # Setup Dispatcher UI - Custom Actions

        menu_dispatcher_ui_selector = ":nth-match(iframe,1) >>> id=SettingsMenu >> div.menuItem >> span:text-is('Dispatcher Console UI'):visible"
        drag_jumps_selector = ":nth-match(iframe,1) >>> div.setting-row-container:has-text('Drag jumps on gantt') >> input.input-settings"
        gantt_settings_selector = ":nth-match(iframe,1) >>> div.settings-tab:has-text('Updating the Gantt')"
        gantt_refresh_selector = ":nth-match(iframe,1) >>> div.setting-row-container:has-text('Seconds between Gantt refreshes') >> input.input-settings"
        tabs_custom_actions_selector = ":nth-match(iframe,1) >>> div.settings-tab:has-text('Custom Actions')"
        action_cat_selector = ":nth-match(iframe,1) >>> id=CA-GanttSection >> div:text-is('Mass Actions')"
        new_action_btn_selector = ":nth-match(iframe,1) >>> id=CA-newAction"
        new_action_label_selector = ":nth-match(iframe,1) >>> div.CA-field-container:has-text('Label in Dispatcher Console') >> input.CA-input-label"
        vf_page_selector = ":nth-match(iframe,1) >>> div.CA-field-container:has-text('Visualforce') >> select.select-setting"
        custom_perm_selector = ":nth-match(iframe,1) >>> div.CA-field-container:has-text('Required Custom Permission') >> select.select-setting"

        self.browser.click(menu_dispatcher_ui_selector)

        # Configure Gantt Jumps
        self.browser.fill_text(drag_jumps_selector, "15")
        self.browser.click(save_button_selector)
        sleep(5)

        # Gantt Updates
        self.browser.click(gantt_settings_selector)
        sleep(1)
        self.browser.fill_text(gantt_refresh_selector, "10")
        self.browser.click(save_button_selector)
        sleep(5)

        # Check and Enable Custom Actions
        self.browser.click(tabs_custom_actions_selector)
        sleep(15)
        self.browser.click(action_cat_selector)
        sleep(1)

        # Create Demo Bundle
        if "visible" not in self.browser.get_element_states(
                ":nth-match(iframe,1) >>> div.singleCustomAction:has-text('Create Demo Bundle')"):
            self.browser.click(new_action_btn_selector)
            sleep(2)
            self.browser.fill_text(new_action_label_selector, "Create Demo Bundle")
            self.browser.select_options_by(vf_page_selector, SelectAttribute.text, "SDO_FSL_Launch_Create_Bundles_Flow")
            self.browser.select_options_by(custom_perm_selector, SelectAttribute.text,
                                           "Gantt and List - Bundle and Unbundle")
            self.browser.click(save_button_selector)
            sleep(5)

        # Create Sliding Demo Data
        if "visible" not in self.browser.get_element_states(
                ":nth-match(iframe,1) >>> div.singleCustomAction:has-text('Create Sliding Demo Data')"):
            self.browser.click(new_action_btn_selector)
            sleep(2)
            self.browser.fill_text(new_action_label_selector, "Create Sliding Demo Data")
            self.browser.select_options_by(vf_page_selector, SelectAttribute.text,
                                           "SDO_FSL_Launch_Sliding_Flow_Launch_Slide")
            self.browser.select_options_by(custom_perm_selector, SelectAttribute.text, "Bulk Schedule")
            self.browser.click(save_button_selector)
            sleep(5)

        # Setup Optimization
        menu_optimize_selector = ":nth-match(iframe,1) >>> id=SettingsMenu >> div.menuItem >> span:text-is('Optimization'):visible"
        optimization_checkbox_selector = ":nth-match(iframe,1) >>> div.slds-media:has-text('Optimization Insights') >> div.transitions-checkbox >> span.toggled-label:text-is('ON')"

        self.browser.click(menu_optimize_selector)
        sleep(1)
        if "visible" not in self.browser.get_element_states(optimization_checkbox_selector):
            self.browser.click(optimization_checkbox_selector)
            self.browser.click(save_button_selector)
            sleep(5)

        sleep(5)

    def enable_all_field_service_permission_sets(self):
        """
        Enables all Field Service Permission Sets and also updates Permissions Sets if there are updates waiting
        """
        self.go_to_field_service_admin_page()
        self.browser.click(":nth-match(iframe,1) >>> div.settings-tab:has-text('Permission Sets')")
        sleep(30)

        create_permission_selector = ":nth-match(iframe,1) >>> div:text-is('Create Permissions')"
        update_permission_selector = ":nth-match(iframe,1) >>> div:text-is('Update Permissions')"

        for x in range(0, 4):

            print(f"Check {x}")

            if x == 0 or x == 1:
                current_selector = create_permission_selector

            if x == 2 or x == 3:
                current_selector = update_permission_selector

            permission_button_elements = self.browser.get_elements(current_selector)

            if permission_button_elements is None:
                continue
            else:
                for permission_button in permission_button_elements:
                    if "visible" in self.browser.get_element_states(permission_button):
                        self.browser.click(permission_button)
                        sleep(30)

    def disable_field_service_status_transitions(self):
        """
        Disables Field Service Status Transitions
        """
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
        """
        Disables Field Service Integration
        """
        self.shared.go_to_setup_admin_page("FieldServiceSettings/home", 5)
        checked = "checked" in self.browser.get_element_states(
            "label:has-text('Permissions to access data needed for optimization, automatic scheduling, and service appointment bundling.')")
        if checked:
            toggle_switch = self.browser.get_element(
                "label:has-text('Permissions to access data needed for optimization, automatic scheduling, and service appointment bundling.')")
            self.browser.click(toggle_switch)
            sleep(5)
            self.browser.click("button:text-is('Save')")
            sleep(5)
