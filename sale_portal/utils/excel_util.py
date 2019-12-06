import os
import xlsxwriter
import logging
from django.conf import settings

array_header = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 'M1', 'N1', 'O1', 'P1', 'Q1',
                'R1', 'S1', 'T1', 'U1', 'V1', 'W1', 'X1', 'Y1', 'Z1', 'AA1', 'AB1', 'AC1', 'AD1', 'AE1', 'AF1', 'AG1',
                'AH1', 'AI1', 'AJ1', 'AK1', 'AL1', 'AM1', 'AN1']


def check_or_create_excel_folder():
    if not os.path.exists(settings.MEDIA_ROOT+'/excel'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT, 'excel'))


def check_or_create_excel_subfolder(folder_name=''):
    if not os.path.exists(settings.MEDIA_ROOT+'/excel/' + folder_name):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', folder_name))


def create_simple_excel_file(folder_name='', file_name='', sheet_name='', column_headers=[], data=[]):
    check_or_create_excel_folder()
    if not isinstance(folder_name, str) or not isinstance(file_name, str) or not isinstance(sheet_name, str):
        logging.error('Create excel file error: folder_name or file_name or sheet_name error')
        return ''
    if column_headers is None or data is None or not isinstance(column_headers, list) or not isinstance(data, list):
        logging.error('Create excel file error: column_headers or data not valid')
        return ''
    check_or_create_excel_subfolder(folder_name)

    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/' + folder_name + '/' + file_name)
    worksheet = workbook.add_worksheet(sheet_name.upper())

    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#74beff',
        'font_color': '#ffffff',
    })

    index = 0
    for column_header in column_headers:
        worksheet.write(array_header[index], column_header, merge_format)
        index += 1
    worksheet.freeze_panes(1, 0)

    row_num = 1
    for item in data:
        index = 0
        for value in item.values():
            worksheet.write(row_num, index, value)
            index += 1
        row_num += 1

    workbook.close()

    return settings.MEDIA_URL + '/excel/' + folder_name + '/' + file_name
