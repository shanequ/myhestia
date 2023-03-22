from __future__ import unicode_literals
from django.db import models
from django.db.models import Q

from matters.models import MatterRecord, MatterNotification


class Agent(models.Model):

    agent_name = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.agent_name

    def get_conveying_matters(self):
        return MatterRecord.objects.filter(~Q(matter_type=MatterRecord.TYPE_OTHER) &
                                           Q(agent_contact__agent=self)).select_related('agent_contact')

    def get_mns(self):
        return MatterNotification.objects.filter(matter__agent_contact__agent=self).distinct()


class AgentContact(models.Model):

    agent = models.ForeignKey('Agent', related_name='agent_contacts')

    contact_name = models.CharField(max_length=128)
    contact_email = models.EmailField()
    contact_mobile = models.CharField(max_length=32)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s (%s, %s)" % (self.contact_name, self.agent.agent_name, self.contact_email,)
