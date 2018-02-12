from django.forms import ModelForm
from .models import Rpas,Manufacturer,RpasModelType,RpasModel,Payload


class ManufacturerForm(ModelForm):
    class Meta:
        model = Manufacturer
        fields = ('name','country')


class PayloadForm(ModelForm):
    class Meta:
        model = Payload
        fields = (
        'manufacturer',
        'payload_nickname',
        'payload_serial',
        )