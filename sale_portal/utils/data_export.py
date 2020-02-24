from django.db import connection

merchant_raw_query = '''select * from merchant
'''

terminal_raw_query = '''select t.id as id, m.merchant_code, m.merchant_brand, m.merchant_name,
t.terminal_id, t.terminal_name, t.business_address,
t.province_code, qr_pro.province_name,
t.district_code, qr_dis.district_name,
t.wards_code, qr_war.wards_name,
t.created_date, sh.code as shop_code, sh.name as shop_name, sh.address as shop_address,
stt.email as staff_email, stt.team as team_code
from terminal t
left join merchant m on t.merchant_id = m.id
left join qr_province qr_pro on qr_pro.province_code = t.province_code
left join qr_district qr_dis on qr_dis.district_code = t.district_code
left join qr_wards qr_war on qr_war.wards_code = t.wards_code
left join shop sh on t.shop_id = sh.id
left join (select st.email, tm.code as team, stc.shop_id from staff st
            left join team tm on st.team_id = tm.id
            inner join staff_care stc on st.id = stc.staff_id and stc.type = 0) stt on stt.shop_id = t.shop_id
'''

shop_raw_query = '''select s.id, m.merchant_brand, stt.email as staff_email, stt.team as team_code,
qr_pro.province_name, qr_dis.district_name, qr_war.wards_name, s.address,
(select count(*) from terminal where shop_id = s.id) as count_ter,
sc.number_of_tran_w_1_7 as k1, sc.number_of_tran_w_8_14 as k2, sc.number_of_tran_w_15_21 as k3, sc.number_of_tran_w_22_end as k4,
s.created_date
from shop s
left join merchant m on s.merchant_id = m.id
left join (select st.email, tm.code as team, stc.shop_id from staff st
            left join team tm on st.team_id = tm.id
            inner join staff_care stc on st.id = stc.staff_id and stc.type = 0) stt on stt.shop_id = s.id
left join qr_province qr_pro on qr_pro.id = s.province_id
left join qr_district qr_dis on qr_dis.id = s.district_id
left join qr_wards qr_war on qr_war.id = s.wards_id
left join shop_cube sc on sc.shop_id = s.id'''


class ExportType:
    MERCHANT = 111
    TERMINAL = 222
    SHOP = 333


def get_data_export(ids_queryset, type=None):

    if type is None:
        return []

    ids = '('

    for item in ids_queryset.values('id'):
        ids += str(item['id']) + ','
    ids = ids[:-1]
    ids += ')'

    if len(ids) < 3:
        return []

    if type == ExportType.MERCHANT:
        raw_query = merchant_raw_query + ' where m.id in ' + ids
    elif type == ExportType.TERMINAL:
        raw_query = terminal_raw_query + ' where t.id in ' + ids + ' order by t.created_date desc'
    elif type == ExportType.SHOP:
        raw_query = shop_raw_query + ' where s.id in ' + ids + ' order by s.created_date desc'
    else:
        return []

    with connection.cursor() as cursor:
        cursor.execute(raw_query)
        columns = [col[0] for col in cursor.description]
        data_cursor = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    return data_cursor


