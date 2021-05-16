from typing import Iterable
from requests.models import HTTPError
from .dbmodels.employee import Employee
from .dbmodels.group import Group
from .dbmodels.schedule import Schedule
from enum import Enum
import requests as req
import json

class RequestStrings(Enum):
    GET_GROUP_SCHEDULE = "https://journal.bsuir.by/api/v1/studentGroup/schedule?studentGroup="
    GET_EMPLOYEE_SCHEDULE = "https://journal.bsuir.by/api/v1/portal/employeeSchedule?employeeId="
    GET_ALL_GROUPS = "https://journal.bsuir.by/api/v1/groups"
    GET_ALL_EMPLOYEES = "https://journal.bsuir.by/api/v1/employees"

class ScheduleProvider:
    def __init__(self) -> None:
        pass

    def load(self) -> None:
        try:
            grop_list = self.make_request(RequestStrings.GET_ALL_GROUPS.value)
            for group in grop_list:
                Group.objects.create(name=group['name'],
                                                    course=group['course'])    
            employee_list = self.make_request(RequestStrings.GET_ALL_EMPLOYEES.value)
            for employee in employee_list:
                db_employee = Employee.objects.create(first_name=employee['first_name'], 
                                                        last_name=employee['last_name'],
                                                        middle_name=employee['middle_name'],
                                                        bsuir_id=employee['id'],
                                                        fio=employee['fio'])
                employee_schedule = self.make_request(RequestStrings.GET_EMPLOYEE_SCHEDULE.value+employee['id'])
                for lesson in employee_schedule['schedules']:
                    lesson['']
        except:
            pass

    def make_request(self, request_string: str) -> Iterable:
        bsuir_api_responce = req.get(request_string) 
        if bsuir_api_responce.status_code == 200:
            return bsuir_api_responce.json()
        else:
            raise HTTPError("GET request failed with status code {code}\nRequest:{req_str}".format(code=bsuir_api_responce.code, req_str=request_string))

if __name__ == "__main__":
    employee_id = ScheduleProvider().make_request(RequestStrings.GET_ALL_EMPLOYEES.value)[3]['id']
    with open("employee_sched.json", "w") as writer:
        json.dump(ScheduleProvider().make_request(RequestStrings.GET_EMPLOYEE_SCHEDULE.value+str(employee_id)), writer)