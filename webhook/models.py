from django.db import models

class DropboxUser(models.Model):
	uid = models.CharField(max_length=255)
	cursor = models.CharField(max_length=255, null = True, blank = True)