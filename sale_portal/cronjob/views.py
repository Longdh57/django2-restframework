from sale_portal.cronjob.models import CronjobLog


def cron_create(name='default', type='default', status=0, description=None):
    cron_log = CronjobLog(
        name=name,
        type=type,
        status=status,
        description=description
    )
    cron_log.save()
    return cron_log


def cron_update(cronjob, status=0, description=None):
    cronjob.status = status
    if cronjob.description is not None:
        cronjob.description = str(cronjob.description) + (
            ('<br/>' + str(description)) if description is not None else None)
    else:
        cronjob.description = description
    cronjob.save()
    return
