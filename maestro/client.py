
__all__ = []

import requests
import json, orjson
from loguru import logger
from typing import Dict, Any, List
from maestro.schemas import Task, Job

class maestro_client:

    def __init__(self, host, service = 'pilot'):
        self.host = host
        self.service = service

    def try_request( self, 
                     endpoint: str,
                     method: str = "get",
                     params: Dict = {},
                     body: str = "",
                     stream: bool = False,
                    ) -> Any:

        function = {
            "get" : requests.get,
            "post": requests.post,
        }[method]
        try:
            #print(f"{self.host}/{self.service}/{endpoint}")
            request = function(f"{self.host}/{self.service}/{endpoint}", params=params, data=body)
        except:
            logger.error("Failed to establish a new connection.")
            return None
        if request.status_code != 200:
            answer = request.json()
            logger.error(f"Request failed. Got {request.status_code} with message: {answer['detail']}")
            return None
        return request.json()


    def ping(self):
        return False if self.try_request('ping', method="get") is None else True


    def create(self, task : Task):
      return self.try_request("create", method='post', body=task.json())


    def delete(self, task_id : int):
      return self.try_request(f"delete/{task_id}", method='post')


    def kill(self, task_id : int):
      return self.try_request(f"kill/{task_id}", method='post')


    def retry(self, task_id : int):
      return self.try_request(f"retry/{task_id}", method='post')
