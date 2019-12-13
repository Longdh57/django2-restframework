class StaffLogType:
    CREATE_NEW = 0
    DELETED = 1
    UPDATED = 2

    CHOICES = [
        (CREATE_NEW, 'New row in qr_terminal table'),
        (DELETED, 'Deleted from qr_terminal table'),
        (UPDATED, 'Updated from qr_terminal table'),
    ]


class StaffStatus:
    ACTIVATE = 1
    DISABLE = -1

    CHOICES = [
        (ACTIVATE, 'Đang hoạt động'),
        (DISABLE, 'Đã hủy'),
    ]


class StaffTeamRoleType:
    TEAM_STAFF = 0
    TEAM_MANAGEMENT = 1

    CHOICES = [
        (TEAM_STAFF, 'TEAM_STAFF'),
        (TEAM_MANAGEMENT, 'TEAM_MANAGEMENT'),
    ]
