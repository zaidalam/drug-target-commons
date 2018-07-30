from django.db import models

# Create your models here.
class Analytics(models.Model):
    #id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=200, blank=True, null=True)
    
