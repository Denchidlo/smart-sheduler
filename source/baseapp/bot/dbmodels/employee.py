from django.db import models

class Employee(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    middle_name = models.CharField(max_length=40)
    fio = models.CharField(max_length=45)
    bsiur_id = models.IntegerField(primary_key=True, auto_created=False, unique=True)