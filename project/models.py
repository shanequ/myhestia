from __future__ import unicode_literals
from django.db import models
from matters.models import MatterRecord, MatterNotification


class Project(models.Model):
    """
        a group of matters
    """

    title = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return '%s (ID: %s)' % (self.title, self.pk,)

    def get_conveying_matters(self):
        return self.project_matters.exclude(matter_type=MatterRecord.TYPE_OTHER).distinct().prefetch_related('project')

    def get_other_matters(self):
        return self.project_matters.filter(matter_type=MatterRecord.TYPE_OTHER).distinct().prefetch_related('project')

    def get_mns(self):
        return MatterNotification.objects.filter(matter__project=self).distinct()

