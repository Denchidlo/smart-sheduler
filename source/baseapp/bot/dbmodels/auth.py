from .group import StudentGroup
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class ScheduleUserManager(BaseUserManager):
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
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    request_group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ScheduleUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["USERNAME_FIELD", "first_name", "last_name"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def get_chatlist(self, group):
        members = ScheduleUser.objects.filter(group=group)
        chat_list = members.chat_set.select_relaced()
        return [el.chat_id for el in chat_list]

    def get_requests(self, group, page):
        req_users = ScheduleUser.objects.filter(request_group=group).order_by("id")
        return req_users[5 * page : 5 * (page + 1)], len(req_users)

    
class GroupLead(models.Model):
    group = models.OneToOneField(StudentGroup, unique=True, on_delete=models.CASCADE)
    user = models.OneToOneField(ScheduleUser, null=True, blank=True, default=None, on_delete=models.SET_NULL)