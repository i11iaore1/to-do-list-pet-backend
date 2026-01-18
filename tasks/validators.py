from django.utils import timezone

from rest_framework.serializers import ValidationError

def validate_future_date(date, error_text):
    if date and date <= timezone.now():
        raise ValidationError(error_text)

    return date
