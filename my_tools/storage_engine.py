import os
from django.core.files.storage import FileSystemStorage
from myhestia import settings
from myhestia.settings import DOC_FILE_ROOT

#
#
# the folder structure are:
#   DOC_FILE_ROOT/field_type/matter_id/file_name_in_uuid.ext
#
#   /var/www/xxx.doc/matter_contract/1/05ac62e34df546d7896e247378a95043.pdf
#
GlobalStorage = FileSystemStorage(location=settings.DOC_FILE_ROOT)


def make_file_path(instance, filename):

    ext = filename.split('.')[-1]
    # set filename as random string
    filename = '{}.{}'.format(instance.uuid, ext)

    # return the whole path to the file
    return os.path.join(DOC_FILE_ROOT, instance.file_type, str(instance.related_model_id), filename)
