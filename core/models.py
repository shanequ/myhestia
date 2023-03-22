from __future__ import unicode_literals

from PIL import Image
import os
import uuid
import StringIO
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from core.commons import CommonConst
from matters.models import MatterDocument
from myhestia.global_const import THUMBNAIL_SIZE, MD_THUMBNAIL_SIZE
from myhestia.privilege_const import STAFF_POSITIONS
from myhestia.settings import TMP_FILE_ROOT
from my_tools.storage_engine import make_file_path, GlobalStorage


class Staff(User):

    USER_TYPE_STAFF = 'S'
    USER_TYPE_SYSADMIN = 'A'
    USER_TYPE = ((USER_TYPE_STAFF, 'Staff'), (USER_TYPE_SYSADMIN, 'Sys Admin'),)

    STATUS_INACTIVE = 'I'
    STATUS_ACTIVE = 'A'
    STATUS_CHOICE = ((STATUS_INACTIVE, 'Inactive'), (STATUS_ACTIVE, 'Active'),)

    #
    # Business organization and system privileges
    #
    #   - line_manager, team and is_team_head describe business organization (only for display)
    #   - StaffPosition is for privileges in this system
    #   - user_type is simply to identity different user
    #
    # privilege has no relationship with business organization
    #
    user_type = models.CharField(max_length=1, choices=USER_TYPE, default=USER_TYPE_STAFF)

    # one staff only has one line manager
    line_manager = models.ForeignKey('core.Staff', blank=True, null=True, related_name='my_members')

    # one staff only belongs to one team
    team = models.ForeignKey('core.StaffTeam', related_name='team_members')

    # only 2 management level for each team - head and member, because most of agencies are small businesses
    is_team_head = models.BooleanField(default=False, blank=True)

    status = models.CharField(max_length=1, default=STATUS_ACTIVE, choices=STATUS_CHOICE)

    en_nickname = models.CharField(max_length=64)
    gender = models.CharField(max_length=8, default=CommonConst.GENDER_UNKNOWN, choices=CommonConst.GENDER_CHOICE)
    mobile = models.CharField(max_length=32, default='')
    personal_email = models.CharField(max_length=128, blank=True, default='')
    join_date = models.DateField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

    def __unicode__(self):
        return '%s %s (%s, ID: %s)' % (self.en_nickname, self.last_name, self.team, self.pk,)

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name]).title()

    def get_full_en_name(self):
        if self.en_nickname:
            return ' '.join([self.en_nickname, self.last_name]).title()
        else:
            return self.get_full_name()

    def get_short_desc(self):
        if self.en_nickname:
            return self.en_nickname.title()

        return self.first_name.title()

    def get_active_positions(self):
        return StaffPosition.objects.filter(staff=self, is_active=True)

    def get_active_position_desc(self):
        return ', '.join([p.get_position_display() for p in self.get_active_positions()])


class StaffPosition(models.Model):

    staff = models.ForeignKey('Staff', related_name='staff_positions')
    position = models.IntegerField(choices=STAFF_POSITIONS)
    is_active = models.BooleanField(blank=True, default=False)
    hr_notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.get_position_display()


class StaffTeam(models.Model):
    """
        Business organization
            - each staff must belong to one and only one business team
    """
    team_name = models.CharField(max_length=128, unique=True)
    parent_team = models.ForeignKey('core.StaffTeam', related_name='child_teams', null=True, blank=True)
    # start from 0
    level = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.team_name


class GlobalFile(models.Model):
    """
        All files
    """
    TYPE_THUMBNAIL_SM = 'thumbnail_sm'
    TYPE_THUMBNAIL_MD = 'thumbnail_md'

    TYPE_MANUAL_ATTACHMENT = 'attachment'
    TYPE_CHOICE = (
        (TYPE_MANUAL_ATTACHMENT, 'Attachment'),
    )

    FILE_TYPES = TYPE_CHOICE + MatterDocument.TYPE_CHOICE

    id = models.AutoField(primary_key=True)

    file_type = models.CharField(max_length=32, choices=FILE_TYPES)
    related_model_id = models.PositiveIntegerField(default=0)

    uuid = models.CharField(max_length=32, default='', unique=True)
    file = models.FileField(blank=True, upload_to=make_file_path, storage=GlobalStorage, max_length=255)
    file_ext = models.CharField(max_length=10, default='')
    notes = models.TextField(blank=True, default='')

    thumbnail = models.ForeignKey('core.GlobalFile', related_name='thumbnail_files', blank=True, null=True)
    md_thumbnail = models.ForeignKey('core.GlobalFile', related_name='md_thumbnail_files', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s: %s' % (self.id, self.get_file_type_display())

    def save(self, *args, **kwargs):
        # in v1.0, Thumbnail is not necessary.
        need_thumbnail = kwargs.get('need_thumbnail', False)
        if need_thumbnail and self.file_type not in [GlobalFile.TYPE_THUMBNAIL_SM, GlobalFile.TYPE_THUMBNAIL_MD]:
            self.thumbnail, self.md_thumbnail = self.make_thumbnail()

        super(GlobalFile, self).save(*args, **kwargs)

    def is_image(self):
        return self.file_ext.lower() in ['bmp', 'jpeg', 'jpg', 'jpe', 'png']

    @staticmethod
    def make_from_tmp(file_name, file_type, related_model_id=0):
        """
        Save file from temporary file in path TMP_FILE_ROOT

        Args:
            file_name - file name, like xxx.jpg
            file_type - ref. GlobalFile. FILE_TYPES

        Returns:
            GlobalFile instance

        """
        global_file = GlobalFile()
        global_file.related_model_id = related_model_id
        global_file.uuid = uuid.uuid4().hex
        global_file.file_type = file_type
        global_file.file_ext = file_name.split('.')[-1]

        #
        # save file to database.
        # whatever destination file name is, storage engine will recalculate it from uuid
        # ref. core.storage_engine.py
        #
        full_name = os.path.join(TMP_FILE_ROOT, file_name)
        tmp_file_content = File(open(full_name, 'rb'))
        global_file.file.save(file_name, tmp_file_content, save=True)
        global_file.save()

        return global_file

    def make_thumbnail(self):
        if not self.is_image():
            return None, None

        image = Image.open(self.file.name)

        # Convert to RGB if necessary
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contains proportions.
        # Additionally, we use Image. ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(MD_THUMBNAIL_SIZE, Image.ANTIALIAS)

        temp_handle = StringIO.StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile(os.path.split(self.file.name)[-1],
                                 temp_handle.read(), content_type='image/png')

        md_global_file = GlobalFile()
        md_global_file.uuid = uuid.uuid4().hex
        md_global_file.file_type = GlobalFile.TYPE_THUMBNAIL_MD
        md_global_file.file_ext = 'png'

        md_global_file.file.save(suf.name + '.png', suf, save=True)

        md_global_file.save()

        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        temp_handle = StringIO.StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile(os.path.split(self.file.name)[-1],
                                 temp_handle.read(), content_type='image/png')

        sm_global_file = GlobalFile()
        sm_global_file.uuid = uuid.uuid4().hex
        sm_global_file.file_type = GlobalFile.TYPE_THUMBNAIL_SM
        sm_global_file.file_ext = 'png'

        sm_global_file.file.save(suf.name + '.png', suf, save=True)

        sm_global_file.save()

        return sm_global_file, md_global_file
