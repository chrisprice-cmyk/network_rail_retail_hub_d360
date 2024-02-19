from time import sleep

from Browser import ElementState
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixServiceKeywords(QbrixRobotTask):

    """Service Cloud Robot Keywords"""

    def enable_incident_management(self):
        """ " Enables Incident Management"""

        # Go To Incident Management Setup Page
        self.shared.go_to_setup_admin_page("IncidentManagement/home")

        # Check if Incident Management is enabled and if not, click the toggle to enable
        service_incident_management_toggle = (
            ":nth-match(label:has-text('Customer Service Incident Management'), 2)"
        )
        self.shared.wait_on_element(service_incident_management_toggle)
        checked = "checked" in self.browser.get_element_states(
            service_incident_management_toggle
        )
        if not checked:
            self.browser.click(service_incident_management_toggle)
            sleep(1)

    def enable_slack_integration(self):
        """Enables Slack Integration with the target org"""

        # Go To Slack Integration Page
        self.shared.go_to_setup_admin_page("SlackSetupAssistant/home", 5)

        # Check if already connected
        timeout_counter = 0
        while timeout_counter <= 15:
            disconnected_status_count = self.browser.get_element_count(
                "div.stage-description-toggle >> label:has-text('Unaccepted'):visible"
            )
            if disconnected_status_count > 0:
                self.builtin.log_to_console(
                    "\nSlack Integration has not been enabled. Completing setup steps..."
                )
                break

            connected_status_count = self.browser.get_element_count(
                "div.stage-description-toggle >> label:has-text('Accepted'):visible"
            )
            if connected_status_count > 0:
                self.builtin.log_to_console("\nSlack Integration Already Connected.")
                return

            sleep(1)
            timeout_counter += 1

        # If not already connected, click the option to connect and wait for the accepted label
        checked = "checked" in self.browser.get_element_states(
            "div.stage-description-toggle >> label:has-text('Unaccepted')"
        )
        if not checked:
            self.browser.click(
                "div.stage-description-toggle >> label:has-text('Unaccepted')"
            )
            self.browser.wait_for_elements_state(
                "div.stage-description-toggle >> label:has-text('Accepted')",
                ElementState.visible,
                "20s",
            )

    def enable_case_swarming(self):
        """Enables Case Swarming"""

        # Ensure Slack Integration is enabled
        self.builtin.log_to_console(
            "\nChecking that Slack Integration is enabled for the org and Service..."
        )
        self.enable_slack_integration()
        self.builtin.log_to_console("\nSlack Integration enabled.")

        # Go To Service Cloud for Slack Setup Page
        self.shared.go_to_setup_admin_page("SlackServiceApp/home")

        # Check and enable Service Cloud for Slack
        toggle_selector = "div.slds-media:has-text('Enable the Service Cloud for Slack App') >> lightning-input.slackServiceEnableToggle"
        self.shared.wait_on_element(toggle_selector)
        checked = "checked" in self.browser.get_element_states(toggle_selector)
        if not checked:
            self.browser.click(toggle_selector)
            sleep(3)

        self.builtin.log_to_console("\nSlack Integration enabled for Service Cloud.")

        # Go To Case Swarming Setup Page
        self.shared.go_to_setup_admin_page("CaseSwarming/home")
        self.builtin.log_to_console("\nOpened Case Swarming Setup Page")

        # Check and Enable Case Swarming
        self.builtin.log_to_console("\nChecking that Case Swarming is enabled.")
        case_swarming_toggle = (
            "div.slds-media:has-text('Turn On Swarming') >> label.slds-checkbox_toggle"
        )
        self.shared.wait_on_element(case_swarming_toggle)
        if "checked" not in self.browser.get_element_states(case_swarming_toggle):
            self.browser.click(case_swarming_toggle)
            sleep(2)
        self.builtin.log_to_console("\nCase Swarming enabled.")

        self.enable_slack_for_swarming(browse_to_setup_page=False)

        # Complete
        self.builtin.log_to_console("\nCase Swarming setup complete!")

    def enable_slack_for_swarming(self, browse_to_setup_page=True):
        """Enables Slack as the Case Swarming Collaboration Tool"""
        if browse_to_setup_page:
            self.shared.go_to_setup_admin_page("CaseSwarming/home")

        # Set default collaboration tool
        self.builtin.log_to_console("\nSetting default collaboration tool to Slack.")
        try:
            self.browser.click(
                "li.slds-setup-assistant__item:has-text('Swarm With a Collaboration Tool') >> button.slds-combobox__input"
            )
            self.shared.wait_and_click(
                "span.slds-truncate:has-text('Slack'):visible", timeout=3
            )
            self.builtin.log_to_console("\nSlack set as default tool.")
        except Exception as e:
            self.builtin.log_to_console(
                "\nUnable to set collaboration tool setting. Moving on."
            )

    def create_chat_button(self):
        """Creates a new Chat Button"""
        self.shared.go_to_setup_admin_page("LiveChatButtonSettings/home")
        sleep(4)
        self.browser.get_element_states(".button:has-text('New')")
        sleep(5)

    def enable_einstein_case_classification(self, model_type: str = "Case Classification"):
            self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home", 5)
            self.browser.reload()
            classification_toggle = (
                 "div.slds-tabs_scoped >> div.case-classification-pref >> lightning-input >> label.slds-checkbox_toggle"
             )
            self.shared.wait_on_element(classification_toggle)
            if "checked" not in self.browser.get_element_states(classification_toggle):
                self.browser.click(classification_toggle)
            else:
                self.builtin.log_to_console("\n einstein classification is already enabled")
                return
            sleep(60)
            self.builtin.log_to_console("\n Enabled einstein classification")

    def disable_einstein_case_classification(self, model_type: str = "Case Classification"):
            self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home", 5)
            self.browser.reload()
            classification_toggle = (
                 "div.slds-tabs_scoped >> div.case-classification-pref >> lightning-input >> label.slds-checkbox_toggle"
             )
            self.shared.wait_on_element(classification_toggle)
            if "checked" in self.browser.get_element_states(classification_toggle):
                self.browser.click(classification_toggle)
            else:
                self.builtin.log_to_console("\n einstein classification is already disabled")
                return
            modal_turnoff_button = (
                "div.modal-footer >> button.slds-button:has-text('Turn Off')"
            )
            self.shared.wait_and_click(modal_turnoff_button)
            sleep(3)
            self.builtin.log_to_console("\n Disabled einstein classification")

    def create_einstein_classification_model(self, model_name: str = None, model_type: str = None):
            """Creates an Einstein Classification Model

            Args:
                model_name (str): The label which you want to give to the model
                model_type (str): The type for the model. This should be either "Case Classification" or "Case Wrap-Up"
            """

            if not model_name:
                raise ValueError("No model name was provided.")

            if not model_type:
                raise ValueError("No model type was provided.")

            if model_type not in ("Case Wrap-Up", "Case Classification"):
                raise ValueError(
                    f"Model type was not one of the expected values (Note that this is case sensitive). You submitted {model_type} and the accepted values are 'Case Classification' or 'Case Wrap-Up'"
                )
            self.builtin.log_to_console(f"\n Creating Model {model_name}")
            # Go To Einstein Classification Setup Page
            self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home", 5)
            self.browser.reload()

            # Go To {Model Type} Tab
            if model_type == 'Case Classification':
                tab_element_no = 1
            else:
                tab_element_no = 2

            model_type_tab = (
                f"a.slds-tabs_scoped__link:has-text('{model_type}')"
            )
            self.shared.wait_and_click(model_type_tab)

            # Check if model has already been created
            if (
                self.browser.get_element_count(
                    f"td.modelName >> button:has-text('{model_name}')"
                )
                > 0
            ):
                self.builtin.log_to_console(f"\n{model_name} has already been defined")
                return

            # Specify App and Name for the Model
            new_model_button_selector = f":nth-match(button.slds-button:text-is('New Model'),{tab_element_no})"
            next_button_selector = "div.modal-footer >> button.slds-button:text-is('Next')"
            self.shared.wait_and_click(new_model_button_selector)
            self.browser.fill_text("label:has-text('Model Name')", model_name)
            self.browser.click("label:has-text('API Name')")
            self.shared.wait_and_click(next_button_selector)

            if self.browser.get_element_count("div.error:visible") > 0:
                self.builtin.log_to_console(f"{model_name} has already been created with the same api name. Skipping.")
                return

            self.shared.wait_and_click(next_button_selector)
            self.shared.wait_and_click(next_button_selector)
            self.shared.wait_and_click(
                "tr:has-text('Case Reason') >> div.slds-checkbox_add-button"
            )

            # Additional Settings for Case Wrap Up
            if model_type == "Case Wrap-Up":
                self.browser.click(
                    "tr:has-text('Case Type') >> div.slds-checkbox_add-button"
                )
                self.browser.click(
                    "tr:has-text('Escalated') >> div.slds-checkbox_add-button"
                )
                self.browser.click(
                    "tr:has-text('Priority') >> div.slds-checkbox_add-button"
                )

            # Complete Setup
            self.shared.wait_and_click(next_button_selector)
            self.shared.wait_and_click(
                "div.modal-footer >> button.slds-button:text-is('Finish')"
            )
            self.builtin.log_to_console(f"\n{model_name} has been created")
            sleep(2)
            self.browser.reload()

    def add_case_wrap_up_model(self, model_name: str = None):
            """Add Case Wrap Up Model"""

            self.create_einstein_classification_model(
                model_name=model_name, model_type="Case Wrap-Up"
            )

    def create_case_classification_model(self, model_name: str = None):
            """Create Case Classification"""

            self.create_einstein_classification_model(
                model_name=model_name, model_type="Case Classification"
            )

    def activate_einstein_case_classification_model(self, model_name: str = None, model_type: str = None, should_enable_toggle: str = None):
            #enabling and disabling toggle 
            if(should_enable_toggle == "Yes"):
                self.enable_einstein_case_classification(
                    model_type= model_type
                )
                self.disable_einstein_case_classification(
                    model_type= model_type
                )
                self.enable_einstein_case_classification(
                    model_type= model_type
                )
            else:
                self.shared.go_to_setup_admin_page("EinsteinCaseClassification/home", 5)
                self.browser.reload()
                
            model_type_tab = (
                f"a.slds-tabs_scoped__link:has-text('{model_type}')"
            )
            self.shared.wait_and_click(model_type_tab)

            #click on model name if exists and ready to activate
            if(self.browser.get_element_count(f"#modelTable tr:has(td.modelName button:text-is('{model_name}')) td.modelStatus:text-is('Ready to Activate')")):
                model_click = (
                    f"td.modelName >> button.slds-button:has-text('{model_name}')"
                )
                self.shared.wait_and_click(model_click)
                activate_button = (
                    "div.ccProgressStepButtons >> button.slds-button:has-text('activate')"
                )
                self.shared.wait_and_click(activate_button)

                modal_activate_button = (
                    "div.modal-footer >> button.slds-button:has-text('Activate')"
                )
                self.shared.wait_and_click(modal_activate_button)
                self.builtin.log_to_console(f"\n Activated {model_name} einstein classification")
                self.browser.reload()
            else:
                self.builtin.log_to_console(f"\n Model {model_name} is not present or already activated")

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
                "description": "Opening conversation acknowledgment",
            },
            {
                "name": "StartConversation",
                "developer_name": "SDO_Messaging_StartConversation",
                "msg": "You are now connected to an agent, thank you for waiting.",
                "description": "Start conversation text, and picks up when someone accepts the work.",
            },
            {
                "name": "EndConversation",
                "developer_name": "SDO_Messaging_EndConversation",
                "msg": "Thanks for contacting us today. Have a great day.",
                "description": "This displays when the conversation has ended",
            },
            {
                "name": "InactiveConversation",
                "developer_name": "SDO_Messaging_InactiveConversation",
                "msg": "Looks like you have left the conversation. Ending conversation.",
                "description": "This displays when the conversation is inactive",
            },
        ]

        for one_msg in list_of_msgs:
            # Make sure we are on Messaging Components page
            self.shared.go_to_setup_admin_page("ConversationMessageDefinitions/home")
            self.browser.wait_for_elements_state(
                "h1:has-text('Messaging Components')", ElementState.visible, "30s"
            )
            sleep(5)

            # Check that Component is not already present
            if (
                self.browser.get_element_count(
                    f"tbody >> th[data-label='Name'] >> a:text-is('{one_msg['name']}')"
                )
                == 0
            ):
                self.shared.click_button_with_text("New Component")
                self.shared.click_button_with_text("Next")
                sleep(2)
                self.browser.click(
                    "div.slds-visual-picker__figure:has-text('Auto-Response')"
                )
                sleep(2)
                self.shared.click_button_with_text("Next")
                self.browser.fill_text(
                    f"{iframe_handler} textarea[name='Title']", one_msg["msg"]
                )
                sleep(2)
                self.shared.click_button_with_text("Next")
                self.browser.fill_text(
                    f"{iframe_handler} input[name='label']", one_msg["name"]
                )
                self.browser.fill_text(
                    f"{iframe_handler} input[name='fullName']",
                    one_msg["developer_name"],
                )
                self.browser.fill_text(
                    f"{iframe_handler} textarea[name='description']",
                    one_msg["description"],
                )
                sleep(2)
                self.shared.click_button_with_text("Done")
                sleep(4)

                # if (
                #     self.browser.get_element_count(
                #         f"{iframe_handler} input[name='label']"
                #     )
                #     > 0
                # ):
                #     print(
                #         f"Conversation '{one_msg['name']}' API Name Component Already Exists"
                #     )
                #     self.shared.click_button_with_text("Close")
            else:
                self.builtin.log_to_console(
                    f"\nConversation '{one_msg['name']}' Component Already Exists"
                )

        return

    def add_messaging_channel(self, channel_name: str = None):
        if not channel_name:
            return

        self.shared.go_to_setup_admin_page("LiveMessageSetup/home")
        self.browser.wait_for_elements_state(
            "table[aria-label='All messaging channels']", ElementState.visible, "15s"
        )

        # Check if channel is already present
        if (
            self.browser.get_element_count(
                f"table[aria-label='All messaging channels'] >> th >> a:text-is('{channel_name}')"
            )
            == 0
        ):
            # Add New Channel
            self.browser.click("button:text-is('New Channel'):visible")
            sleep(2)
            self.browser.click("button:text-is('Start'):visible")
            sleep(2)
            self.browser.click("p[title='Messaging for In-App and Web']")
            sleep(1)
            self.browser.fill_text(
                "div[data-aura-class='setup_serviceLsfContent'] >> :nth-match(input.slds-input:visible, 1)",
                channel_name,
            )
            self.browser.click(
                ":nth-match(.activeStep label:text-is('Developer Name'):visible, 1)"
            )
            sleep(2)
            self.browser.click("button:text-is('Save'):visible")
            sleep(3)

            # Setup Initial Settings for Channel
            self.browser.click(
                "lightning-combobox[data-element-name='RoutingType'] >> lightning-base-combobox.slds-combobox_container"
            )
            self.browser.click("lightning-base-combobox-item[data-value='Omni-Flow']")
            sleep(1)
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='FlowLookup'] >> input",
                "SDO Service",
            )
            self.browser.click(
                "lightning-base-combobox-formatted-text[title='SDO Service - MIAW Omni-Flow']"
            )
            sleep(1)
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='FallbackQueueLookup'] >> input",
                "Messaging",
            )
            self.browser.click(
                "lightning-base-combobox-formatted-text[title='Messaging']"
            )
            sleep(1)
            self.browser.scroll_to_element("button:text-is('Save')")
            sleep(1)
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='InitialResponseLookup'] >> input",
                "ConversationAcknowledgement",
            )
            self.browser.click(
                "lightning-base-combobox-formatted-text[title='ConversationAcknowledgement']"
            )
            sleep(1)
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='EngagedResponseLookup'] >> input",
                "StartConversation",
            )
            self.browser.click(
                "lightning-base-combobox-item:has-text('StartConversation'):visible"
            )
            sleep(1)
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='ConversationEndResponseLookup'] >> input",
                "EndConversation",
            )
            self.browser.click(
                "lightning-base-combobox-item:has-text('EndConversation'):visible"
            )
            sleep(1)
            self.browser.click(
                "lightning-grouped-combobox[data-element-name='EndUserInactiveResponseLookup']"
            )
            self.browser.fill_text(
                "lightning-grouped-combobox[data-element-name='EndUserInactiveResponseLookup'] >> input",
                "inactive",
            )
            self.browser.click(
                "lightning-base-combobox-item:has-text('InactiveConversation'):visible"
            )
            sleep(1)
            self.browser.click("button:text-is('Save')")

            # Go to Channel Page and Setup
            channel_id_result = self.salesforceapi.soql_query(
                f"SELECT Id from MessagingChannel where MasterLabel = '{channel_name.replace('&amp;', '&')}'"
            )
            if channel_id_result and channel_id_result["totalSize"] > 0:
                self.shared.go_to_setup_admin_page(
                    f"LiveMessageSetup/{channel_id_result['records'][0]['Id']}/view"
                )

                # Add Parameter Mappings
                mappings = [
                    {"ParameterName": "First Name", "FlowVariable": "firstName"},
                    {"ParameterName": "Last Name", "FlowVariable": "lastName"},
                    {"ParameterName": "Email", "FlowVariable": "email"},
                    {"ParameterName": "Subject", "FlowVariable": "subject"},
                ]

                new_button_selector = (
                    "header:has-text('Parameter Mappings') >> button:has-text('New')"
                )
                modal_selector = (
                    "div.slds-modal__container:has-text('New Parameter Mapping')"
                )

                for mapping in mappings:
                    # Check Mapping Is Not Already Present
                    if (
                        self.browser.get_element_count(
                            "lightning-card:has-text('Parameter Mappings') >> table"
                        )
                        > 0
                    ):
                        if (
                            self.browser.get_element_count(
                                f"lightning-card:has-text('Parameter Mappings') >> table >> th[data-label='Parameter Name']:has-text('{mapping['ParameterName']}')"
                            )
                            > 0
                        ):
                            continue

                    # Create New Mapping
                    self.browser.click(new_button_selector)
                    self.browser.click(
                        f"{modal_selector} >> lightning-grouped-combobox >> input"
                    )
                    sleep(1)
                    self.browser.click(
                        f"lightning-base-combobox-item:has-text('{mapping['ParameterName']}'):visible",
                    )
                    sleep(1)
                    self.browser.fill_text(
                        f"{modal_selector} >> lightning-input >> input.slds-input",
                        mapping["FlowVariable"],
                    )
                    sleep(1)
                    self.browser.click("button:text-is('Save'):visible")
                    sleep(2)

                # Activate Channel
                if self.browser.get_element_count("button:text-is('Activate')") > 0:
                    self.browser.click("button:text-is('Activate')")
                    sleep(2)

                    if (
                        self.browser.get_element_count(
                            "lightning-modal:has-text('Terms and Conditions')"
                        )
                        > 0
                    ):
                        sleep(1)
                        self.browser.click(
                            "lightning-modal:has-text('Terms and Conditions') >> label:has-text('By checking this box or accessing or using Messaging for In-App and Web')"
                        )
                        sleep(2)
                        self.browser.click("button:text-is('Accept'):visible")
                        sleep(1)

    def enable_dialer(self):
        """ " Enables Dialer"""

        # Go To Setup Page
        self.shared.go_to_setup_admin_page("DialerSetupPage/home", 5)

        # Check if Enabled and enable if not already
        timeout_count = 0
        timeout_reached = False
        while timeout_count <= 30:
            disable_count = self.browser.get_element_count(
                "div.voiceSliderCheckBox:has-text('Dialer'):near(h2:has-text('Enable Dialer')) >> div.switchText:text-is('Disabled'):visible"
            )
            if disable_count == 1:
                self.builtin.log_to_console(
                    "\nDialer is not enabled. Continuing to enable Dialer."
                )
                break

            enabled_count = self.browser.get_element_count(
                "div.voiceSliderCheckBox:has-text('Dialer'):near(h2:has-text('Enable Dialer')) >> div.switchText:text-is('Enabled'):visible"
            )
            if enabled_count == 1:
                self.builtin.log_to_console("\nDialer already enabled. Skipping task.")
                return

            timeout_count += 1
            sleep(1)

        if not timeout_reached:
            self.browser.click(
                ".toggle:has-text('Disabled'):near(h2:text-is('Enable Dialer')) >> label"
            )
            sleep(3)
        else:
            raise Exception(
                "Unable to locate Dialer elements on page. Please review script."
            )

    def enable_dialer_call_recordings(self):
        """ " Enables Dialer Call Recordings"""

        # Go To Setup Page
        self.shared.go_to_setup_admin_page("DialerSetupPage/home", 5)

        # Check if Enabled and enable if not already
        timeout_count = 0
        timeout_reached = False
        while timeout_count <= 30:
            disable_count = self.browser.get_element_count(
                "div.voiceSliderCheckBox:has-text('Call Recording'):near(h3:has-text('Call Recording')) >> div.switchText:text-is('Disabled'):visible"
            )
            if disable_count == 1:
                self.builtin.log_to_console(
                    "\nCall Recordings is not enabled. Continuing to enable Call Recordings."
                )
                break

            enabled_count = self.browser.get_element_count(
                "div.voiceSliderCheckBox:has-text('Call Recording'):near(h3:has-text('Call Recording')) >> div.switchText:text-is('Enabled'):visible"
            )
            if enabled_count == 1:
                self.builtin.log_to_console(
                    "\nCall Recordings already enabled. Skipping task."
                )
                return

            timeout_count += 1
            sleep(1)

        if not timeout_reached:
            self.browser.click(
                "div.voiceSliderCheckBox:has-text('Call Recording'):near(h3:has-text('Call Recording')) >> label"
            )
            sleep(3)
        else:
            raise Exception(
                "Unable to locate Call Recordings elements on page. Please review script."
            )


    def enable_enhanced_omni_channel(self):
        """
        Enable Enhanced Omni-Channel
        """

        self.builtin.log_to_console("\nChecking Enhanced Omni-Channel...")

        # Go To Setup Page
        self.shared.go_to_setup_admin_page("OmniChannelSettings/home", 5)
        self.shared.wait_for_page_to_load()

        # Enable Enhanced Omni
        my_iframe_handler = self.shared.iframe_handler()
        if "visible" in self.browser.get_element_states(f"{my_iframe_handler} input[id='toggleScrt2RoutingConnect']"):
            self.builtin.log_to_console("\n -> Found Toggle")

            toggle_selector = f"{my_iframe_handler} label.slds-checkbox_toggle:has(input[id='toggleScrt2RoutingConnect'])"
            if "unchecked" in self.browser.get_element_states(toggle_selector):
                self.browser.click(toggle_selector)
                self.builtin.log_to_console("\n -> Clicked Toggle")

                self.shared.wait_and_click(
                    f"{self.shared.iframe_handler()} footer.slds-modal__footer  >> input.btn:has-text('Continue')",
                    post_click_sleep = 2
                )

                # if the org had Enhanced Omni-Channel turned on before and disabled again, you will not see this agreement checkbox and "accept" button again, let's skip it if this is the case.
                checkbox_selector = f"{my_iframe_handler} input[name='j_id0:scrt2Form:toggleAcceptAgreement']:visible"
                if not self.browser.get_element_count(checkbox_selector):
                    return

                self.shared.wait_and_toggle(checkbox_selector, True)
                
                self.browser.wait_for_elements_state(
                    f"{my_iframe_handler} footer.slds-modal__footer  >> input.btn:has-text('Accept')", ElementState.visible, "10s"
                )
                self.browser.click(
                    f"{self.shared.iframe_handler()} footer.slds-modal__footer  >> input.btn:has-text('Accept')"
                )