import multiprocessing
from abc import ABC

from cumulusci.core.tasks import BaseTask

from qbrix.tools.shared.qbrix_cci_tasks import run_cci_flow, run_cci_task

def run_multiple_flows(flow_names, org_name, **options):
        pool = multiprocessing.Pool()
        pool.starmap(run_cci_flow_wrapper, [(flow_name, org_name, options) for flow_name in flow_names])
        pool.close()
        pool.join()

def run_cci_flow_wrapper(flow_name, org_name, options):
    try:
        print(f"Starting Flow: {flow_name}.")
        run_cci_flow(flow_name, org_name, **options)
    except Exception as e:
        print(f"Error running flow: {flow_name} - {str(e)}")
    else:
        print(f"Flow: {flow_name} completed.")

def run_multiple_tasks(task_names, org_name):
        pool = multiprocessing.Pool()
        pool.starmap(run_cci_task_wrapper, [(task_name, org_name) for task_name in task_names])
        pool.close()
        pool.join()

def run_cci_task_wrapper(task_name, org_name):
    try:
        print(f"Starting Task: {task_name}.")
        run_cci_task(task_name, org_name)
    except Exception as e:
        print(f"Error running task: {task_name} - {str(e)}")
    else:
        print(f"Task: {task_name} completed.")



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
            "description": "List of Apex Scripts to run (COMING SOON)",
            "required": False
        }
    }

    def _init_options(self, kwargs):
        super(RunFuryMode, self)._init_options(kwargs)
        self.flows = self.options["flows"] if "flows" in self.options else None
        self.tasks = self.options["tasks"] if "tasks" in self.options else None
        self.apex_scripts = self.options["apex_scripts"] if "apex_scripts" in self.options else None

    def _run_task(self):

        self.logger.info("""
         _____ ______ ______  _____ __   __                          
        |  _  || ___ \| ___ \|_   _|\ \ / /                          
        | | | || |_/ /| |_/ /  | |   \ V /                           
        | | | || ___ \|    /   | |   /   \                           
        \ \/' /| |_/ /| |\ \  _| |_ / /^\ \                          
         \_/\_\\____/ \_| \_| \___/ \/   \/                          
                                                                    
                                                                    
        ______  _   _ ______ __   __    ___  ___ _____ ______  _____ 
        |  ___|| | | || ___ \\ \ / /    |  \/  ||  _  ||  _  \|  ___|
        | |_   | | | || |_/ / \ V /     | .  . || | | || | | || |__  
        |  _|  | | | ||    /   \ /      | |\/| || | | || | | ||  __| 
        | |    | |_| || |\ \   | |      | |  | |\ \_/ /| |/ / | |___ 
        \_|     \___/ \_| \_|  \_/      \_|  |_/ \___/ |___/  \____/
        
        """)
        
        if self.flows:
            run_multiple_flows(flow_names=self.flows, org_name=self.org_config.name, options=self.options)

        if self.tasks:
            run_multiple_tasks(task_names=self.tasks, org_name=self.org_config.name)
