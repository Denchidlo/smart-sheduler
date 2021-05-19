from typing import Iterable
from requests.models import HTTPError
from ..dbmodels.employee import Employee
from ..dbmodels.group import StudentGroup
from ..dbmodels.schedule import Lesson, weekday_to_int, weeks_to_int
from django.conf import settings
from enum import Enum
from datetime import time
import requests as req


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
        employee_list = self.make_request(RequestStrings.GET_ALL_EMPLOYEES.value)
        idx = 0
        leng = len(employee_list)
        for employee in employee_list:
            idx += 1
            print(f"Proceeded {idx}/{leng}")
            db_employee, _ = Employee.objects.get_or_create(
                first_name=employee["firstName"],
                last_name=employee["lastName"],
                middle_name=employee["middleName"],
                bsuir_id=employee["id"],
                fio=employee["fio"],
            )
            employee_schedule = self.make_request(
                RequestStrings.GET_EMPLOYEE_SCHEDULE.value + str(employee["id"])
            )
            for schedule in employee_schedule["schedules"]:
                weekday = weekday_to_int(schedule["weekDay"])
                lessons = schedule["schedule"]
                for lesson in lessons:
                    group_list = lesson["studentGroup"]
                    group_list = StudentGroup.objects.filter(name__in=group_list)
                    db_lesson, _ = Lesson.objects.get_or_create(
                        weekday=weekday,
                        weeks=weeks_to_int(lesson["weekNumber"]),
                        subgroup=lesson["numSubgroup"],
                        auditory=lesson["auditory"],
                        lesson_time=lesson["lessonTime"],
                        lesson_start=time.fromisoformat(lesson["startLessonTime"]),
                        lesson_end=time.fromisoformat(lesson["endLessonTime"]),
                        lesson_type=lesson["lessonType"],
                        subject=lesson["subject"],
                        employee=db_employee,
                        zaoch=lesson["zaoch"],
                    )
                    db_lesson.groups.add(*group_list)

    def make_request(self, request_string: str) -> Iterable:
        bsuir_api_responce = req.get(request_string)
        if bsuir_api_responce.status_code == 200:
            return bsuir_api_responce.json()
        else:
            raise HTTPError(
                "GET request failed with status code {code}\nRequest:{req_str}".format(
                    code=bsuir_api_responce.status_code, req_str=request_string
                )
            )


settings.CURRENT_WEEK = ScheduleProvider().make_request(
    RequestStrings.GET_CURRENT_WEEK.value
)
