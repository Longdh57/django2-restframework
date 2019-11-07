import os
import logging

from django.db import connection
from django.core.management.base import BaseCommand, CommandError

from sale_portal.staff.models import Staff, StaffLog
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Compare table qr_staff and staff'

    def get_sql_query(self):
        sql_path = '/sql_query/staff_synchronize_change_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def create_staff_log(self, staff=None, qr_staff=None, status=0):
        old_data, new_data = {}, {}
        try:
            if staff is not None:
                old_data = {
                    'id': staff.id,
                    'staff_code': staff.staff_code,
                    'nick_name': staff.nick_name,
                    'full_name': staff.full_name,
                    'email': staff.email,
                    'mobile': staff.mobile,
                    'department_code': staff.department_code,
                    'status': staff.status,
                    'department_id': staff.department_id,
                    'created_date': str(staff.created_date),
                    'modify_date': str(staff.modify_date),
                }
            if qr_staff is not None:
                new_data = {
                    'id': qr_staff['qr_staff_id'],
                    'staff_code': qr_staff['qr_staff_code'],
                    'nick_name': qr_staff['qr_nick_name'],
                    'full_name': qr_staff['qr_full_name'],
                    'email': qr_staff['qr_email'],
                    'mobile': qr_staff['qr_mobile'],
                    'department_code': qr_staff['qr_department_code'],
                    'status': qr_staff['qr_status'],
                    'department_id': qr_staff['qr_department_id'],
                    'created_date': str(qr_staff['qr_created_date']),
                    'modify_date': str(qr_staff['qr_modify_date']),
                }
            StaffLog(
                old_data=old_data,
                new_data=new_data,
                type=status,
                staff_id=qr_staff['qr_staff_id'] if status != 1 else staff.id
            ).save()
        except Exception as e:
            logging.error('Job staff_synchronize_change - create_staff_log exception: %s', e)
        return

    def handle(self, *args, **options):
        cronjob = cron_create(name='staff_synchronize_change', type='staff')

        try:
            self.stdout.write(self.style.SUCCESS('Start staff synchronize change processing...'))
            created, updated, deleted = 0, 0, 0
            with connection.cursor() as cursor:
                cursor.execute(self.get_sql_query())
                columns = [col[0] for col in cursor.description]
                data_cursor = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            for data in data_cursor:
                if data['status'] == 0:
                    self.create_staff_log(staff=None, qr_staff=data, status=data['status'])
                    staff = Staff(
                        id=data['qr_staff_id'],
                        staff_code=data['qr_staff_code'],
                        nick_name=data['qr_nick_name'],
                        full_name=data['qr_full_name'],
                        email=data['qr_email'],
                        mobile=data['qr_mobile'],
                        department_code=data['qr_department_code'],
                        status=data['qr_status'],
                        department_id=data['qr_department_id'],
                        created_date=data['qr_created_date'],
                        modify_date=data['qr_modify_date'],
                    )
                    staff.save()
                    created += 1

                elif data['status'] == 1:
                    staff = Staff.objects.filter(pk=data['s_staff_id']).first()
                    self.create_staff_log(staff=staff, qr_staff=None, status=data['status'])
                    staff.delete()
                    deleted += 1

                elif data['status'] == 2:
                    try:
                        staff = Staff.objects.filter(pk=data['s_staff_id']).first()
                        self.create_staff_log(staff=staff, qr_staff=data, status=data['status'])

                        staff.staff_code = data['qr_staff_code']
                        staff.nick_name = data['qr_nick_name']
                        staff.full_name = data['qr_full_name']
                        staff.email = data['qr_email']
                        staff.mobile = data['qr_mobile']
                        staff.status = data['qr_status']
                        staff.department_id = data['qr_department_id']
                        staff.department_code = data['qr_department_code']
                        staff.created_date = data['qr_created_date']
                        staff.modify_date = data['qr_modify_date']
                        staff.save()

                        updated += 1

                    except Staff.DoesNotExist:
                        raise CommandError('Staff with staff_id: "%s" does not exist' % (data['s_staff_id']))
                else:
                    pass

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully command. Created: {}. Updated: {}. Deleted: {}'.format(created, updated, deleted)))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job staff_synchronize_change exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
