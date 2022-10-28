from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QbrixSchedulerKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def enable_scheduler(self):
        """ Enables Salesforce Scheduler """
        QbrixSharedKeywords().go_to_setup_admin_page("LightningSchedulerSettings/home")
        self.browser.wait_for_elements_state("h2:has-text('Event Management')", ElementState.visible, '30s')
        sleep(5)
        checked = "checked" in self.browser.get_element_states("label:has-text('Appointment Distribution')")
        if not checked:
            toggle_switch = self.browser.get_element("label:has-text('Appointment Distribution')")
            self.browser.click(toggle_switch)
            sleep(3)
        checked2 = "checked" in self.browser.get_element_states("label:has-text('Aggregate Resource Use')")
        if not checked2:
            toggle_switch2 = self.browser.get_element("label:has-text('Aggregate Resource Use')")
            self.browser.click(toggle_switch2)
            sleep(3)
        checked3 = "checked" in self.browser.get_element_states("label:has-text('Multi-Resource Scheduling')")
        if not checked3:
            toggle_switch3 = self.browser.get_element("label:has-text('Multi-Resource Scheduling')")
            self.browser.click(toggle_switch3)
            sleep(3)

    def create_appointment_assignment_policies(self):
        """ Creates the Appointment Assignment Policies """
        QbrixSharedKeywords().go_to_setup_admin_page("AppointmentAssignmentPolicy/home")
        sleep(2)
        self.browser.wait_for_elements_state("iframe >>> .btn:has-text('New')", ElementState.visible, '30s')
        visible = "visible" in self.browser.get_element_states(
            "iframe >>> .listRelatedObject:has-text('Activity based distribution')")
        if not visible:
            self.browser.click("iframe >>> .btn:has-text('New')")
            self.browser.wait_for_elements_state("iframe >>> input[name='MasterLabel']", ElementState.visible, '30s')
            self.browser.fill_text("iframe >>> input[name='MasterLabel']", "Activity based distribution")
            self.browser.fill_text("iframe >>> input[name='DeveloperName']", "Activity_based_distribution")
            self.browser.select_options_by("iframe >>> select[name='PolicyType']", SelectAttribute.text,
                                           "Load Balancing")
            self.browser.select_options_by("iframe >>> select[name='PolicyApplicableDuration']", SelectAttribute.text,
                                           "Parameter-Based")
            self.browser.select_options_by("iframe >>> select[name='UtilizationFactor']", SelectAttribute.text,
                                           "Number of Appointments")
            sleep(2)
            self.browser.click("iframe >>> :nth-match(.btn:has-text('Save'),1)")
            sleep(1)
