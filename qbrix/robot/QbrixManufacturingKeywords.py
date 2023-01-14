from time import sleep
from Browser import ElementState, SelectAttribute
from cumulusci.robotframework.base_library import BaseLibrary
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI


class QbrixManufacturingKeywords(BaseLibrary):

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

    def get_store_id(self, store_name):
        if store_name is None:
            raise Exception("Profile Name must be specified")

        results = self.salesforceapi.soql_query(f"SELECT Id from WebStore where Name = '{store_name}' LIMIT 1")

        if results["totalSize"] == 1:
            return results["records"][0]["Id"]

        return None

    def start_reindex(self, store_name):

        index_button_selector = ":nth-match(button.slds-button:text-is('Rebuild Index'):visible, 1)"
        index_confirmation_selector = ":nth-match(button.slds-button:text-is('Rebuild'):visible, 1)"

        # Go To Index Page
        store_id = self.get_store_id(store_name)
        if store_id:
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/page/commerceSearch?lightning__webStoreId={store_id}&ws=%2Flightning%2Fr%2FWebStore%2F{store_id}%2Fview")
            self.browser.wait_for_elements_state(index_button_selector, ElementState.visible, '10s')
            if "enabled" in self.browser.get_element_states(index_button_selector):
                self.browser.click(index_button_selector)
                sleep(2)
                self.browser.click(index_confirmation_selector)
                sleep(2)

    def enable_sales_agreements(self, store_name):
        """
        Enables Sales Agreement Setting in Salesforce Setup
        """
        enable_sa_toggle = "span.slds-checkbox_off"
        self.shared.go_to_setup_admin_page("SalesAgreementSettings/home")
        visible = "visible" in self.browser.get_element_states(enable_sa_toggle)
        if visible:
            self.browser.click(enable_sa_toggle)
            sleep(2)
