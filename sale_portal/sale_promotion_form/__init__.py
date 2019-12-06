class PromotionStatus:
    UNIMPLEMENTED = 0
    ADDRESS_NOT_FOUND = 1
    STOP_BUSINESS_OR_RELOCATED = 2
    IMPLEMENTED = 3

    CHOICES = [
        (UNIMPLEMENTED, 'Chưa triển khai'),
        (ADDRESS_NOT_FOUND, 'Không tìm thấy địa chỉ'),
        (STOP_BUSINESS_OR_RELOCATED, 'Cửa hàng ngừng KD/Đã chuyển địa điểm'),
        (IMPLEMENTED, 'Đã triển khai')
    ]