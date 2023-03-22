from __future__ import unicode_literals
import collections
from django.db import models
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator
from core.commons import CommonConst
from n_template.common import NConst
from n_template.models import NReceiver, NTemplate, AttachmentType


class MatterRecord(models.Model):

    TYPE_SALE_EXISTING = 'SEP'
    TYPE_PURCHASE_OFF_PLAN = 'POP'
    TYPE_PURCHASE_EXISTING = 'PEP'
    TYPE_OTHER = 'OT'

    TYPE_CHOICE = (
        (TYPE_PURCHASE_OFF_PLAN, 'Purchase Off-Plan Property'),
        (TYPE_PURCHASE_EXISTING, 'Purchase Existing Property'),
        (TYPE_SALE_EXISTING, 'Sell Existing Property'),
        (TYPE_OTHER, 'Other'),
    )

    STATUS_ACTIVE = 'A'
    STATUS_STAMP_DUTY_PAID = 'P'
    STATUS_CLOSED = 'C'
    STATUS_CHOICE = ((STATUS_ACTIVE, 'Active'), (STATUS_CLOSED, 'Closed'), (STATUS_STAMP_DUTY_PAID, 'Stamp Duty Paid'),)

    project = models.ForeignKey('project.Project', related_name='project_matters',
                                blank=True, null=True, on_delete=models.SET_NULL)

    matter_num = models.CharField(max_length=64, default='', blank=True)
    matter_type = models.CharField(max_length=8, choices=TYPE_CHOICE)
    status = models.CharField(max_length=1, default=STATUS_ACTIVE, choices=STATUS_CHOICE)

    matter_admin = models.ForeignKey('core.Staff', related_name='admin_matters')
    clients = models.ManyToManyField('clientdb.Client', related_name='client_matters')

    #
    # For "other" matter
    #
    subject = models.CharField(max_length=255, default='', blank=True)

    #
    # conveying matter
    #
    property_street = models.CharField(max_length=255, default='', blank=True)
    property_suburb = models.CharField(max_length=64, default='', blank=True)
    property_postcode = models.CharField(max_length=16, default='', blank=True)
    property_state = models.CharField(max_length=32, choices=CommonConst.AUS_STATE_CHOICE, default='', blank=True)

    agent_contact = models.ForeignKey('agent.AgentContact', related_name='agent_contact_matters', blank=True, null=True)

    # solicitor / handling fee earner
    solicitor_name = models.CharField(max_length=255, default='')
    solicitor_email = models.EmailField(default='')
    solicitor_mobile = models.CharField(max_length=32, default='')

    stamp_duty_amount = models.DecimalField(max_digits=12, decimal_places=2, default='0.00', blank=True, null=True)
    stamp_duty_due_date = models.DateField(blank=True, null=True)
    stamp_duty_paid_date = models.DateField(blank=True, null=True)

    contract_exchange_date = models.DateField(blank=True, null=True)
    cooling_off_date = models.DateField(blank=True, null=True)
    settlement_date = models.DateField(blank=True, null=True)

    matter_close_date = models.DateField(blank=True, null=True)

    memo = models.TextField(default='', blank=True)

    created_by = models.ForeignKey('core.Staff', related_name='created_matters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Matter No. %s / %s' % (self.matter_num, self.get_matter_type_display())

    def get_id_desc(self):
        return "M%06d" % self.pk

    def make_doc_file_dict(self):
        """
        Return:
            file dict. key is Project.FILE_FIELD_TYPE, value is a list of ProjectFile for this type.
            for example:
            {
                'da_file_pdf': [ProjectFile, ProjectFile, ...,],
                'da_file_cad': [ProjectFile, ProjectFile, ...,],
                ...
            }
        """
        ret = {}
        _docs = self.matter_docs.all().order_by('doc_type')
        for _doc in _docs:
            if _doc.doc_type in ret:
                ret[_doc.doc_type]['data'].append(_doc)
            else:
                ret[_doc.doc_type] = {
                    'display': _doc.get_doc_type_display(), 'data': [_doc],
                }

        return collections.OrderedDict(sorted(ret.items()))

    def type2nt_category(self):
        _mapping = {
            self.TYPE_SALE_EXISTING: NTemplate.CATEGORY_MATTER_SALE_EXISTING,
            self.TYPE_PURCHASE_OFF_PLAN: NTemplate.CATEGORY_MATTER_PURCHASE_OFF_PLAN,
            self.TYPE_PURCHASE_EXISTING: NTemplate.CATEGORY_MATTER_PURCHASE_EXISTING,
        }
        return _mapping.get(self.matter_type, '')

    def get_exchange_advice_date_times(self):
        return self.mns.filter(status=MatterNotification.STATUS_SENT,
                               template_trigger=NTemplate.TRIGGER_EXCHANGE,
                               template_trigger_days=0)\
            .values_list('sent_at', flat=True).distinct().order_by('-sent_at')

    def get_missed_docs(self):
        """
        Whether the matter has documents which will be emailed out as attachments

        Args:
            matter:

        Return:
            [<AttachmentType>] or []
        """
        # get attachments needed
        attachments = AttachmentType.objects.filter(attachment_mns__matter=self,
                                                    category=AttachmentType.CATEGORY_MATTER,
                                                    attachment_mns__status=MatterNotification.STATUS_WAITING).distinct()

        matter_docs = self.matter_docs.values_list('doc_type', flat=True)

        missed_docs = []
        for attachment in attachments:
            doc_type = attachment.map2_matter_doc_type()
            if not doc_type or doc_type not in matter_docs:
                missed_docs.append(attachment)

        return missed_docs


class MatterDocument(models.Model):

    TYPE_CONTRACT = 'matter_contract'
    TYPE_DEED = 'matter_deed'
    TYPE_NOTICE = 'matter_notice'
    TYPE_LETTER = 'matter_letter'

    TYPE_CHOICE = (
        (TYPE_CONTRACT, "Matter Contract"),
        (TYPE_DEED, "Matter Deed"),
        (TYPE_NOTICE, "Matter Notice"),
        (TYPE_LETTER, "Matter Letter"),
    )

    matter = models.ForeignKey('MatterRecord', related_name='matter_docs')
    doc_type = models.CharField(max_length=32, choices=TYPE_CHOICE)
    global_file = models.ForeignKey('core.GlobalFile', related_name='gf_matter_docs')
    notes = models.TextField(blank=True, default='')

    def __unicode__(self):
        return 'Matter No.: %s, %s' % (self.matter.matter_num, self.get_doc_type_display())


class MatterNotification(models.Model):
    """
        Matter Notification - generated from template or manually
    """
    STATUS_WAITING = "W"
    STATUS_SENT = "S"
    STATUS_INACTIVE = "I"
    STATUS_CHOICE = (
        (STATUS_WAITING, "Waiting To Send"),
        (STATUS_SENT, "Sent"),
        (STATUS_INACTIVE, "Inactive"),
    )

    matter = models.ForeignKey("matters.MatterRecord", related_name="mns")

    #
    # system generated from template when create/update matter or manually.
    #
    is_manual = models.BooleanField(default=False, blank=True)

    # email or sms
    send_type = models.CharField(max_length=4, default=NConst.SEND_TYPE_EMAIL, choices=NConst.SEND_TYPE_CHOICE)

    send_tos = models.ManyToManyField('n_template.NReceiver', related_name='send_to_mns', blank=True)
    cc_tos = models.ManyToManyField('n_template.NReceiver', related_name='cc_to_mns', blank=True)

    expect_sent_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=1, choices=STATUS_CHOICE, default=STATUS_WAITING)

    subject = models.CharField(max_length=128, blank=True, default='')
    content = models.TextField()

    # 2 kinds of attachment types - manually or predefined
    attachments = models.ManyToManyField('n_template.AttachmentType', related_name='attachment_mns', blank=True)
    # manually
    manual_attachment_gfs = models.ManyToManyField('core.GlobalFile', related_name='manual_attachment_gf_mns', blank=True)

    #
    # template snapshot if it's not manual
    #
    template = models.ForeignKey("n_template.NTemplate", related_name="n_template_mns", blank=True, null=True)
    template_category = models.CharField(max_length=8, choices=NTemplate.CATEGORY_CHOICE, default='', blank=True)
    template_trigger = models.CharField(max_length=8, choices=NTemplate.TRIGGER_CHOICE, default='', blank=True)
    template_trigger_days = models.SmallIntegerField(default=0)

    created_by = models.ForeignKey('core.Staff', related_name='created_mns')
    updated_by = models.ForeignKey('core.Staff', related_name='updated_mns', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "ID: %s" % self.pk

    def get_id_desc(self):
        return "N%06d" % self.pk

    def get_attachment_desc(self):
        if self.attachments.exists():
            return ", ".join([a.get_type_name_display() for a in self.attachments.all()])

        _count = self.manual_attachment_gfs.count()
        if _count > 0:
            return '%s uploaded attachment(%s)' % (_count, pluralize(_count, 's,es'))

    def get_trigger_desc(self):

        if self.is_manual:
            return "Manually"

        if self.template_trigger_days == 0:
            desc = "On The Day of %s" % self.get_template_trigger_display()
        elif self.template_trigger_days < 0:
            _days = abs(self.template_trigger_days)
            desc = "%s day%s Before %s" % (_days, pluralize(_days), self.get_template_trigger_display(),)
        else:
            _days = self.template_trigger_days
            desc = "%s day%s After %s" % (_days, pluralize(_days), self.get_template_trigger_display(),)

        return desc

    def get_send_to_emails(self):
        if not self.send_tos.exists():
            return []

        _emails = []
        for _to in self.send_tos.all():

            if _to.receiver == NReceiver.RECEIVER_CLIENT:
                _emails.extend([c.email for c in self.matter.clients.all()])

            elif _to.receiver == NReceiver.RECEIVER_STAFF and self.matter.matter_admin:
                _emails.extend([self.matter.matter_admin.email])

            elif _to.receiver == NReceiver.RECEIVER_AGENT and self.matter.agent_contact:
                _emails.extend([self.matter.agent_contact.contact_email])

            elif _to.receiver == NReceiver.RECEIVER_SOLICITOR and self.matter.solicitor_email:
                _emails.extend([self.matter.solicitor_email])

        return _emails

    def get_send_cc_emails(self):
        _emails = []
        for _cc in self.cc_tos.all():
            if _cc.receiver == NReceiver.RECEIVER_CLIENT:
                _emails.extend([c.email for c in self.matter.clients.all()])

            elif _cc.receiver == NReceiver.RECEIVER_AGENT and self.matter.agent_contact:
                _emails += [self.matter.agent_contact.contact_email]

            elif _cc.receiver == NReceiver.RECEIVER_STAFF and self.matter.matter_admin:
                _emails += [self.matter.matter_admin.email]

            elif _cc.receiver == NReceiver.RECEIVER_SOLICITOR and self.matter.solicitor_email:
                _emails += [self.matter.solicitor_email]

        return _emails

    def get_sms_mobiles(self):
        _mobiles = []
        for _to in self.send_tos.all():
            if _to.receiver == NReceiver.RECEIVER_CLIENT:
                _mobiles.extend([c.mobile for c in self.matter.clients.all()])

            # elif _to.receiver == NReceiver.RECEIVER_STAFF and self.matter.matter_admin:
            # send staff email
            #    _mobiles.extend([self.matter.matter_admin.mobile])

            elif _to.receiver == NReceiver.RECEIVER_AGENT and self.matter.agent_contact:
                _mobiles.extend([self.matter.agent_contact.contact_mobile])

            elif _to.receiver == NReceiver.RECEIVER_SOLICITOR and self.matter.solicitor_mobile:
                _mobiles.extend([self.matter.solicitor_mobile])

        return _mobiles

    def get_attach_global_files(self):

        if self.attachments.exists():
            _doc_types = []
            for a in self.attachments.all():
                _doc_type = a.map2_matter_doc_type()
                if _doc_type != '':
                    _doc_types.append(_doc_type)

            docs = self.matter.matter_docs.filter(doc_type__in=_doc_types).order_by('doc_type')
            return [d.global_file for d in docs]

        if self.manual_attachment_gfs.exists():
            return self.manual_attachment_gfs.all()

    def get_missed_docs(self):
        """
        Whether the matter has documents which will be emailed out as attachments

        Args:
            matter:

        Return:
            [<AttachmentType>] or []
        """
        if self.status != self.STATUS_WAITING:
            return []

        # get attachments needed
        attachments = self.attachments.filter(category=AttachmentType.CATEGORY_MATTER).distinct()

        matter_docs = self.matter.matter_docs.values_list('doc_type', flat=True)

        missed_docs = []
        for attachment in attachments:
            doc_type = attachment.map2_matter_doc_type()
            if not doc_type or doc_type not in matter_docs:
                missed_docs.append(attachment)

        return missed_docs
