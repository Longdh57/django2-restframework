from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Set table_id_seq to max id'

    def handle(self, *args, **options):
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data_cursor = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        for item in data_cursor:
            try:
                seq_query = "SELECT setval('" + str(item['table_name']) + "_id_seq', (SELECT MAX(id) FROM " + str(
                    item['table_name']) + ") +1) from " + str(item['table_name']) + ";"
                print(seq_query)
                cursor.execute(seq_query)
            except Exception as e:
                self.style.ERROR('Repair_id_seq error at table {}: {}'.format(item['table_name'], e))
