from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixVraKeywords(QbrixRobotTask):
    """Q Robot keywords for Visual Remote Assistant (VRA)"""

    def create_vra_service_channel(
        self,
        service_channel_name=None,
        service_channel_developer_name=None,
        related_salesforce_object=None,
    ) -> None:
        """
        Checks that you have a Visual Remote Assistant (VRA) service channel configured within the target Salesforce org. If not, it is created with the default demo configuration.

        Args:
            service_channel_name (str): Name of the service channel to be used with VRA. Defaults to 'VRA - End User Session Request'
            service_channel_developer_name (str): API name for the service channel. Defaults to 'SDO_VRA_End_User_Session_Request'
            related_salesforce_object (str): Target API for the Salesforce object. Defaults to 'tspa__Visual_Support_Request__c'
        """

        self.builtin.log_to_console(
            "\nChecking Visual Remote Assistant (VRA) Service Channel has been configured:"
        )

        # Set Defaults
        if not service_channel_name:
            service_channel_name = "VRA - End User Session Request"

        if not related_salesforce_object:
            related_salesforce_object = "tspa__Visual_Support_Request__c"

        if not service_channel_developer_name:
            service_channel_developer_name = "SDO_VRA_End_User_Session_Request"

        self.builtin.log_to_console(
            f"\n -> Supplied Channel Name: {service_channel_name}\nService Channel Developer Name: {service_channel_developer_name}\n -> Supplied Salesforce Object: {related_salesforce_object}"
        )

        # Load the Setup Page
        self.shared.go_to_setup_admin_page("ServiceChannelSettings/home")
        self.builtin.log_to_console("\n -> Loaded VRA Service Channel Setup Page")

        # Wait for New button - This assumes that page has loaded now
        iframe_selector = self.shared.iframe_handler()
        self.browser.wait_for_elements_state(
            f"{iframe_selector} .btn:has-text('New')", ElementState.visible, "15s"
        )

        # Check Current Settings
        self.builtin.log_to_console("\n -> Checking current settings...")
        if "visible" not in self.browser.get_element_states(
            f"iframe >>> .listRelatedObject:has-text('{service_channel_developer_name}')"
        ):
            self.builtin.log_to_console(
                "\n -> Service Channel has not be configured. Creating configuration now:"
            )
            self.browser.click(f"{iframe_selector} .btn:has-text('New')")
            self.browser.fill_text(
                f"{iframe_selector} tr:has-text('Service Channel Name') >> input",
                service_channel_name,
            )
            self.browser.fill_text(
                f"{iframe_selector} tr:has-text('Developer Name') >> input", ""
            )
            sleep(1)
            self.browser.fill_text(
                f"{iframe_selector} tr:has-text('Developer Name') >> input",
                service_channel_developer_name,
            )
            sleep(1)
            self.browser.select_options_by(
                f"{iframe_selector} tr:has-text('Salesforce Object') >> select",
                SelectAttribute.value,
                related_salesforce_object,
            )
            sleep(2)
            self.browser.click(
                f"{iframe_selector} :nth-match(.saveBtn:has-text('Save'),1)"
            )
            sleep(1)
        self.builtin.log_to_console("\n -> Configuration Complete!")
