from __future__ import unicode_literals

from django.db import models
from core.commons import CommonConst
from matters.models import MatterRecord, MatterNotification


class Client(models.Model):

    STATUS_ACTIVE = 'A'
    STATUS_INACTIVE = 'I'
    STATUS_CHOICE = ((STATUS_ACTIVE, 'Active'), (STATUS_INACTIVE, 'Inactive'),)

    status = models.CharField(max_length=1, choices=STATUS_CHOICE, default=STATUS_ACTIVE)

    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255)

    en_nickname = models.CharField(max_length=255, blank=True, default='')

    email = models.EmailField()
    mobile = models.CharField(max_length=32)

    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=CommonConst.GENDER_CHOICE, default=CommonConst.GENDER_UNKNOWN)

    memo = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s %s (%s, ID: %s, %s)" % \
               (self.en_nickname.title(), self.last_name.title(), self.first_name.title(), self.pk, self.email,)

    def get_short_desc(self):
        return '%s (ID: %s)' % (self.get_legal_name(), self.pk,)

    def get_legal_name(self):
        if self.middle_name:
            _full_name = '%s %s %s' % (self.first_name, self.middle_name, self.last_name,)
        else:
            _full_name = '%s %s' % (self.first_name, self.last_name,)

        return _full_name.title()

    def get_name_desc(self):
        return self.get_legal_name()

    def get_conveying_matters(self):
        return self.client_matters.exclude(matter_type=MatterRecord.TYPE_OTHER).distinct().prefetch_related('clients')

    def get_other_matters(self):
        return self.client_matters.filter(matter_type=MatterRecord.TYPE_OTHER).distinct().prefetch_related('clients')

    def get_mns(self):
        return MatterNotification.objects.filter(matter__clients=self).distinct()

