from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixServiceKeywords(QbrixRobotTask):
    """Service Cloud Keywords"""

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

    def enable_case_swarming(self):
        """Enables Case Swarming"""
        self.enable_slack_integration()
        self.shared.go_to_setup_admin_page("SlackServiceApp/home")
        checked = "checked" in self.browser.get_element_states("span.slds-checkbox_faux")
        if not checked:
            self.browser.click("span.slds-checkbox_faux")
            sleep(1)
        sleep(3)
        self.shared.go_to_setup_admin_page("CaseSwarming/home")
        self.browser.wait_for_elements_state("h1:has-text('Swarming')", ElementState.visible, '30s')
        checked = "checked" in self.browser.get_element_states("span.slds-checkbox_faux")
        if not checked:
            self.browser.click("span.slds-checkbox_faux")
            sleep(1)

    def create_chat_button(self):
        """Creates a new Chat Button"""
        self.shared.go_to_setup_admin_page("LiveChatButtonSettings/home")
        sleep(4)
        self.browser.get_element_states(".button:has-text('New')")
        sleep(5)

    def add_case_wrap_up_model(self):
        """Add Case Wrap Up Model"""
        self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home")
        sleep(2)
        if "visible" in self.browser.get_element_states("button.slds-button:text-is('Get Started')"):
            self.browser.click("button.slds-button:text-is('Get Started')")
        else:
            if "visible" in self.browser.get_element_states("button.slds-button:text-is('New Model')"):
                self.browser.click("button.slds-button:text-is('New Model')")
        self.browser.click("div.slds-visual-picker >> label:has-text('Case Wrap-Up')")
        self.browser.fill_text("label:has-text('Model Name')", "Case Wrap-Up")
        self.browser.click("label:has-text('Model Name')")
        sleep(1)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(2)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(2)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(3)
        self.browser.click("tr:has-text('Case Reason') >> div.slds-checkbox_add-button")
        self.browser.click("tr:has-text('Case Type') >> div.slds-checkbox_add-button")
        self.browser.click("tr:has-text('Escalated') >> div.slds-checkbox_add-button")
        self.browser.click("tr:has-text('Priority') >> div.slds-checkbox_add-button")
        sleep(3)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Finish')")
        sleep(10)

    def create_case_classification_model(self):
        """Create Case Classification"""
        self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home")
        sleep(2)
        if "visible" in self.browser.get_element_states("button.slds-button:text-is('Get Started')"):
            self.browser.click("button.slds-button:text-is('Get Started')")
        else:
            if "visible" in self.browser.get_element_states("button.slds-button:text-is('New Model')"):
                self.browser.click("button.slds-button:text-is('New Model')")
        self.browser.fill_text("label:has-text('Model Name')", "SDO - Classification")
        sleep(1)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(2)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(2)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        sleep(3)
        self.browser.click("tr:has-text('Case Reason') >> div.slds-checkbox_add-button")
        sleep(3)
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Next')")
        self.browser.click("div.modal-footer >> button.slds-button:text-is('Finish')")
        sleep(10)


    def messaging_components_setup(self):
        """
        Runs the Messaging Components Setup
        """
        iframe_handler = self.shared.iframe_handler()

        # define the attributes of 3 message components
        list_of_msgs = [
            {
                "name": "ConversationAcknowledgement",
                "developer_name": "SDO_Messaging_ConversationAcknowledgement",
                "msg": "Hello, thanks for reaching out. We will be with you shortly.",
                "description": "Opening conversation acknowledgment"
            },
            {
                "name": "StartConversation",
                "developer_name": "SDO_Messaging_StartConversation",
                "msg": "You are now connected to an agent, thank you for waiting.",
                "description": "Start conversation text, and picks up when someone accepts the work."
            },
            {
                "name": "EndConversation",
                "developer_name": "SDO_Messaging_EndConversation",
                "msg": "Thanks for contacting us today. Have a great day.",
                "description": "This displays when the conversation has ended"
            },
            {
                "name": "InactiveConversation",
                "developer_name": "SDO_Messaging_InactiveConversation",
                "msg": "Looks like you have left the conversation. Ending conversation.",
                "description": "This displays when the conversation is inactive"
            }
        ]

        for one_msg in list_of_msgs:
            # Make sure we are on Messaging Components page
            self.shared.go_to_setup_admin_page("ConversationMessageDefinitions/home")
            self.browser.wait_for_elements_state("h1:has-text('Messaging Components')", ElementState.visible, '30s')
            sleep(5)
            
            # Check that Component is not already present
            if self.browser.get_element_count(f"tbody >> th[data-label='Name'] >> a:text-is('{one_msg['name']}')") == 0:
                self.shared.click_button_with_text("New Component")
                self.shared.click_button_with_text("Next")
                sleep(1)
                self.browser.click("div.slds-visual-picker__figure:has-text('Auto-Response')")
                sleep(1)
                self.shared.click_button_with_text("Next")
                self.browser.fill_text(f"{iframe_handler} textarea[name='Title']",one_msg["msg"])
                sleep(1)
                self.shared.click_button_with_text("Next")
                self.browser.fill_text(f"{iframe_handler} input[name='label']",one_msg["name"])
                self.browser.fill_text(f"{iframe_handler} input[name='fullName']",one_msg["developer_name"])
                self.browser.fill_text(f"{iframe_handler} textarea[name='description']",one_msg["description"])
                self.shared.click_button_with_text("Done")
                sleep(4)
            else:
                print(f"Conversation '{one_msg['name']}' Component Already Exists")

        return
    
    def add_messaging_channel(self, channel_name: str = None):

        if not channel_name:
            return

        self.shared.go_to_setup_admin_page("LiveMessageSetup/home")
        self.browser.wait_for_elements_state("table[aria-label='All messaging channels']", ElementState.visible, "15s")

        # Check if channel is already present
        if self.browser.get_element_count(f"table[aria-label='All messaging channels'] >> th >> a:text-is('{channel_name}')") == 0:
            
            # Add New Channel
            self.browser.click("button:text-is('New Channel'):visible")
            sleep(2)
            self.browser.click("button:text-is('Start'):visible")
            sleep(2)
            self.browser.click("p[title='Messaging for In-App and Web']")
            sleep(1)
            self.browser.fill_text("div[data-aura-class='setup_serviceLsfContent'] >> :nth-match(input.slds-input:visible, 1)", channel_name)
            self.browser.click("label:text-is('Developer Name')")
            sleep(2)
            self.browser.click("button:text-is('Save'):visible")
            sleep(3)
        
            # Setup Initial Settings for Channel
            self.browser.click("lightning-combobox[data-element-name='RoutingType'] >> lightning-base-combobox.slds-combobox_container")
            self.browser.click("lightning-base-combobox-item[data-value='Omni-Flow']")
            sleep(1)
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='FlowLookup'] >> input", "SDO Service")
            self.browser.click("lightning-base-combobox-formatted-text[title='SDO Service - MIAW Omni-Flow']")
            sleep(1)
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='FallbackQueueLookup'] >> input", "Messaging")
            self.browser.click("lightning-base-combobox-formatted-text[title='Messaging']")
            sleep(1)
            self.browser.scroll_to_element("button:text-is('Save')")
            sleep(1)
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='InitialResponseLookup'] >> input", "ConversationAcknowledgement")
            self.browser.click("lightning-base-combobox-formatted-text[title='ConversationAcknowledgement']")
            sleep(1)
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='EngagedResponseLookup'] >> input", "StartConversation")
            self.browser.click("lightning-base-combobox-item:has-text('StartConversation'):visible")
            sleep(1)
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='ConversationEndResponseLookup'] >> input", "EndConversation")
            self.browser.click("lightning-base-combobox-item:has-text('EndConversation'):visible")
            sleep(1)
            self.browser.click("lightning-grouped-combobox[data-element-name='EndUserInactiveResponseLookup']")
            self.browser.fill_text("lightning-grouped-combobox[data-element-name='EndUserInactiveResponseLookup'] >> input", "inactive")
            self.browser.click("lightning-base-combobox-item:has-text('InactiveConversation'):visible")
            sleep(1)
            self.browser.click("button:text-is('Save')")

            # Go to Channel Page and Setup
            channel_id_result = self.salesforceapi.soql_query(f"SELECT Id from MessagingChannel where MasterLabel = '{channel_name.replace('&amp;', '&')}'")
            if channel_id_result and channel_id_result['totalSize'] > 0:
                self.shared.go_to_setup_admin_page(f"LiveMessageSetup/{channel_id_result['records'][0]['Id']}/view")

                # Add Parameter Mappings
                mappings = [
                    {
                        "ParameterName": "First Name",
                        "FlowVariable": "firstName"
                    },
                    {
                        "ParameterName": "Last Name",
                        "FlowVariable": "lastName"
                    },
                    {
                        "ParameterName": "Email",
                        "FlowVariable": "email"
                    },
                    {
                        "ParameterName": "Subject",
                        "FlowVariable": "subject"
                    }
                ]

                new_button_selector = "header:has-text('Parameter Mappings') >> button:has-text('New')"
                modal_selector = "div.slds-modal__container:has-text('New Parameter Mapping')"

                for mapping in mappings:

                    # Check Mapping Is Not Already Present
                    if self.browser.get_element_count("lightning-card:has-text('Parameter Mappings') >> table") > 0:
                        if self.browser.get_element_count(f"lightning-card:has-text('Parameter Mappings') >> table >> th[data-label='Parameter Name']:has-text('{mapping['ParameterName']}')") > 0:
                            continue
                    
                    # Create New Mapping
                    self.browser.click(new_button_selector)
                    self.browser.click(f"{modal_selector} >> lightning-grouped-combobox >> input")
                    sleep(1)
                    self.browser.click(f"lightning-base-combobox-item:has-text('{mapping['ParameterName']}'):visible", )
                    sleep(1)
                    self.browser.fill_text(f"{modal_selector} >> lightning-input >> input.slds-input", mapping["FlowVariable"])
                    sleep(1)
                    self.browser.click("button:text-is('Save'):visible")
                    sleep(2)

                # Activate Channel
                if self.browser.get_element_count("button:text-is('Activate')") > 0:
                    self.browser.click("button:text-is('Activate')")
                    sleep(2)

                    if self.browser.get_element_count("lightning-modal:has-text('Terms and Conditions')") > 0:
                        sleep(1)
                        self.browser.click("lightning-modal:has-text('Terms and Conditions') >> label:has-text('By checking this box or accessing or using Messaging for In-App and Web')")
                        sleep(2)
                        self.browser.click("button:text-is('Accept'):visible")
                        sleep(1)
