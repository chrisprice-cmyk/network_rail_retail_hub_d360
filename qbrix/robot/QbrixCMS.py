from time import sleep
import os

from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI

class QbrixCMS(BaseLibrary):

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

    def go_to_digital_experiences(self):
      self.shared.go_to_app("Digital Experiences")

    def download_all_content(self):

      # Get Workspace Names
      results = self.salesforceapi.soql_query(f"SELECT Name FROM ManagedContentSpace WHERE IsDeleted=False")
      if results["totalSize"] == 0:
        return

      # Download content from each workspace
      for workspace in results["records"]:
        self.download_cms_content(workspace["Name"])


    def upload_cms_import_file(self, file_path, workspace):
      
      self.go_to_digital_experiences()
      sleep(5)

      #Go To Workspace Page
      if workspace:

        # Get the Application ID
        results = self.salesforceapi.soql_query(
            f"SELECT Id FROM ManagedContentSpace where Name = '{workspace}' LIMIT 1")

        if results["totalSize"] == 1:
          app_id = results["records"][0]["Id"]

          # Go to the app
          self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/spaces/{app_id}", timeout='30s')


          #Open Import Menu
          iframe_handler = self.shared.iframe_handler()
          drop_down_menu_selector = f"{iframe_handler} div.slds-page-header__row >> button.slds-button:has-text('Show menu')"
          import_button_selector = f"{iframe_handler} div.slds-page-header__row >> lightning-menu-item.slds-dropdown__item:has-text('Import Content')"

          self.browser.click(drop_down_menu_selector)
          sleep(1)
          upload_promise = self.browser.promise_to_upload_file(file_path)
          self.browser.click(import_button_selector)
          sleep(2)
          self.browser.click("div.modal-body >> span.slds-checkbox >> span.slds-checkbox_faux")
          sleep(1)
          self.browser.click("button.slds-button:has-text('Import')")
          sleep(5)
          self.browser.click("button.slds-button:has-text('ok')")
          sleep(2)
    
    def download_cms_content(self, workspace, directory=None):
      if not directory:
        directory = f"datasets/cmsfiles/{workspace}"

      os.makedirs(directory, exist_ok=True)  

      self.go_to_digital_experiences()
      sleep(5)

      #Go To Workspace Page
      if workspace:

        # Get the Application ID
        results = self.salesforceapi.soql_query(
            f"SELECT Id FROM ManagedContentSpace where Name = '{workspace}' LIMIT 1")

        if results["totalSize"] == 1:
          app_id = results["records"][0]["Id"]

          # Go to the app
          self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/spaces/{app_id}", timeout='30s')
          iframe_handler = self.shared.iframe_handler()

          # Enhanced workspace handler
          if self.browser.get_element_count(f"{iframe_handler} lightning-badge.slds-badge:has-text('Enhanced'):visible") > 0:
            return

          # Select all checkboxes

          while True:

            total_cms_elements = self.browser.get_element(f"{iframe_handler} p.slds-page-header__meta-text")

            if total_cms_elements:

              innertext_for_total = self.browser.get_property(f"{iframe_handler} p.slds-page-header__meta-text", "innerText")

              if innertext_for_total and "+" not in str(innertext_for_total):
                break

              if innertext_for_total and "+" in str(innertext_for_total):
                elements = self.browser.get_elements(f"{iframe_handler} table.slds-table >> sfdc_cms-content-check-box-button")
                for elem in elements:
                  self.browser.scroll_to_element(elem)

            else:
              break


          elements = self.browser.get_elements(f"{iframe_handler} table.slds-table >> sfdc_cms-content-check-box-button")
          for elem in elements:
            self.browser.scroll_to_element(elem)
            self.browser.click(elem)

          #Open Export Menu
          
          drop_down_menu_selector = f"{iframe_handler} div.slds-page-header__row >> button.slds-button:has-text('Show menu')"
          import_button_selector = f"{iframe_handler} div.slds-page-header__row >> lightning-menu-item.slds-dropdown__item:has-text('Export Content')"

          self.browser.click(drop_down_menu_selector)
          sleep(1)
          
          self.browser.click(import_button_selector)
          sleep(2)
          self.browser.click(f"{iframe_handler} button.slds-button:has-text('Export')")
          sleep(5)
      

    def create_workspace(self, workspace_name, channels=[], enhanced_workspace = True):

      # Check for existing workspace
      results = self.salesforceapi.soql_query(f"SELECT Id FROM ManagedContentSpace where Name = '{workspace_name}' LIMIT 1")

      if results["totalSize"] == 1:
        print("Workspace exists already, skipping.")
        return

      # Go to Digital Experience Home and initiate Workspace creation
      self.go_to_digital_experiences()
      sleep(3)
      self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/cms/home/", timeout='30s')
      sleep(3)
      self.browser.click(f"{self.shared.iframe_handler()} span.label:text-is('Create a CMS Workspace'):visible")

      # Enter initial information
      sleep(2)
      self.browser.click("lightning-input:has-text('Name') >> input.slds-input")
      self.browser.fill_text("lightning-input:has-text('Name') >> input.slds-input", workspace_name)

      # Handle enhanced workspace option
      if enhanced_workspace:
        self.browser.click("span.slds-text-heading_medium:text-is('Enhanced CMS Workspace')")

      # Handle Channel Selection
      self.browser.click("button.nextButton:visible")
      sleep(2)
      if len(channels) > 0:
        for channel in channels:
          if self.browser.get_element_count(f"tr.slds-hint-parent:has-text('{channel}')"):
            self.browser.click(f"tr.slds-hint-parent:has-text('{channel}') >> div.slds-checkbox_add-button")
      else:
        for checkbox_add_button in self.browser.get_elements("div.slds-checkbox_add-button"):
          self.browser.click(checkbox_add_button)

      # Handle Contributors
      self.browser.click("button.nextButton:visible")
      sleep(2)
      for checkbox_add_button in self.browser.get_elements("div.forceSelectableListViewSelectionColumn"):
          self.browser.click(checkbox_add_button)

      # Handle Contributer Access Levels
      self.browser.click("button.nextButton:visible")
      sleep(2)
      for combo_box in self.browser.get_elements("lightning-picklist:visible"):
        self.browser.click(combo_box)
        sleep(1)
        self.browser.click("span.slds-listbox__option-text:has-text('Content Admin'):visible")

      # Handle Language
      self.browser.click("button.nextButton:visible")
      sleep(2)
      
      if not enhanced_workspace:
        self.browser.click("button.slds-button:has-text('Move selection to Selected'):visible")
        self.browser.click("lightning-combobox.slds-form-element:has-text('Default Language'):visible")
        self.browser.click("lightning-base-combobox-item:has-text('English (United States)'):visible")

      # Complete Screen
      self.browser.click("button.nextButton:visible")
      sleep(1)
      self.browser.click("button.nextButton:visible")



      

