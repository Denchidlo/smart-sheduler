from .auth import ScheduleUser
from .schedule import Lesson, int_to_weeks
from django.db import models

class StudentGroup(models.Model):
    name = models.CharField(max_length=7, unique=True)
    head = models.ForeignKey(ScheduleUser, on_delete=models.SET_NULL, null=True, blank=True)
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

    def get_schedule(self, day, week: int) -> list:
        lessons = Lesson.objects.lesson_set.filter(weekday=day)
        schedule = []
        for lesson in lessons:
            week_list = int_to_weeks(lesson.weeks)
            if week in week_list:
                schedule.append(lesson)
        return schedule