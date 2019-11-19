import logging
import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField

from sale_portal.team import TeamLogType


class Team(models.Model):
    name = models.CharField(max_length=255, null=False)
    code = models.CharField(max_length=20, unique=True, null=True)
    description = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team'
        default_permissions = ()

    def __init__(self, *args, **kwargs):
        super(Team, self).__init__(*args, **kwargs)
        self.__important_fields = ['name', 'code', 'description', 'created_date', 'updated_date']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def compare(self):
        old_data = {}
        new_data = {}
        type = TeamLogType.CREATED

        for field in self.__important_fields:
            orig = '__original_%s' % field
            old_data[field] = getattr(self, field) if not isinstance(getattr(self, field), datetime.date) else str(
                getattr(self, field))
            new_data[field] = getattr(self, orig) if not isinstance(getattr(self, orig), datetime.date) else str(
                getattr(self, orig))
            if getattr(self, orig) != getattr(self, field):
                type = TeamLogType.UPDATED
        return old_data, new_data, type

    def save(self, *args, **kwargs):
        try:
            old_data, new_data, type = self.compare()
            if type == TeamLogType.CREATED:
                TeamLog.objects.create(new_data=new_data, team_id=self.id, type=type)
            else:
                TeamLog.objects.create(old_data=old_data, new_data=new_data, team_id=self.id, type=type)
        except Exception as e:
            logging.error('Save team exception: %s', e)
        super(Team, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            old_data, new_data, type = self.compare()
            TeamLog.objects.create(old_data=old_data, team_id=self.id, type=TeamLogType.DELETED)
        except Exception as e:
            logging.error('Delete team exception: %s', e)
        super(Team, self).delete()

    def __str__(self):
        return self.name


class TeamLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    team_id = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(choices=TeamLogType.CHOICES)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'team_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data