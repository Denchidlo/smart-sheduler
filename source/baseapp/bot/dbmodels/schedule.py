from .group import StudentGroup
from .employee import Employee
from django.db import models
from enum import Enum

class WeekDay(Enum):
    NULL_DAY = (0, "NULL_DAY")
    MONDAY = (1, "Понедельник")
    TUESDAY = (2, "Вторник")
    WEDNESDAY = (3, "Среда")
    THURSDAY = (4, "Вторник")
    FRIDAY = (5, "Вторник")
    SATURDAY = (6, "Вторник")
    SUNSDAY = (7, "Вторник")

def weekday_to_int(day_str: str) -> int:
    for day in WeekDay:
        if day_str == day.value[1]:
            return day.value[0]
    return 0

def int_to_weekday(day_int: int) -> WeekDay:
    for day in WeekDay:
        if day_int == day.value[0]:
            return day
    return 0

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
    weeks = models.IntegerField()
    subgroup = models.SmallIntegerField(default=0)
    auditory = models.CharField(max_length=12, null=True, blank=True, default="unknown")
    lesson_time = models.CharField(max_length=11)
    lesson_start = models.TimeField()
    lesson_end = models.TimeField()
    lesson_type = models.CharField(max_length=6)
    subject = models.CharField(max_length=20)
    groups = models.ManyToManyField(StudentGroup)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default=None, null=True, blank=True)
    zaoch = models.BooleanField(default=False)
