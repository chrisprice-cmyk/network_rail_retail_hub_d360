from pickle import FALSE
import subprocess
import textwrap
from cumulusci.tasks.command import Command

class CreateBanner(Command):

  task_options={
        "text": {
            "description": "Text you want to show as a banner",
            "required": FALSE
        }
    }

  def _init_options(self, kwargs):
        super(CreateBanner, self)._init_options(kwargs)
        self.text = ""
        if "text" in self.options:
          self.text = self.options["text"]
        else:
          self.text = f"{self.project_config.project__name} | DEPLOYMENT STARTED\n\nAPI VERSION: {self.project_config.project__package__api_version}\nREPO URL:    {self.project_config.project__git__repo_url}"
        
        self.width = None
        self.text_box = None
        self.max_width = None
        self.border_char = '*'
        self.min_width = None
        self.env = self._get_env()
  
  def _banner_string(self):
        output_string = self.border_char * self.width + "\n"
        for text_line in self.text_box:
            output_string += self.border_char + " " + text_line + " " + self.border_char + "\n"
        output_string += self.border_char * self.width
        return output_string

  def _generate_list(self):
    
        #if we are running in a headless runner- tty will not be there.
        if self.width ==0: return []
        # Split the input text into separate paragraphs before formatting the
        # length.
        box_width = self.width - 4
        paragraph_list = self.text.split("\n")
        text_list = []
        for paragraph in paragraph_list:
            text_list += textwrap.fill(paragraph, box_width, replace_whitespace=False).split("\n")
        text_list = [line.ljust(box_width) for line in text_list]
        return text_list

  def _run_task(self):
    self.width = get_terminal_width()
    self.text_box = self._generate_list()
    print(self._banner_string())

def get_terminal_width():
   #if we are running in a headless runner- tty will not be there.
  try:
    return int(subprocess.check_output(['stty', 'size']).split()[1])
  except Exception as e:
      print(e)
  return 0
  
