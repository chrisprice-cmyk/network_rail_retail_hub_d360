from time import sleep

from Browser import ElementState, SelectAttribute
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask
from qbrix.robot.QbrixFieldServiceKeywords import QbrixFieldServiceKeywords


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixPatchAutomation(QbrixRobotTask):

    def __init__(self):
        super().__init__()
        self._field_service_keywords = None
    
    @property
    def field_service_keywords(self):

        """Loads Q Robot Field Service Keywords and Methods"""

        if self._field_service_keywords is None:
            self._field_service_keywords = QbrixFieldServiceKeywords()
        return self._field_service_keywords

    def disable_field_service(self):
        self.field_service_keywords.enable_field_service(turn_off=True)  

    def enable_messaging_channels(self):
        pass

    def update_sdo_service_omniflow(self):
        pass 