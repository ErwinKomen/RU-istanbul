from django.apps import apps
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Generic(models.Model):
	name = models.CharField(max_length=300,blank=True,null=True)

