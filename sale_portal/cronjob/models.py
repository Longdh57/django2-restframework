from django.db import models


class CronjobLog(models.Model):
    STATUS = (
        (0, 'PROCESSING'),
        (1, 'DONE'),
        (2, 'ERROR'),
    )
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=100, null=False)
    status = models.IntegerField(choices=STATUS, default=0)
    description = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cronjob_log'
        ordering = ['-created_date']
        default_permissions = ()
        permissions = (
            ('cronjob_log_list_data', 'Can get cronjob_log list data'),
        )
