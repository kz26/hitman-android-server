from django.core.exceptions import ValidationError
from django.utils import timezone

def FutureDateValidator(value):
    if value <= timezone.now():
        raise ValidationError("Date/time must be in the future.")
