from __future__ import unicode_literals
import datetime
from matters.models import MatterRecord, MatterNotification
from myhestia.global_const import DEFAULT_NOTIFICATION_SENT_TIME
from n_template.models import NTemplate, AttachmentType


def update_matter_notifications(new_matter, old_matter):

    if not isinstance(new_matter, MatterRecord):
        return []

    #
    # clear notifications
    #
    if not new_matter.contract_exchange_date:
        MatterNotification.objects.filter(matter=new_matter, is_manual=False,
                                          status=MatterNotification.STATUS_WAITING,
                                          template_trigger=NTemplate.TRIGGER_EXCHANGE).delete()

    if not new_matter.settlement_date:
        MatterNotification.objects.filter(matter=new_matter, is_manual=False,
                                          status=MatterNotification.STATUS_WAITING,
                                          template_trigger=NTemplate.TRIGGER_SETTLEMENT).delete()

    if not new_matter.stamp_duty_due_date:
        MatterNotification.objects.filter(matter=new_matter, is_manual=False,
                                          status=MatterNotification.STATUS_WAITING,
                                          template_trigger=NTemplate.TRIGGER_STAMP_DUTY_DUE).delete()

    #
    # make valid template type list
    #
    template_triggers = []
    if new_matter.contract_exchange_date:
        template_triggers.append(NTemplate.TRIGGER_EXCHANGE)

    if new_matter.settlement_date:
        template_triggers.append(NTemplate.TRIGGER_SETTLEMENT)

    if new_matter.stamp_duty_due_date:
        template_triggers.append(NTemplate.TRIGGER_STAMP_DUTY_DUE)

    _nt_category = new_matter.type2nt_category()
    if not _nt_category:
        return []

    templates = NTemplate.objects.filter(status=NTemplate.STATUS_ACTIVE,
                                         category=_nt_category, trigger__in=template_triggers)
    ret = []
    for t in templates:
        # if field is not changed, skip it
        if old_matter and\
                (
                    (t.trigger == NTemplate.TRIGGER_EXCHANGE and
                        new_matter.contract_exchange_date == old_matter.contract_exchange_date) or
                    (t.trigger == NTemplate.TRIGGER_SETTLEMENT and
                        new_matter.settlement_date == old_matter.settlement_date) or
                    (t.trigger == NTemplate.TRIGGER_STAMP_DUTY_DUE and
                        new_matter.stamp_duty_due_date == old_matter.stamp_duty_due_date)
                ):
            continue

        except_sent_date = make_matter_notification_sent_date(nt=t, matter=new_matter)
        if not except_sent_date:
            continue

        except_sent_at = datetime.datetime.combine(except_sent_date, DEFAULT_NOTIFICATION_SENT_TIME)

        MatterNotification.objects.filter(matter=new_matter, template=t,
                                          is_manual=False, status=MatterNotification.STATUS_WAITING).delete()

        n = MatterNotification()
        n.is_manual = False
        n.subject = t.subject
        n.content = t.content
        n.expect_sent_at = except_sent_at
        n.status = MatterNotification.STATUS_WAITING
        n.send_type = t.send_type
        n.template = t
        n.template_category = t.category
        n.template_trigger = t.trigger
        n.template_trigger_days = t.trigger_days

        n.matter = new_matter
        n.created_by = new_matter.created_by
        n.save()

        n.attachments.clear()
        n.attachments.add(*[a for a in t.attachments.all()])

        n.send_tos.clear()
        n.send_tos.add(*[a for a in t.send_tos.all()])

        n.cc_tos.clear()
        n.cc_tos.add(*[a for a in t.cc_tos.all()])

        ret.append(n)

    return ret


def make_matter_notification_sent_date(nt, matter):

    trigger_date = None
    if nt.trigger == NTemplate.TRIGGER_EXCHANGE:
        trigger_date = matter.contract_exchange_date

    elif nt.trigger == NTemplate.TRIGGER_SETTLEMENT:
        trigger_date = matter.settlement_date

    elif nt.trigger == NTemplate.TRIGGER_STAMP_DUTY_DUE:
        trigger_date = matter.stamp_duty_due_date

    if not trigger_date:
        return None

    return trigger_date + datetime.timedelta(nt.trigger_days)

