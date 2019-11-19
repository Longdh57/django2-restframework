class SaleReportFormPurposeTypes:
    OPEN_NEW = 0
    IMPLEMENT = 1
    CARE = 2

    CHOICES = (
        (OPEN_NEW, 'Mở mới'),
        (IMPLEMENT, 'Triển khai'),
        (CARE, 'Chăm sóc'),
    )


class SaleReportFormCreateNewResults:
    CONTRACT_OK = 0
    CONTRACT_NOT_OK = 1
    CONSIDER_FURTHER = 2
    REJECT = 3

    CHOICES = (
        (CONTRACT_OK, 'Dong y, da ky duoc HD'),
        (CONTRACT_NOT_OK, 'Dong y, chua ky duoc HD'),
        (CONSIDER_FURTHER, 'Can xem xet them'),
        (REJECT, 'Tu choi hop tac'),
    )


class SaleReportFormShopStatus:
    CLOSED = 0
    LIQUIDATION_QR = 1
    ACTIVE = 2
    UNCOOPERATIVE = 3
    CHANGED_LOCATION = 4

    CHOICES = (
        (CLOSED, 'Da nghi kinh doanh/ khong co cua hang thuc te'),
        (LIQUIDATION_QR, 'Muon thanh ly QR'),
        (ACTIVE, 'Dang hoat dong'),
        (UNCOOPERATIVE, 'Không hợp tác'),
        (CHANGED_LOCATION, 'Da chuyen dia diem'),
    )


class SaleReportFormShopConfirm:
    CORRECT_ADDRESS = 0
    INCORRECT_ADDRESS = 1
    NOT_FOUND = 2

    CHOICES = (
        (CORRECT_ADDRESS, 'Cua hang dung dia chi'),
        (INCORRECT_ADDRESS, 'Cua hang sai dia chi/ da chuyen dia diem'),
        (NOT_FOUND, 'Khong tim duoc cua hang'),
    )


class SaleReportFormCashierReward:
    NO = 0
    YES = 1

    CHOICES = (
        (NO, 'Không'),
        (YES, 'Có'),
    )
