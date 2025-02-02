import logging

import sh

from django.core.files import File
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.storage.utils import NamedTemporaryFile

from ..classes import SourceBackend
from ..settings import setting_backend_arguments

from .mixins import SourceBackendInteractiveMixin, SourceBaseMixin

__all__ = ('SourceBackendSANEScanner',)
logger = logging.getLogger(name=__name__)


class SourceBackendSANEScanner(
    SourceBackendInteractiveMixin, SourceBaseMixin, SourceBackend
):
    field_order = ('device_name', 'arguments')
    fields = {
        'device_name': {
            'class': 'django.forms.CharField',
            'help_text': _(
                'Device name as returned by the SANE backend.'
            ),
            'kwargs': {'max_length': 255},
            'label': _('Device name'),
            'required': True
        },
        'arguments': {
            'class': 'django.forms.CharField',
            'help_text': _(
                'YAML formatted arguments to pass to the `scanimage` '
                'command. The arguments will change depending on the '
                'device. Execute `scanimage --help --device-name=DEVICE` '
                'for the list of supported arguments.'
            ),
            'label': _('Arguments'),
            'required': False,
        },
    }
    label = _('SANE Scanner')
    widgets = {
        'arguments': {
            'class': 'django.forms.widgets.Textarea', 'kwargs': {
                'attrs': {
                    'rows': 10
                }
            }
        }
    }

    def get_shared_uploaded_files(self):
        command_scanimage = sh.Command(
            path=setting_backend_arguments.value[
                'mayan.apps.sources.source_backends.SourceBackendSaneScanner'
            ]['scanimage_path']
        )

        with NamedTemporaryFile() as file_object:
            command_scanimage = command_scanimage.bake(
                device_name=self.kwargs['device_name'],
                format='tiff', output_file=file_object.name
            )
            loaded_arguments = yaml_load(
                stream=self.kwargs.get('arguments', '{}')
            ) or {}
            command_scanimage(**loaded_arguments)

            file_object.seek(0)

            return (
                SharedUploadedFile.objects.create(
                    file=File(file=file_object), filename='scan {}'.format(
                        now()
                    )
                ),
            )

    def get_view_context(self, context, request):
        return {
            'subtemplates_list': [
                {
                    'name': 'appearance/generic_multiform_subtemplate.html',
                    'context': {
                        'forms': context['forms'],
                        'is_multipart': True,
                        'title': _('Document properties'),
                        'submit_label': _('Scan'),
                    },
                }
            ]
        }
