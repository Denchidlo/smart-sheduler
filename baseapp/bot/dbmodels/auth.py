from .group import StudentGroup
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class ScheduleUserManager(BaseUserManager):  # pragma: no cover
    def create_user(self, username, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError("Users must have: [username, first name, last_name]")

        user = self.model(username=username, first_name=first_name, last_name=last_name)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class ScheduleUser(AbstractBaseUser):
    username = models.CharField(
        verbose_name="username",
        max_length=32,
        unique=True,
    )
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    from .group import StudentGroup

    group = models.ForeignKey(
        StudentGroup, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_member = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ScheduleUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["USERNAME_FIELD", "first_name", "last_name"]

    def get_requests(self, group, page):
        req_users = ScheduleUser.objects.filter(group=group, is_member=False).order_by(
            "id"
        )
        return req_users[5 * page : 5 * (page + 1)], len(req_users)

    def get_members(self, group, page):
        members = ScheduleUser.objects.filter(group=group)
        return members[5 * page : 5 * (page + 1)], len(members)


class GroupLead(models.Model):
    group = models.OneToOneField(StudentGroup, unique=True, on_delete=models.CASCADE)
    user = models.OneToOneField(
        ScheduleUser, null=True, blank=True, default=None, on_delete=models.SET_NULL
    )
