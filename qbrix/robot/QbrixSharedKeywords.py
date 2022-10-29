import json
from time import sleep
from datetime import datetime
from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI


class QbrixSharedKeywords(BaseLibrary):

    def __init__(self):
        super().__init__()
        self._browser = None
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
        """ Creates the Chat Button and Invitations with Defaulls of *Standard Chat Button and SDO_Service_Chat """
        self.create_a_chat_button_and_automated_invitations("*Standard Chat Button","SDO_Service_Chat")


    def create_a_chat_button_and_automated_invitations(self, buttonName:str, buttonAPIName:str):
        sleep(3)
        """ Creates the Chat Button and Invitations """
        if buttonName is None:
            raise Exception("buttonName must be specified")
        if buttonAPIName is None:
            raise Exception("buttonAPIName must be specified")
        self.go_to_setup_admin_page("LiveChatButtonSettings/home")
        self.browser.wait_for_elements_state("iframe >>> h1:has-text('Chat Buttons')", ElementState.visible, '60s')
        sleep(5)
        visible = "visible" in self.browser.get_element_states(f"iframe >>> .listRelatedObject:has-text('{buttonName}')")
        if not visible:
            self.click_input_button_in_iframe_with_text('New')
            self.browser.wait_for_elements_state("iframe >>> h3:has-text('Basic Information')", ElementState.visible, '45')
            sleep(5)
            self.browser.select_options_by("iframe >>> select[name='j_id0:theForm:thePageBlock:editDataSection:editTypeItem:editType']", SelectAttribute.text,"Chat Button")       
            sleep(1)
            self.browser.fill_text("iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:nameSection:editMasterLabel']", buttonName)
            self.browser.fill_text("iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:developerNameSection:editDeveloperName']", '')
            sleep(1)
            self.browser.fill_text("iframe >>> input[name='j_id0:theForm:thePageBlock:editDataSection:developerNameSection:editDeveloperName']", buttonAPIName)
            sleep(2)
            if not "checked" in self.browser.get_element_states("iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout"):
                self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:hasChasitorIdleTimeout:hasChasitorIdleTimeout")
                sleep(1)
                #Customer Timeout
                self.browser.fill_text("iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id76:editChasitorIdleTimeout", "300")
                sleep(1)
                #Customer Timeout Warning
                self.browser.fill_text("iframe >>> id=j_id0:theForm:thePageBlock:editDataSection:j_id79:editChasitorIdleTimeoutWarning", "250")
                sleep(1)    
            self.browser.select_options_by("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:rountingTypeSection:editRoutingType", SelectAttribute.text, "Omni-Channel")
            sleep(2)
            self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:queueSection:editQueue_lkwgt")
            sleep(5)
            mainpage = self.browser.switch_page('NEW')
            sleep(2)
            self.browser.fill_text(":nth-match(frame,1) >>> xpath=//*[@id=\"lksrch\"]","Chat")
            sleep(1)
            button_to_click = self.browser.get_element(f":nth-match(frame,1) >>> input:has-text('Go!')")
            self.browser.click(button_to_click)
            sleep(3) 
            search_header = self.browser.get_element(":nth-match(frame,2) >>> xpath=//*[@id=\"new\"]/div/div[3]/div/div[2]/table/tbody/tr[2]/th")
            self.browser.click(search_header)
            sleep(5)
            self.browser.switch_page(mainpage)
            if not "checked" in self.browser.get_element_states("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue"):
                self.browser.click("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id192:editHasQueue")
                sleep(1)
                self.browser.fill_text("iframe >>> id=j_id0:theForm:thePageBlock:editRoutingSection:j_id195:editPerAgentQueueLength", "5")
                sleep(1)
            self.browser.click("iframe >>> :nth-match(.btn[value='Save'], 1)")
            sleep(8)

    def find_profileid_by_name(self,profilename:str):
        """ Locates the ID of a profile by friendly name """
        if profilename is None:
            raise Exception("Profile Name must be specified")
        
        results = self.salesforceapi.soql_query(f"SELECT ID FROM Profile where Name ='{profilename}'")
        
        #so this gets translated to a dict with 3 keys: 
        #records
        #totalSize
        #done
        
        if results["totalSize"] == 1:
            return results["records"][0]["Id"]
        
        return None
    
    def validate_minimal_rowcount(self,object,count,filter=None):
        '''Validate that the rows for the target object and filter do not go below the minimal count'''
        
        if object is None:
            raise Exception("A target object must be specified")
        
        if count is None:
            raise Exception("A minimal count must be specified")
        
        foundcnt = self.find_record_count(object,filter=None)
        
        if( not foundcnt>=int(count)):
            raise Exception(f"A minimal count not met. Expected was: {count} and found count was {foundcnt}")
        
        pass
    
     
    def validate_exact_rowcount(self,object,count,filter=None):
        
        '''Validate that the rows for the target object and filter match the expected count'''
        
        if object is None:
            raise Exception("A target object must be specified")
        
        if count is None:
            raise Exception("A minimal count must be specified")
        
        foundcnt = self.find_record_count(object,filter)
        
        if( not foundcnt==int(count)):
            raise Exception(f"An exact count not met. Expected was: {count} and found count was {foundcnt}")
        
        pass
    
    def validate_maximum_rowcount(self,object,count,filter=None):
        '''Validate that the rows for the target object and filter do not exceed the expected count'''
        
        if object is None:
            raise Exception("A target object must be specified")
        
        if count is None:
            raise Exception("A minimal count must be specified")
        
        foundcnt = self.find_record_count(object,filter)
        
        if( foundcnt>int(count)):
            raise Exception(f"A max count not met. Expected was: {count} and found count was {foundcnt}")
        
        pass
    
    
    def validate_range_rowcount(self,object,lowercount,uppercount,filter=None):
        '''Validate the count of the rows for the specified object and filter is >= lower value and <= upper value'''
        
        if object is None:
            raise Exception("A target object must be specified")
        
        if lowercount is None:
            raise Exception("A lower count must be specified")
        
        if uppercount is None:
            raise Exception("As upper count must be specified")
        
        foundcnt = self.find_record_count(object,filter)
        
        if( not foundcnt>=int(lowercount) or not foundcnt<=int(uppercount)):
            raise Exception(f"A range count not met. Expected Range was between {lowercount} and {uppercount} and the found count was {foundcnt}")
        
        pass

    def find_record_count(self,object,filter=None):
        '''Locate the record count for the target object and given filter'''
        
        if object is None:
            raise Exception("A target object must be specified")
        
        soql = f"select count(Id) from {object}"
        
        if not filter is None and filter != "":
            soql = f"{soql} where ({filter})"
            
        results = self.salesforceapi.soql_query(soql)
        
        #so this gets translated to a dict with 3 keys: 
        #records
        #totalSize
        #done
        
        if results["totalSize"] == 1:
            return int(results["records"][0]["expr0"])
        
        return None

    def log_to_file(self,data):
        '''Use this for local debugging to write data to a temp file'''
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with open(f"temp.log", "a") as tmpFile:
            tmpFile.write(f"{dt_string}::{data}\n")
            tmpFile.close()

    def add_service_presence_statuses_to_profile(self,profilename:str,servicestatus:str):
        
        """ Adds a specified service presence to the specified profile """
        if profilename is None:
            raise Exception("Profile Name must be specified")
        if servicestatus is None:
            raise Exception("Service Status must be specified")
        
        self.go_to_setup_admin_page("EnhancedProfiles/home")
        sleep(10)
        profileid = self.find_profileid_by_name(profilename)
        
        if profileid is None:  
            raise Exception(f"The Profile Name: {profilename} cannot be located.")
        
        if(profileid is None):
            raise Exception("Unable to locate the Profile ID by name")
        
        profileediturl =f"EnhancedProfiles/page?address=%2F{profileid}%3Fs%3DServicePresenceStatusAccess"
        
        self.go_to_setup_admin_page(profileediturl)
        sleep(5)
        self.browser.click("iframe >>> a:has-text('Edit')")
        sleep(10)        
        self.browser.select_options_by(f"iframe >>> td.selectCell:has-text('{servicestatus}') >> select", SelectAttribute.text, servicestatus)
        self.browser.click("iframe >>> img.rightArrowIcon")
        sleep(1)
        self.browser.click("iframe >>> .btn:text-is('Save')")

    # -----------------------------------------------------------------------------------------------------------------------------------------
    # Chat Agent Configurations
    # -----------------------------------------------------------------------------------------------------------------------------------------
    def add_profile_to_chat_configuration(self,liveagentconfigname:str,profilename:str):
        """ Adds a specified profile to the specified Chat User Config  """
        
        if profilename is None:
            raise Exception("Profile Name must be specified")
        
        if liveagentconfigname is None:
            raise Exception("Live Chat User Config Name must be specified")
        
    
        self.go_to_setup_admin_page("EnhancedProfiles/home")
        sleep(10)
        
        liveagentconfig = self.find_livechatuserconfig_by_name(liveagentconfigname)
        editurl =f"LiveChatUserConfigSettings/page?address=%2F{liveagentconfig}"
        self.go_to_setup_admin_page(editurl)
        sleep(5)
        self.browser.click("iframe >>> .btn:text-is('Edit')")
        sleep(10)
    
        self.browser.select_options_by(f"iframe >>> td.selectCell:has-text('{profilename}') >> select", SelectAttribute.text, profilename)
        #there are 5 dueling lists. second one is profiles
        self.browser.click("iframe >>> :nth-match(img.rightArrowIcon, 2)")
        sleep(1)
        #button at top and one on the bottom. dealer's choice
        self.browser.click("iframe >>> :nth-match(.btn:text-is('Save'), 1)")
        
        
        
        
    def find_livechatuserconfig_by_name(self,configname:str):
        """ Locates the ID of a Live Chat User Config by Master Label. See: select id, MasterLabel from LiveChatUserConfig"""
        if configname is None:
            raise Exception("Live Chat User Config Name must be specified")
        
        soql=f"SELECT ID FROM LiveChatUserConfig where MasterLabel ='{configname}'"
        self.log_to_file(soql)
        results = self.salesforceapi.soql_query(soql)
        
        #so this gets translated to a dict with 3 keys: 
        #records
        #totalSize
        #done
        self.log_to_file(results)
        if results["totalSize"] == 1:
            return results["records"][0]["Id"]
        
        return None