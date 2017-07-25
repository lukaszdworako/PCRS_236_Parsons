from django_cron import CronJobBase, Schedule
from problems_r.models import FileSubmissionManager
from problems.models import FileUpload
from django.utils import timezone
from pcrs.settings_r import FILE_DELETE_FREQUENCY

class FileCronJob(CronJobBase):
    """
    A cron job class for deleting expired FileUploads.
    """
    RUN_EVERY_MINS = FILE_DELETE_FREQUENCY

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'problems_r.file_cron_job'

    def do(self):
        """
        Delete FileUploads which lifespan's have passed.

        @return None
        """
        # Retrieve each FileUpload that has expired
        expired_files = FileUpload.objects.filter(lifespan__lte=timezone.now())

        for f in expired_files:
            try:
                # This file was used with a submission
                affected_subs = FileSubmissionManager.objects.get(data_set=f)
                f.delete()
                affected_subs.delete()
            except Exception as e:
                f.delete()
