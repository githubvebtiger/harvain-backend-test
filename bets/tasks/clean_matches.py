import celery
from django.utils import timezone

from football.models import Match


@celery.shared_task(name="task_clean_matches")
def clean_matches():
    three_days_ago = timezone.now() - timezone.timedelta(days=3)
    Match.objects.filter(date__lte=three_days_ago).delete()
