import subprocess

from qbrix.tools.shared.qbrix_console_utils import init_logger

log = init_logger()


def rebuild_cci_cache():
    
    """" 
    Rebuilds the CCI projects Cache folder using the dev_org flow from CCI 
    """

    log.info("Rebuilding CumulusCI Project Cache")

    try:
        subprocess.run(["cci", "flow", "info", "dev_org"])
    except Exception as e:
        log.error(f"Failed to rebuild CCI cache. Error Message: {e}")

    log.info("CumulusCI Project Cache Rebuild Complete!")
