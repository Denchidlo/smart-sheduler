import logging
from typing import Iterable
from requests.models import HTTPError
from ..dbmodels.employee import Employee
from ..dbmodels.group import StudentGroup
from ..dbmodels.schedule import Lesson, weekday_to_int, weeks_to_int
from ..dbmodels.auth import GroupLead
from django.conf import settings
from enum import Enum
import time as t
from datetime import time
import requests as req
import asyncio
from asgiref.sync import sync_to_async

class RequestStrings(Enum):
    GET_GROUP_SCHEDULE = (
        "https://journal.bsuir.by/api/v1/studentGroup/schedule?studentGroup="
    )
    GET_EMPLOYEE_SCHEDULE = (
        "https://journal.bsuir.by/api/v1/portal/employeeSchedule?employeeId="
    )
    GET_ALL_GROUPS = "https://journal.bsuir.by/api/v1/groups"
    GET_ALL_EMPLOYEES = "https://journal.bsuir.by/api/v1/employees"
    GET_CURRENT_WEEK = "http://journal.bsuir.by/api/v1/week"


class ScheduleProvider:
    def load(self) -> None:
        # print(RequestStrings.GET_ALL_GROUPS.value)
        grop_list = self.make_request(RequestStrings.GET_ALL_GROUPS.value)
        for group in grop_list:
            StudentGroup.objects.get_or_create(
                name=group["name"], course=group["course"]
            )
        employee_list = self.make_request(
            RequestStrings.GET_ALL_EMPLOYEES.value)
        self.idx = 0
        start = t.time()
        self.leng = len(employee_list)
        asyncio.set_event_loop(asyncio.new_event_loop())
        emp_loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self._proceed_employee(employee)) for employee in employee_list]
        emp_loop.run_until_complete(asyncio.wait(tasks))  
        logging.info("all tasks were loaded")
        emp_loop.close()

        for el in StudentGroup.objects.all():
            GroupLead.objects.get_or_create(group=el, defaults={"user": None})

        end = t.time()
        logging.info(f"Successful upload!\nTime consumed: {end - start} seconds")
            


    def make_request(self, request_string: str) -> Iterable:
        bsuir_api_responce = req.get(request_string)
        if bsuir_api_responce.status_code == 200:
            return bsuir_api_responce.json()
        else:
            logging.exception("GET request failed with status code {code}\nRequest:{req_str}".format(
                code=bsuir_api_responce.status_code, req_str=request_string))
            raise HTTPError("")

    async def _proceed_employee(self, employee):
        
        self.idx += 1
        logging.debug(f"Proceeded {self.idx}/{self.leng}")
        db_employee, _ = await sync_to_async(Employee.objects.get_or_create)(
            first_name=employee["firstName"],
            last_name=employee["lastName"],
            middle_name=employee["middleName"],
            bsuir_id=employee["id"],
            fio=employee["fio"],
        )
        employee_schedule = await sync_to_async(self.make_request)(
            RequestStrings.GET_EMPLOYEE_SCHEDULE.value +
            str(employee["id"])
        )
        for schedule in employee_schedule["schedules"]:
            weekday = weekday_to_int(schedule["weekDay"])
            lessons = schedule["schedule"]
            for lesson in lessons:
                group_list = lesson["studentGroup"]
                group_list = await sync_to_async(StudentGroup.objects.filter)(
                    name__in=group_list)
                db_lesson, _ = await sync_to_async(Lesson.objects.get_or_create)(
                    weekday=weekday,
                    weeks=weeks_to_int(lesson["weekNumber"]),
                    subgroup=lesson["numSubgroup"],
                    auditory=lesson["auditory"],
                    lesson_time=lesson["lessonTime"],
                    lesson_start=time.fromisoformat(
                        lesson["startLessonTime"]),
                    lesson_end=time.fromisoformat(lesson["endLessonTime"]),
                    lesson_type=lesson["lessonType"],
                    subject=lesson["subject"],
                    employee=db_employee,
                    zaoch=lesson["zaoch"],
                )
                db_lesson.groups.add(*group_list)


settings.CURRENT_WEEK = ScheduleProvider().make_request(
    RequestStrings.GET_CURRENT_WEEK.value
)
