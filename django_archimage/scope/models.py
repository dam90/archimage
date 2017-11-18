# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Location(models.Model):
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)
	altitude = models.FloatField(blank=True, null=True)
	name = models.CharField(max_length=100,primary_key=True)