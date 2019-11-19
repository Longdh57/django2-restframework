class StaffLogType:
    CREATE_NEW = 0
    DELETED = 1
    UPDATED = 2

    CHOICES = [
        (CREATE_NEW, 'New row in qr_terminal table'),
        (DELETED, 'Deleted from qr_terminal table'),
        (UPDATED, 'Updated from qr_terminal table'),
    ]