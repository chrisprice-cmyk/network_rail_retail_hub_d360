import subprocess

from qbrix.tools.shared.qbrix_console_utils import init_logger
from cumulusci.core.utils import import_global
from cumulusci.core.exceptions import TaskOptionsError
from cumulusci.core.config import ScratchOrgConfig, TaskConfig, FlowConfig
from cumulusci.core.tasks import CURRENT_TASK, BaseTask
from cumulusci.cli.runtime import CliRuntime
from cumulusci.core.config.org_config import OrgConfig
from cumulusci.core.config.project_config import BaseProjectConfig
from cumulusci.core.flowrunner import FlowCoordinator

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


def _parse_task_options(options, task_class, task_config):
    if "options" not in task_config.config:
        task_config.config["options"] = {}
    # Parse options and add to task config
    if options:
        for name, value in options.items():
            # Validate the option
            if name not in task_class.task_options:
                raise TaskOptionsError(
                    'Option "{}" is not available for task {}'.format(
                        name, task_class
                    )
                )

            # Override the option in the task config
            task_config.config["options"][name] = value

    return task_config


def _run_task(task):
    task()
    return task.return_values


def run_cci_task(class_path, org_name="dev", **options):

    """
    Runs a given task using the given class_path and optional org name along with optional options.

    Example Usage:

    run_cci_task('cumulusci.tasks.salesforce.Deploy', 'dev', path='force-app')
    """

    if getattr(CURRENT_TASK, "stack", None) and CURRENT_TASK.stack[0].project_config:
        _project_config = CURRENT_TASK.stack[0].project_config
    else:
        _project_config = CliRuntime().project_config

    if getattr(CURRENT_TASK, "stack", None) and CURRENT_TASK.stack[0].org_config:
        _org = CURRENT_TASK.stack[0].org_config
    else:
        _org = CliRuntime().project_config.keychain.get_org(org_name)

    task_class = import_global(class_path)
    task_config = _parse_task_options(options, task_class, TaskConfig())
    task = task_class(
        task_config.project_config or _project_config,
        task_config,
        org_config=_org,
        logger=log,
    )
    return _run_task(task)


def run_cci_flow(flow_name, org_name="dev", **options):

    """
    Runs a given flow using the flow name and optional org name along with optional options.

    Example Usage:

    run_cci_flow('deploy_qbrix', 'dev')
    """

    org_config = CliRuntime().project_config.keychain.get_org(org_name)
    flow_coordinator = CliRuntime().get_flow(flow_name, options=options)
    flow_coordinator.run(org_config)

# This has been added and left as a general test runner for testing only
class testRun(BaseTask):
    task_options = {
        "org": {
            "description": "Org alias",
            "required": False
        },
    }

    def _run_task(self):
        run_cci_flow("base:deploy_qbrix", "mfgido")
