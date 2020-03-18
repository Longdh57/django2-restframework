from django.db import connection


def refresh_shop_full_data():
    with connection.cursor() as cursor:
        cursor.execute("REFRESH MATERIALIZED VIEW shop_full_data")
