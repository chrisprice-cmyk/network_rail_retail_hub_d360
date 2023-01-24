import json
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

    def generate_product_media_file(self):

      # Get All Active Products which have attached ElectronicMedia
      results = self.salesforceapi.soql_query(f"SELECT Id, External_ID__c, Name from Product2 WHERE Id IN (Select ProductId from ProductMedia)")

      if results["totalSize"] == 0:
          print("No Products found with attached media")
          return

      result_dict = {}
      self.shared.go_to_app("Commerce - Admin")

      for product in results["records"]:

        product_dict = {}

        #Set External ID
        product_dict.update({"External_ID__c": product["External_ID__c"]})
        

        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/r/Product2/{product['Id']}/view", timeout='30s')
        sleep(4)

        self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")
        sleep(10)

        # Get Product Detail Images (Max. 8)
        if self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") > 0:
          product_detail_image_list = []
          product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible")
          if product_detail_images:
            for prod in product_detail_images:
              prod_property = self.browser.get_property(prod, "alt")
              if prod_property:
                print(prod_property)
                product_detail_image_list.append(prod_property)

          if len(product_detail_image_list) > 0:
            product_dict.update({"ProductDetailImages": product_detail_image_list})

        # Get Product List Image (Max. 1)
        if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") > 0:
          product_image_list = []
          product_images = self.browser.get_elements(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible")
          if product_images:
            for prod in product_images:
              prod_property = self.browser.get_property(prod, "alt")
              if prod_property:
                print(prod_property)
                product_image_list.append(prod_property)

          if len(product_image_list) > 0:
            product_dict.update({"ProductImages": product_image_list})


        # Get Attachments (Max. 5)
        if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") > 0:
          attachment_list = []
          attachment_images = self.browser.get_elements(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text")
          if attachment_images:
            for prod in attachment_images:
              prod_property = self.browser.get_property(prod, "title")
              if prod_property:
                print(prod_property)
                attachment_list.append(prod_property)

          if len(attachment_list) > 0:
            product_dict.update({"Attachments": attachment_list})

        self.browser.click(f"li.oneConsoleTabItem:has-text('{product['Name']}'):visible >> div.close")

        result_dict.update({f"Product_{product['External_ID__c']}": product_dict})

      # Save dict to file
      if not os.path.exists("cms_data"):
        os.makedirs("cms_data", exist_ok=True)  

      with open("cms_data/product_images.json", "w") as save_file:
        json.dump(result_dict, save_file, indent=2)
              
    def reassign_product_media_files(self):

      if not os.path.exists("cms_data/product_images.json"):
        print("Missing CMS Definition File. Location: cms_data/product_images.json")
        return

      with open("cms_data/product_images.json", "r") as cms_file:
        product_dict = json.load(cms_file)

      if product_dict:
        for product in dict(product_dict).items():

          if product[1]['External_ID__c'] != "Product2.001":
            continue
          
          results = self.salesforceapi.soql_query(f"SELECT Id, External_ID__c, Name from Product2 WHERE External_ID__c = '{product[1]['External_ID__c']}' LIMIT 1")

          if results["totalSize"] == 0:
              print("No Products found")
              continue

          self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/r/Product2/{results['records'][0]['Id']}/view", timeout='30s')
          sleep(4)

          self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")
          sleep(5)
          
          # Product Detail Images
          if "ProductDetailImages" in dict(product[1]).keys():
            
            for product_detail_image in list(product[1]["ProductDetailImages"]):

              if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") == 8:
                  continue

              skip = False
              if self.browser.get_element_count(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible") > 0:
                product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Product Detail Images'):visible >> img.fileCardImage:visible")
                if product_detail_images:
                  for prod in product_detail_images:
                    prod_property = self.browser.get_property(prod, "alt")
                    if prod_property:
                      if prod_property in list(product[1]["ProductDetailImages"]):
                        skip = True

              if skip:
                continue

              self.browser.click("article.slds-card:has-text('Product Detail Images'):visible >> button.slds-button:text-is('Add Image')")
              sleep(7)
              self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", product_detail_image)
              sleep(2)
              
              search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{product_detail_image}'):visible")

              if len(search_results) == 0:
                self.browser.click(f"button.slds-button:text-is('Cancel')")
                sleep(2)
                continue

              if len(search_results) > 0:
                self.browser.click("tr:has(span:text-matches('^{}$')) >> th >> span.slds-checkbox_faux".format(product_detail_image))
                      
              sleep(1)
              self.browser.click(f"button.slds-button:text-is('Save')")
              sleep(5)
              self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")

          # Product Images
          if "ProductImages" in dict(product[1]).keys():
            
              for product_image in list(product[1]["ProductImages"]):

                skip = False

                if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") == 1:
                  continue

                if self.browser.get_element_count(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible") > 0:
                  product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Product List Image'):visible >> img.fileCardImage:visible")
                  if product_detail_images:
                    for prod in product_detail_images:
                      prod_property = self.browser.get_property(prod, "alt")
                      if prod_property:
                        if prod_property in list(product[1]["ProductImages"]):
                          skip = True

                if skip:
                  continue

                self.browser.click("article.slds-card:has-text('Product List Image'):visible >> button.slds-button:text-is('Add Image')")
                sleep(7)
                self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", product_image)
                sleep(2)
                
                search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{product_image}'):visible")

                if len(search_results) == 0:
                  self.browser.click(f"button.slds-button:text-is('Cancel')")
                  sleep(2)
                  continue

                if len(search_results) > 0:
                  self.browser.click("tr:has(span:text-matches('^{}$')) >> th >> span.slds-checkbox_faux".format(product_image))
                        
                sleep(1)
                self.browser.click(f"button.slds-button:text-is('Save')")
                sleep(5)
                self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")

          # Attachments
          if "Attachments" in dict(product[1]).keys():
           
              for attachment in list(product[1]["Attachments"]):

                if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") == 5:
                  continue

                skip = False
                if self.browser.get_element_count(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text") > 0:
                  product_detail_images = self.browser.get_elements(f"article.slds-card:has-text('Attachments'):visible >> span.slds-file__text")
                  if product_detail_images:
                    for prod in product_detail_images:
                      prod_property = self.browser.get_property(prod, "title")
                      if prod_property:
                        if prod_property in list(product[1]["Attachments"]):
                          skip = True

                if skip:
                  continue

                self.browser.click("article.slds-card:has-text('Attachments'):visible >> button.slds-button:text-is('Add Attachment')")
                sleep(7)
                self.browser.fill_text("sfdc_cms-content-uploader-header.slds-col:visible >> input.slds-input", attachment)
                sleep(2)
                
                search_results = self.browser.get_elements(f"tr.slds-hint-parent:has-text('{attachment}'):visible")

                if len(search_results) == 0:
                  self.browser.click(f"button.slds-button:text-is('Cancel')")
                  sleep(2)
                  continue

                if len(search_results) > 0:
                  self.browser.click("tr:has(span:text-matches('^{}$')) >> th >> span.slds-checkbox_faux".format(attachment))
                        
                sleep(1)
                self.browser.click(f"button.slds-button:text-is('Save')")
                sleep(5)
                self.browser.click(f"div.uiTabBar >> span.title:text-is('Media')")

