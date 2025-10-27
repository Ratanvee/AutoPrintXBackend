
# tasks.py (Optional - for Celery periodic tasks)
"""
If you want automatic cleanup using Celery, install:
pip install celery django-celery-beat

Then add this to your tasks.py:
"""
from celery import shared_task
from .models import OTPVerification

@shared_task
def delete_expired_otps():
    """Celery task to delete expired OTPs"""
    print("Deleting expired otps ....")
    count = OTPVerification.delete_expired()
    print("delete expired OTP")
    return f"Deleted {count} expired OTP records"

"""
# settings.py - Add Celery configuration
CELERY_BEAT_SCHEDULE = {
    'delete-expired-otps': {
        'task': 'smartdocx.tasks.delete_expired_otps',
        'schedule': 3600.0,  # Run every hour
    },
}
"""