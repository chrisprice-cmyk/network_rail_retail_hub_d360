import json
from time import sleep
from typing import Union

import requests
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask
from qbrix.robot.QbrixServiceKeywords import QbrixServiceKeywords
from qbrix.tools.shared.qbrix_authentication import get_secure_setting


@library(scope="GLOBAL", auto_keywords=True, doc_format="reST")
class QbrixSlack(QbrixRobotTask):

    """Slack Keywords for Robot"""

    def __init__(self):
        super().__init__()
        self._service = None

    @property
    def service(self):
        """Loads Q Robot Service Keywords and Methods"""

        if self._service is None:
            self._service = QbrixServiceKeywords()
        return self._service

    def slack_message_using_webhook(
        self,
        webhook_url: str,
        channel: str,
        sender: str,
        text: str,
        icon_emoji: str = None,
        use_secure_setting=True,
    ):
        """Send message to Slack channel using webhook.

        Args:
            webhook_url (str): If use_secure_message is True (The default) then this should be the name of the secure message entry from Q Labs which holds the slack webhook URL. Otherwise this is the Slack webhook URL.
            channel: channel needs to exist in the Slack server
            sender: shown in the message post as sender
            text: text for the message post
            icon_emoji: icon for the message post, defaults to None
            use_secure_setting (bool): If True (the default) then this will lookup the webhook_url by name from Q labs, using the value passed in for the webhook url. Otherwise will use the given value for the webhook url as the webhook url in the request.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "channel": channel if "#" in channel else f"#{channel}",
            "username": sender,
            "text": text,
        }
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji

        if use_secure_setting:
            webhook_url = get_secure_setting(webhook_url)

        response = requests.post(
            webhook_url, headers=headers, data=json.dumps(payload), timeout=60
        )
        print(response.status_code)

    def slack_raw_message(
        self,
        webhook_url: str,
        message: Union[str, dict],
        channel: str = None,
        use_secure_setting=True,
    ):
        """Send Slack message by custom JSON content.

        Args:
            webhook_url (str): If use_secure_message is True (The default) then this should be the name of the secure message entry from Q Labs which holds the slack webhook URL. Otherwise this is the Slack webhook URL.
            channel: channel needs to exist in the Slack server
            message: dictionary or string defining message content and structure
            use_secure_setting (bool): If True (the default) then this will lookup the webhook_url by name from Q labs, using the value passed in for the webhook url. Otherwise will use the given value for the webhook url as the webhook url in the request.
        """
        headers = {"Content-Type": "application/json"}

        if use_secure_setting:
            webhook_url = get_secure_setting(webhook_url)

        if channel and isinstance(message, dict):
            message["channel"] = channel
        elif channel:
            self.builtin.log_to_console(
                "\nCan't set channel as 'json_data' is a string."
            )
            return

        data_for_message = message if isinstance(message, str) else json.dumps(message)
        response = requests.post(
            webhook_url, headers=headers, data=data_for_message, timeout=60
        )
        print(response.status_code)

    def go_to_slack_apps_setup(self):
        """Browses to the Slack Setup Assistant Page"""
        self.shared.go_to_setup_admin_page("SlackSetupAssistant/home")

    def enable_prm_for_slack(self):
        """Enables the settings on the Partner Relationship Management Setup Page"""

        self.shared.go_to_setup_admin_page("SlackSetupForPRM/home", 4)
        self.builtin.log_to_console("\nLoaded PRM for Slack Setup Page")

        # Review Documentation
        self.check_and_enable_slack_setting(
            setting_name="Documentation Review Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Review Documentation and Resources') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        # Review Set up Object Permissions
        self.check_and_enable_slack_setting(
            setting_name="Object Permissions Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Set up Object Permissions') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Set up Object Permissions'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Set up Object Permissions'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        # Review Manage Channel Search & Post Objects
        self.check_and_enable_slack_setting(
            setting_name="Manage Channel Search & Post Objects Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Manage Channel Search & Post Objects') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Manage Channel Search & Post Objects'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Manage Channel Search & Post Objects'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        # Review Slack Community Link
        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Share the PRM for Slack installation link with Community Administrators') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            self.check_and_enable_slack_setting(
                setting_name="PRM for Slack Community Link Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Share the PRM for Slack installation link with Community Administrators') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Share the PRM for Slack installation link with Community Administrators'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Share the PRM for Slack installation link with Community Administrators'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        # Configure Business Processes
        self.check_and_enable_slack_setting(
            setting_name="PRM for Slack Business Processes Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Configure Business Processes') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Configure Business Processes'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Configure Business Processes'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

    def enable_sales_cloud_for_slack(self):
        """Enables settings on the Sales Cloud for Slack setup page"""
        self.shared.go_to_setup_admin_page("SlackSetupForSales/home")
        self.builtin.log_to_console("\nLoaded Sales Cloud for Slack Setup Page...")
        self.shared.wait_on_element(
            "a.slds-tabs_default__link[data-tab-value='Getting Started']"
        )

        # Check Review Documentation Box
        self.check_and_enable_slack_setting(
            setting_name="Review Documentation and Resources Checkbox",
            completed_selector="div.setupcontent >> h2:has-text('Review Documentation and Resources') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources')) >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources')) >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Prepare for Sales Channels'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            # Check Settings for Sales Channels
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Sales Channel']"
            )
            sleep(1)

            # Check Review Documentation Box
            self.check_and_enable_slack_setting(
                setting_name="Documentation Checkbox",
                completed_selector="div.setupcontent >> h2:has-text('Review Documentation and Resources'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'):visible)  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Who Creates Sales Channels
            if (
                self.browser.get_element_count(
                    "div.setupcontent >> button:has-text('Manage Who Creates Sales Channels'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
                )
                == 0
            ):
                self.browser.click(
                    ":nth-match(label.slds-radio__label:has-text('Users with Read Only access to a record'), 1)"
                )
                self.check_and_enable_slack_setting(
                    setting_name="Manage Who Creates Sales Channels Confirmation",
                    completed_selector="div.setupcontent >> button:has-text('Manage Who Creates Sales Channels'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                    state_check_selector="div.setupcontent >> section:has(button:has-text('Manage Who Creates Sales Channels'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                    enable_selectors=[
                        "div.setupcontent >> section.slds-accordion__section:has(button:has-text('Manage Who Creates Sales Channels'):visible) >> div.step-container-summary >> label.slds-checkbox-button"
                    ],
                )

            # Page Layouts
            self.check_and_enable_slack_setting(
                setting_name="Add the Sales Channel Related List to Page Layouts Confirmation",
                completed_selector="div.setupcontent >> button:has-text('Add the Sales Channel Related List to Page Layouts'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Add the Sales Channel Related List to Page Layouts'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Add the Sales Channel Related List to Page Layouts'):visible)  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Channel Action Button
            self.check_and_enable_slack_setting(
                setting_name="Add the Link a Channel Action Button Confirmation",
                completed_selector="div.setupcontent >> button:has-text('Add the Link a Channel Action Button'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Add the Link a Channel Action Button'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Add the Link a Channel Action Button'):visible)  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Go Back
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Getting Started']"
            )
            sleep(1)

            # Check Review Documentation Box
            self.check_and_enable_slack_setting(
                setting_name="Prepare for Sales Channels Confirmation Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Prepare for Sales Channels'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Prepare for Sales Channels'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Prepare for Sales Channels'):visible)  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        # Notifications
        if (
            self.browser.get_element_count(
                "div.setupcontent >> button:has-text('Activate Automated Notifications') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Automated Notifications']"
            )

            # Check Review Documentation Box
            self.check_and_enable_slack_setting(
                setting_name="Documentation Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Review Documentation and Resources'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Review Documentation and Resources'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Review Documentation and Resources'):visible)  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Activation Notifications
            self.check_and_enable_slack_setting(
                setting_name="Clone and Activate Notifications for Sales Channels Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Clone and Activate Notifications for Sales Channels') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Clone and Activate Notifications for Sales Channels'))  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Clone and Activate Notifications for Sales Channels'))  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Activation Notifications
            self.check_and_enable_slack_setting(
                setting_name="Clone and Activate Reminder Notifications for Opportunity Owners Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Clone and Activate Reminder Notifications for Opportunity Owners') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Clone and Activate Reminder Notifications for Opportunity Owners'))  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Clone and Activate Reminder Notifications for Opportunity Owners'))  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Go Back
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Getting Started']"
            )
            sleep(1)

            # Check Notifications Confirmation
            self.check_and_enable_slack_setting(
                setting_name="Activate Automated Notifications Confirmation Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Activate Automated Notifications') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Activate Automated Notifications'))  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Activate Automated Notifications'))  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        # Feeds
        if (
            self.browser.get_element_count(
                "div.setupcontent >> button:has-text('Set Up Feed Channels') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Feed Channels']"
            )

            # Check Review Documentation Box
            self.check_and_enable_slack_setting(
                setting_name="Documentation Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Review Documentation and Resources'):visible >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Review Documentation and Resources'):visible)  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Review Documentation and Resources'):visible)  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Activate the Deals Won Channel
            if (
                self.browser.get_element_count(
                    "div.setupcontent >> button:has-text('Activate the Deals Won Channel') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
                )
                == 0
            ):
                # self.browser.click(
                #     "div.setupcontent >> section:has(button:has-text('Activate the Deals Won Channel')) >> button:has-text('Go to Setup Wizard')"
                # )
                # sleep(1)
                # self.shared.wait_and_click(
                #     "div.navigation-bar__right-align >> button:has-text('Next')"
                # )

                self.check_and_enable_slack_setting(
                    setting_name="Activate the Deals Won Channel Checkbox",
                    completed_selector="div.setupcontent >> button:has-text('Activate the Deals Won Channel') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                    state_check_selector="div.setupcontent >> section:has(button:has-text('Activate the Deals Won Channel'))  >> :nth-match(input[type='checkbox'], 1)",
                    enable_selectors=[
                        "div.setupcontent >> section:has(button:has-text('Activate the Deals Won Channel'))  >> :nth-match(label.slds-checkbox-button, 1)"
                    ],
                )

            # Activate the Deals to Watch Channel
            self.check_and_enable_slack_setting(
                setting_name="Activate the Deals to Watch Channel",
                completed_selector="div.setupcontent >> button:has-text('Activate the Deals to Watch Channel') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Activate the Deals to Watch Channel'))  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Activate the Deals to Watch Channel'))  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

            # Go Back
            self.browser.click(
                "a.slds-tabs_default__link[data-tab-value='Getting Started']"
            )
            sleep(1)

            # Check Set Up Feed Channels Confirmation
            self.check_and_enable_slack_setting(
                setting_name="Set Up Feed Channels Confirmation Checkbox",
                completed_selector="div.setupcontent >> button:has-text('Set Up Feed Channels') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Set Up Feed Channels'))  >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Set Up Feed Channels'))  >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

    def check_and_enable_slack_setting(
        self,
        setting_name,
        completed_selector,
        state_check_selector,
        enable_selectors,
        check_state="checked",
    ):
        """Checks and Enables a Slack Apps Setting"""

        self.builtin.log_to_console(f"\nChecking {setting_name} is enabled...")
        if self.browser.get_element_count(completed_selector) == 1:
            self.builtin.log_to_console("\n -> Already Confirmed as Enabled")
            return
        if check_state not in self.browser.get_element_states(state_check_selector):
            for selector in enable_selectors:
                self.browser.click(selector)
            self.builtin.log_to_console("\n -> Enabled!")
        else:
            self.builtin.log_to_console("\n -> Already Enabled!")

    def enable_slack_apps(self):
        """Enables all settings for Slack Apps"""
        # Load Setup Page
        self.go_to_slack_apps_setup()
        self.builtin.log_to_console("\nLoaded Setup Page")

        # Check Review Documentation Box
        self.check_and_enable_slack_setting(
            setting_name="Documentation Checkbox",
            completed_selector="div.setupcontent >> h2:has-text('Review Documentation and Resources') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'))  >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Review Documentation and Resources'))  >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        # Agree To Terms
        self.check_and_enable_slack_setting(
            setting_name="Terms and Conditions Toggle",
            completed_selector="div.setupcontent >> h2:has-text('Agree to Terms and Conditions') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(button:has-text('Agree to Terms and Conditions'))  >> span.slds-checkbox_on",
            check_state="visible",
            enable_selectors=[
                "div.setupcontent >> section:has(button:has-text('Agree to Terms and Conditions'))  >> span.slds-checkbox_faux"
            ],
        )

        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Enable Slack Apps') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            # Enable Sales Cloud for Slack
            self.check_and_enable_slack_setting(
                setting_name="Sales Cloud for Slack App",
                completed_selector="div.setupcontent >> h2:has-text('Enable Slack Apps') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Enable Slack Apps')) >> div.slds-media:has-text('Sales Cloud for Slack') >> span.slds-checkbox_on",
                check_state="visible",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Enable Slack Apps')) >> div.slds-media:has-text('Sales Cloud for Slack') >> span.slds-checkbox_faux"
                ],
            )

            # Enable Service Cloud for Slack
            self.builtin.log_to_console(
                "\nEnabling Service Cloud for Slack App and Case Swarming..."
            )
            self.service.enable_case_swarming()
            self.go_to_slack_apps_setup()

            # Enable CRM Analytics for Slack
            self.builtin.log_to_console("\nEnabling CRM Analytics Slack App...")
            self.shared.go_to_setup_admin_page("SlackAnalyticsApp/home")
            if "checked" not in self.browser.get_element_states(
                "input[value='AnalyticsSlackAppPref']"
            ):
                self.browser.click("label[for='AnalyticsSlackAppPref']")
                sleep(1)
            self.go_to_slack_apps_setup()

            # Enable Partner Relationship Management for Slack
            self.check_and_enable_slack_setting(
                setting_name="Partner Relationship Management for Slack App",
                completed_selector="div.setupcontent >> h2:has-text('Enable Slack Apps') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(button:has-text('Enable Slack Apps')) >> div.slds-media:has-text('Partner Relationship Management for Slack') >> span.slds-checkbox_on",
                check_state="visible",
                enable_selectors=[
                    "div.setupcontent >> section:has(button:has-text('Enable Slack Apps')) >> div.slds-media:has-text('Partner Relationship Management for Slack') >> span.slds-checkbox_faux"
                ],
            )

            # Slack Apps Setup Complete
            self.check_and_enable_slack_setting(
                setting_name="Slack Apps Section Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Enable Slack Apps') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Enable Slack Apps'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Enable Slack Apps'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Assign Slack App and User Permissions') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            self.builtin.log_to_console(
                "\nAssigning Permission Sets to current user..."
            )

            # Sales Cloud for Slack
            self.shared.assign_permission_set(
                "Sales Cloud for Slack", "SlackSalesCloud"
            )

            # Service Cloud for Slack
            self.shared.assign_permission_set("Service User", "ServiceUserPsl")
            self.shared.assign_permission_set("Slack Service User", "SlackServiceUser")

            # CRM for Analytics
            self.shared.assign_permission_set(
                "CRM Analytics Plus User", "EinsteinAnalyticsPlusUser"
            )

            # Partner Relationship Management
            self.shared.assign_permission_set(
                "Partner Account Manager", "PRMForSlackPartnerManagerPermSet"
            )

            # Slack Permissions Setup Complete
            self.check_and_enable_slack_setting(
                setting_name="Assign Slack App and User Permissions Section Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Assign Slack App and User Permissions') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Assign Slack App and User Permissions'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Assign Slack App and User Permissions'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Verify Data Sharing Options') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            # Check PRM Setup
            self.enable_prm_for_slack()
            self.go_to_slack_apps_setup()

            # Slack Sharing Setup Complete
            self.check_and_enable_slack_setting(
                setting_name="Sharing Section Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Verify Data Sharing Options') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Verify Data Sharing Options'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Verify Data Sharing Options'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        # Slack Apps Setup Complete
        self.check_and_enable_slack_setting(
            setting_name="Install Slack Apps Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Install Slack Apps') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Install Slack Apps'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Install Slack Apps'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

        # Complete Apps Setup
        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Complete Slack Apps Setup') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            # Check Sales Cloud for Slack Setup
            self.enable_sales_cloud_for_slack()
            self.go_to_slack_apps_setup()

            # Slack Apps Setup Complete
            self.check_and_enable_slack_setting(
                setting_name="Sharing Section Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Complete Slack Apps Setup') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Complete Slack Apps Setup'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Complete Slack Apps Setup'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )

        # Slack Apps Setup Complete
        self.check_and_enable_slack_setting(
            setting_name="Control Field-Level Access in Slack Confirmation",
            completed_selector="div.setupcontent >> h2:has-text('Control Field-Level Access in Slack') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
            state_check_selector="div.setupcontent >> section:has(h2:has-text('Control Field-Level Access in Slack'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
            enable_selectors=[
                "div.setupcontent >> section:has(h2:has-text('Control Field-Level Access in Slack'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
            ],
        )

    def assign_default_slack_layout(
        self,
        object_name: str,
        layout_name: str = "",
        field_list: str = "",
        layout_type: str = "CRUD",
    ):
        """Assigns a Slack Record Layout to a defined object"""

        if not layout_name:
            layout_name = "Slack Default"

        self.builtin.log_to_console(f"\nCreating new Slack Layout called {layout_name}")

        # Load Slack record Page
        self.shared.go_to_setup_admin_page(
            setup_page_url=f"ObjectManager/{object_name}/SlackRecordLayouts/view"
        )
        self.builtin.log_to_console(f"\n -> Loaded Object page for {object_name}")

        # Check if already created
        if self.shared.wait_on_element(
            f"th[data-label='Layout Name']:has-text('{layout_name}')", 3
        ):
            self.builtin.log_to_console("\n -> Layout already assigned to object")
            return

        # Create New Layout
        self.builtin.log_to_console("\n -> Layout not found. Creating...")
        self.browser.click("button.slds-button:has-text('New')")
        sleep(1)

        # Set Layout Type
        if "CRUD" not in layout_type.upper():
            self.builtin.log_to_console("\n -> Setting to URL Unfurling Layout")
            self.browser.click(
                "span.slds-text-title_bold:has-text('URL Unfurling Layout')"
            )
        else:
            self.builtin.log_to_console("\n -> Leaving as default type CRUD Layout")

        self.browser.click("button.next-button")

        # Set Layout Name
        self.shared.wait_and_fill_text(
            "lightning-primitive-input-simple:has-text('Layout Name') >> input.slds-input",
            layout_name,
        )
        self.browser.click("lightning-primitive-input-simple:has-text('API Name')")
        self.builtin.log_to_console("\n -> Added Layout Name")

        # Set Fields
        if len(field_list) > 0:
            self.builtin.log_to_console("\n -> Adding Fields")
            for field in field_list.split(","):
                field_in_list = f":nth-match(div.slds-dueling-list__options, 1) >> :nth-match(li.slds-listbox__item:has-text('{field}'), 1)"
                if self.browser.get_element_count(field_in_list) == 1:
                    self.browser.click(field_in_list)
                    self.browser.click(
                        "button.slds-button_icon-container[title='Move selection to Selected*']"
                    )
                    self.builtin.log_to_console(f"\n -> Added Field {field}")
                    sleep(0.5)

        self.browser.click("button.next-button")

        # Set Addditonal Settings
        self.builtin.log_to_console("\n -> Skipping Additional Object Settings")
        self.browser.click("button.next-button")

        # Assign Actions
        self.builtin.log_to_console("\n -> Skipping Action Assignments")
        self.browser.click("button.next-button")

        # Assign Layout to Profiles
        self.builtin.log_to_console("\n -> Assigning to all Profiles")
        for rt in ["Slack Record Layout","Simple Opportunity","Channel (Partner)"]:
            if self.browser.get_element_count(f"th.assignment-header:has-text('{rt}')"):
                self.browser.click(f"th.assignment-header:has-text('{rt}') >> span.slds-checkbox_faux")
                sleep(0.5)
        sleep(0.5)

        # Finish
        self.builtin.log_to_console("\n -> Completing Setup")
        self.browser.click("button.slds-button:has-text('Done')")

        # Wait for Table to Appear
        self.shared.wait_on_element(
            f"th[data-label='Layout Name']:has-text('{layout_name}')"
        )
        self.builtin.log_to_console("\n -> Layout Created!")

    def update_data_sharing_for_slack_apps(self, record_security="", link_unfurling=""):
        """Sets or Updates the Data Sharing Settings for Slack Apps"""
        self.go_to_slack_apps_setup()
        self.builtin.log_to_console("\nLoaded Setup Page")

        # If Already Set, Expand Options
        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Verify Data Sharing Options') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 1
        ):
            self.browser.click(
                "button.stage-label:has-text('Verify Data Sharing Options')"
            )
            sleep(1)

        # Set Options
        if record_security:
            record_security = record_security.replace("'", "\\'")
            self.browser.click(
                "lightning-combobox:has-text('Set Record Detail Security for Your Salesforce Apps') >> lightning-base-combobox.slds-combobox_container"
            )
            record_security_selector = f"lightning-base-combobox-item >> span.slds-truncate:has-text('{record_security}')"
            if self.shared.wait_on_element(record_security_selector, 2):
                self.browser.click(record_security_selector)

        if link_unfurling:
            link_unfurling = link_unfurling.replace("'", "\\'")
            self.browser.click(
                "lightning-combobox:has-text('Link Unfurling') >> lightning-base-combobox.slds-combobox_container"
            )
            unfurling_selector = f"lightning-base-combobox-item >> span.slds-truncate:has-text('{link_unfurling}')"
            if self.shared.wait_on_element(unfurling_selector, 2):
                self.browser.click(unfurling_selector)

        # If not already updated, confirm the section has been updated
        if (
            self.browser.get_element_count(
                "div.setupcontent >> h2:has-text('Verify Data Sharing Options') >> div.slds-progress-ring_complete[aria-valuetext='Complete']"
            )
            == 0
        ):
            # Slack Sharing Setup Complete
            self.check_and_enable_slack_setting(
                setting_name="Sharing Section Confirmation",
                completed_selector="div.setupcontent >> h2:has-text('Verify Data Sharing Options') >> div.slds-progress-ring_complete[aria-valuetext='Complete']",
                state_check_selector="div.setupcontent >> section:has(h2:has-text('Verify Data Sharing Options'))  >> div.step-container-summary >> :nth-match(input[type='checkbox'], 1)",
                enable_selectors=[
                    "div.setupcontent >> section:has(h2:has-text('Verify Data Sharing Options'))  >> div.step-container-summary >> :nth-match(label.slds-checkbox-button, 1)"
                ],
            )
