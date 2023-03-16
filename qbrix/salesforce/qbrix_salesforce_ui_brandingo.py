import base64
import json
import os
import pathlib
from abc import ABC
from cumulusci.tasks.sfdx import SFDXOrgTask
from cumulusci.core.tasks import BaseTask
from qbrix.tools.shared.qbrix_console_utils import init_logger
from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.core.config import ScratchOrgConfig
from qbrix.salesforce.qbrix_salesforce_tasks import salesforce_query

log = init_logger()

class Brandingo(BaseSalesforceApiTask, ABC):

  salesforce_task = True

  task_docs = """
  Upserts a Favorite (aka Bookmark) in the target org.
  """

  task_options = {
        "org": {
          "description": "Org Alias for the target org",
          "required": False
        },
        "theme": {
          "description": "The name of the theme to update. Defaults to Q Brix Theme",
          "required": False
        },
        "PrimaryColour": {
          "description": "Hex Code for the Primary Color",
          "required": False
        },
        "SecondaryColor": {
          "description": "Hex Code for the Secondary color",
          "required": False
        },
        "LogoPath": {
          "description": "Path to image file for the logo",
          "required": False
        }
  }

  def _init_options(self, kwargs):
    super(Brandingo, self)._init_options(kwargs)
    self.theme = self.options["theme"] if "theme" in self.options else "QBrix"
    self.PrimaryColour = self.options["PrimaryColour"] if "PrimaryColour" in self.options else None
    self.SecondaryColor = self.options["SecondaryColor"] if "SecondaryColor" in self.options else None
    self.LogoPath = self.options["LogoPath"] if "LogoPath" in self.options else None

  def _run_task(self):

    image_path = self.LogoPath

    # Upload the image file
    with open(image_path, "rb") as file:
        encoded_image = base64.b64encode(file.read()).decode("utf-8")
    logo_id = self.sf.ContentVersion.create({
        "Title": os.path.basename(image_path),
        "PathOnClient": image_path,
        "VersionData": encoded_image,
        "IsMajorVersion": True
    })["ContentDocumentId"]

    # Set the org logo and color settings
    org_settings = self.sf.Organization.get()
    org_settings["InstanceName"] = self.sf.sf_instance[:-3]
    org_settings["UiSkin"] = self.theme
    org_settings["DefaultBrandingSet"] = {
        "PrimaryColor": self.primary_color,
        "SecondaryColor": self.secondary_color,
        "SmallLogoId": logo_id,
        "MediumLogoId": logo_id,
        "LargeLogoId": logo_id
    }
    self.sf.Organization.update(self.sf.Organization.get()["Id"], org_settings)

          
