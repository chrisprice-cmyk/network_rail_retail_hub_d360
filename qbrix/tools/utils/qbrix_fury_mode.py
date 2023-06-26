import multiprocessing
from abc import ABC

from cumulusci.core.tasks import BaseTask

from tools.shared.qbrix_cci_tasks import run_cci_flow, run_cci_task


class RunFuryMode(BaseTask, ABC):
    task_docs = """
    Parallel Task, Flow and Script Runner for Q Brix. Use with caution.
    """

    task_options = {
        "org": {
            "description": "Org Alias for the target org",
            "required": False
        },
        "flows": {
            "description": "List of flows to execute. These must already be defined in the flows area.",
            "required": False
        },
        "tasks": {
            "description": "List of Tasks to execute. These must already be defined with options in the tasks area.",
            "required": False
        },
        "apex_scripts": {
            "description": "List of Apex Scripts to run",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(RunFuryMode, self)._init_options(kwargs)
        self.flows = self.options["flows"] if "flows" in self.options else None
        self.tasks = self.options["tasks"] if "tasks" in self.options else None
        self.apex_scripts = self.options["apex_scripts"] if "apex_scripts" in self.options else None

    def _run_task(self, processes=None):

        for flow in self.flows:
            flow_parameters = ["flow_name", flow, "org_name", self.org_config.name]
            process = multiprocessing.Process(target=run_cci_flow, args=(flow_parameters,))
            processes.append(process)
            process.start()

        for task in self.tasks:
            task_parameters = ["task_name", task, "org_name", self.org_config.name]
            process = multiprocessing.Process(target=run_cci_task, args=(task_parameters,))
            processes.append(process)
            process.start()

        for script in self.apex_scripts:
            print("Apex Scripts not yet supported.")

        # Wait for all processes to finish
        for process in processes:
            process.join()
