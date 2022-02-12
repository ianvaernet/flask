import os
import requests
from datetime import datetime


class SchedulerService:
    """
    Service used to communicate with the Scheduler container API
    """

    __http: requests.Session
    __scheduler_host: str

    def __init__(self) -> None:
        self.__scheduler_host = os.getenv("SCHEDULER_HOST")
        self.__http = requests.Session()
        self.__http.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def add_job(
        self,
        id: str,
        func: str,
        args: list,
        run_date: str or datetime,
        trigger: str = "date",
        replace_existing: bool = True,
    ):
        body = {
            "id": id,
            "func": func,
            "args": args,
            "run_date": run_date if type(run_date) is str else run_date.isoformat(),
            "trigger": trigger,
            "replace_existing": replace_existing,
        }
        self.__http.post(
            f"{self.__scheduler_host}/scheduler/jobs",
            json=body,
            allow_redirects=False,
        )

    def get_job(self, id: str):
        response = self.__http.get(f"{self.__scheduler_host}/scheduler/jobs/{id}")
        return response.json()

    def remove_job(self, id: str):
        self.__http.delete(f"{self.__scheduler_host}/scheduler/jobs/{id}")
