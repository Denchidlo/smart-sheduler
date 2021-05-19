from source.baseapp.bot.dbmodels.schedule import Lesson
from typing import Iterable
from .auth import ScheduleUser
from django.db import models


def int_to_weeks(hashed_weeks: int) -> list:
    weeks = []
    for i in range(4):
        if (hashed_weeks & 7) != 0:
            weeks.append(hashed_weeks & 7)
            hashed_weeks = hashed_weeks >> 3
    return weeks


class StudentGroup(models.Model):
    name = models.CharField(max_length=7, unique=True)
    head = models.ForeignKey(
        ScheduleUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    course = models.SmallIntegerField(default=None, null=True)

    def add_user(self, user: ScheduleUser):
        if self.head == None:
            self.set_admin(user)
        else:
            user.group = self
            user.save()

    def set_admin(self, user: ScheduleUser):
        user.group = self
        user.save()
        self.head = user
        self.save()

    def get_schedule(self, day, week: int) -> Iterable[Lesson]:
        lessons = self.lesson_set.select_related().filter(weekday=day)
        schedule = []
        for lesson in lessons:
            week_list = int_to_weeks(lesson.weeks)
            if week in week_list:
                schedule.append(lesson)
        return schedule
