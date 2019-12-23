import re

vn_char = 'AaĂăÂâĐđEeÊêIiOoÔôƠơUuƯưYyÁáẮắẤấÉéẾếÍíÓóỐốỚớÚúỨứÝýÀàẰằẦầÈèỀềÌìÒòỒồỜờÙùỪừỲỳẢảẲẳẨẩẺẻỂểỈỉỎỏỔổỞởỦủỬửỶỷÃãẴẵẪẫẼẽỄễĨĩÕõỖỗỠỡŨũỮữỸỹẠạẶặẬậẸẹỆệỊịỌọỘộỢợỤụỰựỴỵ'


def validate_string_field(name, input, allow_none=False, allow_blank=False, rase_exception=False):
    if input is None:
        if allow_none:
            return True
        else:
            if rase_exception:
                raise Exception(str(name) + ' is None')
            else:
                return False

    if input == '':
        if allow_blank:
            return True
        else:
            if rase_exception:
                raise Exception(str(name) + ' is blank')
            else:
                return False
    return 'continue'


def validate_in_string_list(list, name, input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field(name, input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if input in list:
        return True
    else:
        if rase_exception:
            raise Exception(name + ' is not correct.')
        else:
            return False


def validate_merchant_brand(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('merchant_brand', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if re.match(r"^[a-zA-Z0-9_ " + vn_char + "]{1,50}$", input):
        return True
    else:
        if rase_exception:
            raise Exception('Merchant brand has some invalid character or over length.')
        else:
            return False


def validate_merchant_name(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('merchant_name', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if len(input) < 150:
        return True
    else:
        if rase_exception:
            raise Exception('Merchant name is over length.')
        else:
            return False


def validate_address(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('address', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if len(input) < 300:
        return True
    else:
        if rase_exception:
            raise Exception('Address is is over length.')
        else:
            return False


def validate_customer_name(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('customer_name', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if re.match(r"^[a-zA-Z " + vn_char + "]{1,150}$", input):
        return True
    else:
        if rase_exception:
            raise Exception('Customer name is over length or has invalid character.')
        else:
            return False


def validate_phone(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('phone', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if re.match(r"^[+0-9]{9,13}$", input):
        return True
    else:
        if rase_exception:
            raise Exception('Phone is invalid.')
        else:
            return False


def validate_note(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('Note', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate

    if len(input) < 500:
        return True
    else:
        if rase_exception:
            raise Exception('Note is over length.')
        else:
            return False


def validate_transaction(input, allow_none=False, allow_blank=False, rase_exception=False):
    string_common_validate = validate_string_field('Transaction', input, allow_none, allow_blank, rase_exception)
    if not str(string_common_validate) == 'continue':
        return string_common_validate
    if input.isdigit():
        return True
    else:
        if rase_exception:
            raise Exception('Transaction is invalid.')
        else:
            return False


def validate_posm_field(name, input):
    if input is not None and not str(input).isdigit():
        raise Exception('{} is required and typeOf {} must equal Interger'.format(name, name))
    return True
