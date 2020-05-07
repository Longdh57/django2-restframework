class Pos365ContractDuration:
    SIX_MONTH = 0
    ONE_YEAR = 1
    TWO_YEAR = 2
    LIFETIME = 3

    CHOICES = [
        (SIX_MONTH, '6 tháng'),
        (ONE_YEAR, '1 năm'),
        (TWO_YEAR, '2 năm'),
        (LIFETIME, 'Trọn đời'),
    ]


class Pos365ContractProduct:
    POS365 = 0
    T1 = 1
    V1S = 2
    DEVICE = 3

    CHOICES = [
        (POS365, 'Phần mềm POS365'),
        (T1, 'Phần cứng: Máy T2'),
        (V1S, 'Phần cứng: Máy V1s'),
        (DEVICE, 'Phần cứng: Thiết bị'),
    ]