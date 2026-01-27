from django.utils import timezone

from rest_framework.serializers import ValidationError

def validate_future_date(date, error):
    if date and date <= timezone.now():
        raise ValidationError(error)

    return date
