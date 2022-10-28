from time import sleep

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary


class QbrixSharedKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def go_to_lightning_setup_home(self):
        """ Goes directly to setup home page in Lightning UI """
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/setup/SetupOneHome/home")
        self.browser.wait_for_elements_state("h1:has-text('Home')", ElementState.visible, '30s')

    def set_org_wide_email(self):
        """ Sets and org wide email address for the target org, defaulting to the sdo address """
        self.go_to_setup_admin_page("OrgWideEmailAddresses/home")
        self.browser.wait_for_elements_state(
            f"iframe >>> h2:text-is('Organization-Wide Email Addresses for User Selection and Default No-Reply Use')",
            ElementState.visible, '10s')
        email_address_check = "visible" in self.browser.get_element_states(
            "iframe >>> td:has-text('sdo@salesforce.com')")
        if not email_address_check:
            self.browser.click("iframe >>> .btn:has-text('Add')")
            sleep(2)
            self.browser.fill_text("iframe >>> tr:has-text('Display Name') >> input", "Default Email")
            self.browser.fill_text("iframe >>> tr:has-text('Email Address') >> input", "sdo@salesforce.com")
            self.browser.select_options_by("iframe >>> tr:has-text('Purpose') >> select", SelectAttribute.text,
                                           "User Selection and Default No-Reply Address")
            self.browser.click("iframe >>> :nth-match(.btn:text-is('Save'), 1)")
            sleep(2)

    def go_to_setup_admin_page(self, setup_page_url):
        """ Browses to a lightning setup URL, provide everything after lightning/setup/ in the URL """
        if setup_page_url is None:
            raise Exception("URL Text must be specified")
        if "lightning/setup" in setup_page_url:
            startpos = setup_page_url.find('lightning/setup/') + len('lightning/setup/')
            endpos = len(setup_page_url)
            setup_page_url = setup_page_url[startpos:endpos]
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/setup/{setup_page_url}")
        sleep(2)

    def set_lightning_toggle(self, new_state):
        """ Toggles a Salesforce Lightning Toggle either on or off """
        if new_state is None:
            raise Exception("State for the lightning toggle must be specified. State should be 'on' or 'off'.")
        if new_state.lower() not in ("on", "off"):
            raise Exception("define a state of 'on' or 'off'")
        visible = "visible" in self.browser.get_element_states("label:has-text('Off')")
        if visible and new_state.lower() == "on":
            toggle_switch = self.browser.get_element("label:has-text('Off')")
            self.browser.click(toggle_switch)
            sleep(1)
        if not visible and new_state.lower() == "off":
            visible = "visible" in self.browser.get_element_states("label:has-text('On')")
            if visible:
                toggle_switch = self.browser.get_element("label:has-text('On')")
                self.browser.click(toggle_switch)
                sleep(1)

    def click_button_with_text(self, button_text):
        """ Finds a button using the button text and clicks it providing it is visible on the page. You must define
        the text for the label on the button. """

        if button_text is None:
            raise Exception("Button Text must be specified")
        visible = "visible" in self.browser.get_element_states(f"button:has-text('{button_text}')")
        if visible:
            button_to_click = self.browser.get_element(f"button:has-text('{button_text}')")
            self.browser.click(button_to_click)
            sleep(1)

    def click_button_in_frame_with_text(self, button_text):
        """ Finds a button using the button text and clicks it providing it is visible on the page within an iframe.
        You must define the text for the label on the button. """

        if button_text is None:
            raise Exception("Button Text must be specified")
        visible = "visible" in self.browser.get_element_states(
            f":nth-match(iframe,1) >>> button:has-text('{button_text}')")
        if visible:
            button_to_click = self.browser.get_element(f":nth-match(iframe,1) >>> button:has-text('{button_text}')")
            self.browser.click(button_to_click)
            sleep(1)

    def click_input_button_in_iframe_with_text(self, button_text):
        """ Finds a button using the button text and clicks it providing it is visible on the page within an iframe.
        You must define the text for the label on the button. """
        if button_text is None:
            raise Exception("Button Text must be specified")
        visible = "visible" in self.browser.get_element_states(
            f":nth-match(iframe,1) >>> input:has-text('{button_text}')")
        if visible:
            button_to_click = self.browser.get_element(f":nth-match(iframe,1) >>> input:has-text('{button_text}')")
            self.browser.click(button_to_click)
            sleep(1)

    def wait_for_page_title(self, page_title):
        """ Waits for a title on a lightning page to be loaded. Page Title needs to be passed in and is expected to
        be in an H1 element. """

        if page_title is None:
            raise Exception("No page title specified")
        self.browser.wait_for_elements_state(f"iframe >>> h1:text-is('{page_title}')", ElementState.visible, '10s')

    def enable_omnichannel_for_bot(self, button_name, queue_name):
        """ Sets a given Live Chat Button to Omni-Channel Routing with an associated Queue"""

        if button_name == '' or queue_name == '':
            raise Exception("Button Name and Queue Name must be specified")

        self.go_to_setup_admin_page("LiveChatButtonSettings/home")
        self.browser.click(f"iframe >>> a:text-is('{button_name}')")
        sleep(2)
        self.browser.click("iframe >>> .btn:has-text('Edit')")
        sleep(2)
        self.browser.select_options_by("iframe >>> tr:has-text('Routing Type') >> select", SelectAttribute.text,
                                       "Omni-Channel")
        sleep(2)
        self.browser.fill_text("iframe >>> tr:has-text('Queue') >> span.lookupInput >> input", f"{queue_name}")
        sleep(2)
        self.browser.click("iframe >>> :nth-match(.btn:has-text('Save'), 1)")
        sleep(2)

    def create_chat_button_and_automated_invitations(self):
        """ Creates the Chat Button and Invitations """

        sleep(5)
        self.go_to_setup_admin_page("LiveChatButtonSettings/home")
        sleep(5)
        visible = "visible" in self.browser.get_element_states(f"iframe >>> input:has-text('New')")
        sleep(5)
        if visible:

            self.click_input_button_in_iframe_with_text('New')
            sleep(5)

            # *************************************************************************************************************
            # Basic Information
            # *************************************************************************************************************
            # https://robocorp.com/docs/libraries/rpa-framework/rpa-browser-playwright/keywords#fill-text

            # Type
            self.browser.select_options_by(
                "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:editTypeItem:editType", SelectAttribute.text,
                "Chat Button")
            sleep(2)

            # Name
            self.browser.fill_text(
                "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:nameSection:editMasterLabel",
                "*Standard Chat Button")
            sleep(2)

            # Developer Name
            self.browser.fill_text(
                "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:developerNameSection:editDeveloperName",
                "SDO_Service_Chat")
            sleep(2)

            # Enable timeouts
            if not "checked" in self.browser.get_element_states(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout"):
                self.browser.click(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout")
                sleep(1)

                # Customer Timeout
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id76:editChasitorIdleTimeout", "300")
                sleep(1)

                # Customer Timeout Warning
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id79:editChasitorIdleTimeoutWarning",
                    "250")
                sleep(1)

            # *************************************************************************************************************
            # Routing Information
            # *************************************************************************************************************

            # Set routing type first
            # Routing Type
            self.browser.select_options_by(
                "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:rountingTypeSection:editRoutingType",
                SelectAttribute.text, "Omni-Channel")
            sleep(2)

            # *************************************************************************************************************
            # pop the lookup to get the queue
            # *************************************************************************************************************
            # //*[@id="j_id0:theForm:thePageBlock:editRoutingSection:queueSection:editQueue_lkwgt"]/img
            self.browser.click(
                "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:queueSection:editQueue_lkwgt")
            sleep(5)

            mainpage = self.browser.switch_page('NEW')

            sleep(2)

            # Search - first frame (2)
            # Search for Chat
            self.browser.fill_text(":nth-match(frame,1) >>> xpath=//*[@id=\"lksrch\"]", "Chat")

            sleep(1)

            button_to_click = self.browser.get_element(f":nth-match(frame,1) >>> input:has-text('Go!')")
            self.browser.click(button_to_click)

            sleep(3)

            # Grab the top one in the table - second frame (2)
            search_header = self.browser.get_element(
                ":nth-match(frame,2) >>> xpath=//*[@id=\"new\"]/div/div[3]/div/div[2]/table/tbody/tr[2]/th")
            self.browser.click(search_header)
            sleep(5)

            # go back to main
            self.browser.switch_page(mainpage)
            # *************************************************************************************************************

            # Enable Queue
            if not "checked" in self.browser.get_element_states(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue"):
                self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue")
                sleep(1)

                # Queue Size per Agent
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id195:editPerAgentQueueLength", "5")
                sleep(1)

        sleep(2)

        # save and go have a nice day
        # Save on the bottom - there are 2 on the page.
        self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:j_id5:bottom:save")

    def create_a_chat_button_and_automated_invitations(self, buttonName, buttonAPIName):
        sleep(3)
        """ Creates the Chat Button and Invitations """
        if buttonName is None:
            raise Exception("buttonName must be specified")
        if buttonAPIName is None:
            raise Exception("buttonAPIName must be specified")
        self.go_to_setup_admin_page("LiveChatButtonSettings/home")
        self.browser.wait_for_elements_state("iframe >>> h1:has-text('Chat Buttons')", ElementState.visible, '60s')
        sleep(5)
        visible = "visible" in self.browser.get_element_states(
            f"iframe >>> .listRelatedObject:has-text('{buttonName}')")
        if not visible:
            self.click_input_button_in_iframe_with_text('New')
            self.browser.wait_for_elements_state("iframe >>> h3:has-text('Basic Information')", ElementState.visible,
                                                 '45')
            sleep(5)
            self.browser.select_options_by(
                "iframe >>> select[name='j_id0:theForm:thePageBlock:editDataSection:editTypeItem:editType']",
                SelectAttribute.text, "Chat Button")
            sleep(1)
            self.browser.fill_text(
                "iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:nameSection:editMasterLabel']",
                buttonName)
            self.browser.fill_text(
                "iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:developerNameSection:editDeveloperName']",
                '')
            sleep(1)
            self.browser.fill_text(
                "iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:developerNameSection:editDeveloperName']",
                buttonAPIName)
            sleep(2)
            if not "checked" in self.browser.get_element_states(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout"):
                self.browser.click(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout")
                sleep(1)
                # Customer Timeout
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id76:editChasitorIdleTimeout", "300")
                sleep(1)
                # Customer Timeout Warning
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id79:editChasitorIdleTimeoutWarning",
                    "250")
                sleep(1)
            self.browser.select_options_by(
                "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:rountingTypeSection:editRoutingType",
                SelectAttribute.text, "Omni-Channel")
            sleep(2)
            self.browser.click(
                "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:queueSection:editQueue_lkwgt")
            sleep(5)
            mainpage = self.browser.switch_page('NEW')
            sleep(2)
            self.browser.fill_text(":nth-match(frame,1) >>> xpath=//*[@id=\"lksrch\"]", "Chat")
            sleep(1)
            button_to_click = self.browser.get_element(f":nth-match(frame,1) >>> input:has-text('Go!')")
            self.browser.click(button_to_click)
            sleep(3)
            search_header = self.browser.get_element(
                ":nth-match(frame,2) >>> xpath=//*[@id=\"new\"]/div/div[3]/div/div[2]/table/tbody/tr[2]/th")
            self.browser.click(search_header)
            sleep(5)
            self.browser.switch_page(mainpage)
            if not "checked" in self.browser.get_element_states(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue"):
                self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue")
                sleep(1)
                self.browser.fill_text(
                    "iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id195:editPerAgentQueueLength", "5")
                sleep(1)
            self.browser.click("iframe >>> :nth-match(.btn[value='Save'], 1)")
            sleep(8)
