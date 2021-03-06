# Generated by Django 2.2.7 on 2020-03-18 14:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('shop_cube', '0006_auto_20200609_2213'),
    ]

    operations = [
        migrations.RunSQL(
            '''
            DROP MATERIALIZED VIEW IF EXISTS shop_full_data;
            CREATE MATERIALIZED VIEW shop_full_data as
            select sh.id              as id,
                   sh.name,
                   sh.code,
                   sh.street,
                   sh.address,
                   sh.activated,
                   sh.take_care_status,
                   sh.created_date,
                   m.id               as merchant_id,
                   m.merchant_brand,
                   m.merchant_code,
                   qp.id              as province_id,
                   qp.province_name,
                   qd.id              as district_id,
                   qd.district_name,
                   qw.id              as wards_id,
                   qw.wards_name,
                   s.id               as staff_id,
                   s.email            as staff_email,
                   t.id               as team_id,
                   t.name             as team_name,
                   t.area_id          as area_id,
                   ter.count_terminal as count_terminals,
                   scube.report_date,
                   scube.number_of_tran_acm,
                   scube.number_of_tran_last_m,
                   scube.number_of_tran,
                   scube.number_of_tran_w_1_7,
                   scube.number_of_tran_w_8_14,
                   scube.number_of_tran_w_15_21,
                   scube.number_of_tran_w_22_end,
                   scube.voucher_code_list
            from shop sh
                     left join merchant m on sh.merchant_id = m.id
                     left join qr_province qp on sh.province_id = qp.id
                     left join qr_district qd on sh.district_id = qd.id
                     left join qr_wards qw on sh.wards_id = qw.id
                     left join staff_care sc on sh.id = sc.shop_id and sc.type = 0
                     left join staff s on sc.staff_id = s.id
                     left join team t on s.team_id = t.id
                     left join shop_cube scube on sh.id = scube.shop_id
                     left join (select count(shop_id) as count_terminal, shop_id from terminal group by shop_id) ter
                               on ter.shop_id = sh.id
            order by id desc;
            ''',
            '''
            DROP MATERIALIZED VIEW IF EXISTS shop_full_data;
            CREATE MATERIALIZED VIEW shop_full_data as
            select sh.id              as id,
                   sh.name,
                   sh.code,
                   sh.street,
                   sh.address,
                   sh.activated,
                   sh.take_care_status,
                   sh.created_date,
                   m.id               as merchant_id,
                   m.merchant_brand,
                   m.merchant_code,
                   qp.id              as province_id,
                   qp.province_name,
                   qd.id              as district_id,
                   qd.district_name,
                   qw.id              as wards_id,
                   qw.wards_name,
                   s.id               as staff_id,
                   s.email            as staff_email,
                   t.id               as team_id,
                   t.name             as team_name,
                   t.area_id          as area_id,
                   ter.count_terminal as count_terminals,
                   scube.report_date,
                   scube.number_of_tran,
                   scube.number_of_tran_w_1_7,
                   scube.number_of_tran_w_8_14,
                   scube.number_of_tran_w_15_21,
                   scube.number_of_tran_w_22_end,
                   scube.voucher_code_list
            from shop sh
                     left join merchant m on sh.merchant_id = m.id
                     left join qr_province qp on sh.province_id = qp.id
                     left join qr_district qd on sh.district_id = qd.id
                     left join qr_wards qw on sh.wards_id = qw.id
                     left join staff_care sc on sh.id = sc.shop_id and sc.type = 0
                     left join staff s on sc.staff_id = s.id
                     left join team t on s.team_id = t.id
                     left join shop_cube scube on sh.id = scube.shop_id
                     left join (select count(shop_id) as count_terminal, shop_id from terminal group by shop_id) ter
                               on ter.shop_id = sh.id
            order by id desc;
            '''
        ),
    ]
