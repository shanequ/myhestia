"""
    Models for Email
"""
import datetime

from django.db import models


class MPEmail(models.Model):
    STATUS_SENT = 'S'
    STATUS_CHOICE = ((STATUS_SENT, 'Sent'),
                     ('P', 'Pending'),
                     ('R', 'Resending'),
                     ('F', 'Failure to send'),
                     ('C', 'Cancelled'),)

    RETRY_LIMIT = 3

    insert_time = models.DateTimeField(auto_now_add=True)
    last_attempt_time = models.DateTimeField(null=True, blank=True)
    sent_out_time = models.DateTimeField(null=True, blank=True)
    failure_count = models.SmallIntegerField(blank=True, default=0)

    status = models.CharField(max_length=8, choices=STATUS_CHOICE, default='P')

    subject = models.CharField(max_length=128)
    to_email = models.TextField()
    cc_email = models.TextField(blank=True, default='')
    bcc_email = models.TextField(blank=True, default='')
    from_email = models.TextField(blank=True, default='')
    from_email_desc = models.CharField(max_length=64, blank=True, default='')
    text_content = models.TextField(blank=True, default='')
    html_content = models.TextField(blank=True, default='')
    no_reply = models.BooleanField(default=False, blank=True)
    reply_to = models.EmailField(null=True, blank=True)
    image_list = models.TextField(blank=True, default='')
    attach_file_list = models.TextField(blank=True, default='')
    failure_log = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Multipart Email'
        verbose_name_plural = 'Multipart Emails'

    def failed(self):
        self.failure_count += 1
        if self.failure_count >= self.RETRY_LIMIT:
            self.status = 'F'
        else:
            self.status = 'R'

    def sent(self):
        self.status = 'S'
        self.sent_out_time = datetime.datetime.now()


class SMS(models.Model):
    STATUS_SENT = 'S'
    STATUS = (('P', 'Pending'), (STATUS_SENT, 'Sent'), ('F', 'Fail'), ('C', 'Cancel'),)
    PRIORITY = (('L', 'Low'), ('M', 'Mediate'), ('H', 'High'), ('C', 'Critical'),)

    status = models.CharField(max_length=8, choices=STATUS, default='P')
    insert_time = models.DateTimeField(auto_now_add=True)
    sms_priority = models.CharField(max_length=8, default='M')
    sms_from = models.CharField(max_length=32, null=True, blank=True)
    sms_subject = models.CharField(max_length=32, null=True, blank=True)
    sms_text = models.TextField()
    target_numbers = models.CharField(max_length=4096)
    sp_response = models.CharField('Result', max_length=128, null=True, blank=True)
    note = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = 'SMS'
        verbose_name_plural = 'SMSs'

    def target_count(self):
        if self.target_numbers:
            return self.target_numbers.count(',') + 1
        return 0
