class ShopTakeCareStatus:
    NOT_CARE = 0
    CARE = 1
    CARE_OK = 2

    CHOICES = (
        (NOT_CARE, 'NOT TAKE CARE'),
        (CARE, 'TAKE CARE'),
        (CARE_OK, 'CARE_OK')
    )


class ShopActivateType:
    DISABLE = 0
    ACTIVATE = 1

    CHOICES = (
        (DISABLE, 'DISABLE'),
        (ACTIVATE, 'ACTIVATE'),
    )


class ShopLogType:
    CREATED = 0
    DELETED = 1
    CHANGE_STAFF = 2
    CHANGE_TAKE_CARE_STATUS = 3
    CHANGE_ACTIVATED = 4
    OTHER_UPDATE = 5

    CHOICES = (
        (CREATED, 'Created new'),
        (DELETED, 'Do not use because do not delete shop'),
        (CHANGE_STAFF, 'Change staff'),
        (CHANGE_TAKE_CARE_STATUS, 'Change take care status'),
        (CHANGE_ACTIVATED, 'Change activate type'),
        (OTHER_UPDATE, 'Other field updated'),
    )
