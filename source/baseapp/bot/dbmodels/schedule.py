from typing import Iterable
from .group import Group
from .employee import Employee
from django.db import models
from enum import Enum

class WeekDay(Enum):
    MONDAY = (1, "Понедельник")
    TUESDAY = (2, "Вторник")
    WEDNESDAY = (3, "Среда")
    THURSDAY = (4, "Вторник")
    FRIDAY = (5, "Вторник")
    SATURDAY = (6, "Вторник")
    SUNSDAY = (7, "Вторник")

def convert_to_weekday(day_str: str):
    for day in WeekDay:
        if day_str == day.value[1]:
            return day.value[0]
    raise ValueError("Unknown day")

def weeks_to_int(weeks_list: list) -> int:
    result = 0
    for week in weeks_list:
        result = (result << 3) | week
    return result

def int_to_weeks(hashed_weeks: int) -> list:
    weeks = []
    for i in range(4):
        if (hashed_weeks & 7) != 0:
            weeks.append(hashed_weeks & 7)
            hashed_weeks = hashed_weeks >> 3
    return weeks  

class Week(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 4
    FOURTH = 8

class Lesson(models.Model):
    weekday = models.SmallIntegerField()
    weeks = models.SmallIntegerField()
    subgroup = models.SmallIntegerField(default=0)
    auditory = models.CharField(max_length=12, null=True, blank=True, default="unknown")
    lesson_time = models.CharField(max_length=11)
    lesson_start = models.TimeField()
    lesson_end = models.TimeField()
    subject = models.CharField(max_length=20)
    groups = models.ManyToManyField(Group)
    employee = models.ForeignKey(Employee)
    zaoch = models.BooleanField(default=False)
