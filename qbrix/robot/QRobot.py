from time import sleep

from Browser import SupportedBrowsers
from robot.api.deco import library
from robot.libraries.BuiltIn import BuiltIn


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QRobot:
    """Initializes the Q Robot Browser"""

    def __init__(self):
        self._builtin = None
        self._cumulusci = None
        self._salesforce_api = None
        self._browser = None

    @property
    def salesforce_api(self):
        """Initiates the Salesforce API Connection"""
        if getattr(self, "_salesforce_api", None) is None:
            self._salesforce_api = self.builtin.get_library_instance(
                "cumulusci.robotframework.SalesforceAPI"
            )
        return self._salesforce_api

    @property
    def builtin(self):
        """Initiates the builtin methods"""
        if getattr(self, "_builtin", None) is None:
            self._builtin = BuiltIn()
        return self._builtin

    @property
    def cumulusci(self):
        """Initiates the methods for CumulusCI"""
        if getattr(self, "_cumulusci", None) is None:
            self._cumulusci = self.builtin.get_library_instance(
                "cumulusci.robotframework.CumulusCI"
            )
        return self._cumulusci

    @property
    def browser(self):
        """Initiates Browser"""
        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def open_q_browser(self, record_video=False):

        """Starts a new browser session with Chromium"""

        # Set Defaults for Browser Instance
        browser = self.builtin.get_variable_value("${BROWSER}", "chrome")
        headless = browser.startswith("headless")
        browser_type = browser[8:] if headless else browser
        browser_type = "chromium" if browser_type == "chrome" else browser_type
        browser_enum = getattr(SupportedBrowsers, browser_type, None)
        login_url = self.cumulusci.login_url()

        # Enable Video Recording (if requested)
        rec=None
        if record_video:
            rec={"dir": "../video"}

        # Open New Browser
        browser_id = self.browser.new_browser(browser=browser_enum, headless=headless)
        context_id = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}, recordVideo=rec
        )
        self.browser.set_browser_timeout("900 seconds")
        sleep(1)

        # Login to Org
        page_details = self.browser.new_page()

        retries = 0
        while retries < 4:
            try:
                self.browser.go_to(login_url, timeout="120s")
                sleep(1)
                if "lightning" in str(self.browser.get_url()):
                    break
            except Exception as e:
                print(e)
                self.browser.take_screenshot()
                retries += 1

        if retries >= 3:
            raise Exception("Unable to launch robot. Please try again.")

        # Browse to Setup Page if not there already
        if not str(self.browser.get_url()).endswith("/lightning/setup/SetupOneHome/home"):
            self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/setup/SetupOneHome/home", timeout="120s")

        return browser_id, context_id, page_details

    def close_q_browser(self):

        """Closes All Instances of Browser which have been launched within the session"""

        self.browser.close_browser("ALL")
