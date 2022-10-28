from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.qbrix_shared_keywords import QbrixSharedKeywords


class QbrixSurveysKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def enable_surveys(self):
        sleep(5)
        QbrixSharedKeywords.go_to_setup_admin_page("SurveySettings/home")
        sleep(10)
        # label:has-text('Inactive')
        # [data-interactive-lib-uid=\"5\"]
        survey_toggle = "[class=\"toggle slds-p-left_medium\"]"

        if self.browser.get_element_count(survey_toggle) == 1:
            self.browser.wait_for_elements_state(survey_toggle, ElementState.visible, '30s')
            toggle_switch = self.browser.get_element(survey_toggle)
            self.browser.hover(toggle_switch)
            self.browser.click(toggle_switch)
            sleep(10)

    def set_survey_default_community(self):
        """ Sets the Default Community for Surveys """
        self.enable_surveys()

        # visible
        # = "visible" in self.browser.get_element_states(f"iframe >>> input:has-text('New')")
        sleep(5)

        # Set the default community to SDO Consumer
        # Routing Type
        self.browser.select_options_by("[class=\"slds-select\"]", SelectAttribute.text, "SDO - Consumer")
        sleep(2)