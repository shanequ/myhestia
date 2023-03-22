from __future__ import unicode_literals
from django.db import models
from django.template.defaultfilters import pluralize
from n_template.common import NConst


class NTemplate(models.Model):

    STATUS_ACTIVE = 'A'
    STATUS_INACTIVE = 'IA'
    STATUS_CHOICE = ((STATUS_ACTIVE, 'In Use'), (STATUS_INACTIVE, 'Not In Use'))

    TRIGGER_EXCHANGE = 'EXC'
    TRIGGER_SETTLEMENT = 'SET'
    TRIGGER_STAMP_DUTY_DUE = 'SDD'
    TRIGGER_CHOICE = (
        (TRIGGER_EXCHANGE, 'Contract Exchange'), (TRIGGER_STAMP_DUTY_DUE, 'Stamp Duty Due'),
        (TRIGGER_SETTLEMENT, 'Settlement')
    )

    CATEGORY_MATTER_PURCHASE_OFF_PLAN = 'MPO'
    CATEGORY_MATTER_PURCHASE_EXISTING = 'MPE'
    CATEGORY_MATTER_SALE_EXISTING = 'MSE'
    CATEGORY_CHOICE = (
        (CATEGORY_MATTER_PURCHASE_OFF_PLAN, 'Purchase Off-Plan Property (Matter)'),
        (CATEGORY_MATTER_PURCHASE_EXISTING, 'Purchase Existing Property (Matter)'),
        (CATEGORY_MATTER_SALE_EXISTING, 'Sell Existing Property (Matter)'),
    )

    template_name = models.CharField(max_length=64, default='', unique=True)
    status = models.CharField(max_length=8, blank=True, default=STATUS_ACTIVE, choices=STATUS_CHOICE)

    # email or sms
    send_type = models.CharField(max_length=4, default=NConst.SEND_TYPE_EMAIL, choices=NConst.SEND_TYPE_CHOICE)

    # bind template to generate notification instance
    category = models.CharField(max_length=8, choices=CATEGORY_CHOICE, default='', blank=True)

    #
    trigger = models.CharField(max_length=8, choices=TRIGGER_CHOICE, default='', blank=True)

    # 0 - on the day, - before, + after
    trigger_days = models.SmallIntegerField(default=0)

    subject = models.CharField(max_length=128, blank=True, default='')
    content = models.TextField()

    # attachment types
    attachments = models.ManyToManyField('AttachmentType', related_name='attachment_n_templates', blank=True)

    send_tos = models.ManyToManyField('NReceiver', related_name='send_to_n_templates', blank=True)
    cc_tos = models.ManyToManyField('NReceiver', related_name='cc_to_n_templates', blank=True)

    def __unicode__(self):
        return self.template_name

    def get_trigger_desc(self):
        if self.trigger_days == 0:
            return "On The Day of %s" % self.get_trigger_display()

        elif self.trigger_days < 0:
            _days = abs(self.trigger_days)
            return "%s day%s Before %s" % (_days, pluralize(_days), self.get_trigger_display(),)

        return "%s day%s After %s" % (self.trigger_days, pluralize(self.trigger_days), self.get_trigger_display(),)

    def get_attachment_desc(self):
        return ", ".join([a.get_type_name_display() for a in self.attachments.all()])


class AttachmentType(models.Model):

    TYPE_CONTRACT = 'Contract'
    TYPE_DEED = 'Deed'
    TYPE_NOTICE = 'Notice'
    TYPE_LETTER = 'Letter'

    TYPE_CHOICE = (
        (TYPE_CONTRACT, TYPE_CONTRACT), (TYPE_DEED, TYPE_DEED), (TYPE_NOTICE, TYPE_NOTICE), (TYPE_LETTER, TYPE_LETTER),
    )

    CATEGORY_MATTER = 'M'
    CATEGORY_CHOICE = (
        (CATEGORY_MATTER, 'Matter'),
    )

    # only matter now - v1.0.0
    category = models.CharField(max_length=1, default=CATEGORY_MATTER, choices=CATEGORY_CHOICE)
    type_name = models.CharField(max_length=64, choices=TYPE_CHOICE)

    def __unicode__(self):
        return "ID: %s Type: %s" % (self.pk, self.get_type_name_display(),)

    def map2_matter_doc_type(self):
        from matters.models import MatterDocument
        _mapping = {
            self.TYPE_CONTRACT: MatterDocument.TYPE_CONTRACT,
            self.TYPE_DEED: MatterDocument.TYPE_DEED,
            self.TYPE_NOTICE: MatterDocument.TYPE_NOTICE,
            self.TYPE_LETTER: MatterDocument.TYPE_LETTER,
        }

        return _mapping.get(self.type_name, '')


class NReceiver(models.Model):

    RECEIVER_CLIENT = 'Client'
    RECEIVER_STAFF = 'Staff'
    RECEIVER_AGENT = 'Agent'
    RECEIVER_SOLICITOR = 'Solicitor/Conveyancer'

    RECEIVER_CHOICE = (
        (RECEIVER_CLIENT, RECEIVER_CLIENT), (RECEIVER_STAFF, RECEIVER_STAFF), (RECEIVER_AGENT, RECEIVER_AGENT),
        (RECEIVER_SOLICITOR, RECEIVER_SOLICITOR),
    )

    CATEGORY_MATTER = 'M'
    CATEGORY_CHOICE = (
        (CATEGORY_MATTER, 'Matter'),
    )

    # only matter now - v1.0.0
    category = models.CharField(max_length=1, default=CATEGORY_MATTER, choices=CATEGORY_CHOICE)
    receiver = models.CharField(max_length=64, choices=RECEIVER_CHOICE)

    def __unicode__(self):
        return "ID: %s Receiver: %s" % (self.pk, self.get_receiver_display(),)
