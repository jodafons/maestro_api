
__all__ = []

from typing import Dict, Any, List
from pydantic import BaseModel


class Request(BaseModel):
  token       : str = ""


class Job(Request):  
  id          : int = -1
  image       : str = ""
  command     : str = ""
  envs        : str = "{}"
  binds       : str = "{}"
  workarea    : str = ""
  inputfile   : str = ""
  partition   : str = ""
  status      : str = "Unknown"

class Task(Request):
  id          : int = -1
  name        : str = ""
  volume      : str = ""
  jobs        : List[Job] = []
  partition   : str = ""
  status      : str = "Unknown"




