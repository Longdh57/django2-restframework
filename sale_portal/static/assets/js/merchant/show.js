var superuser = localStorage.getItem("is_superuser");
var permissions = JSON.parse(localStorage.getItem("permissions"));

function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

$(function () {
    accessToken = localStorage.getItem("accessToken");

    $('#staff_id').select2({
        ajax: {
            url: url_api + '/api/staff/list_api/',
            headers: {'Authorization': 'JWT ' + accessToken},
            type: 'GET',
            dataType: 'json',
            data: function (params) {
                return {
                    email: params.term,
                    status: 1
                };
            },
            processResults: function (data, params) {
                return {
                    results: $.map(data.data, function (item) {
                        return {
                            text: item.email,
                            id: item.id,
                            data: item
                        };
                    })
                };
            }
        },
        placeholder: '--- Chọn NV Sale ---',
        allowClear: true
    });

    datatable.on('click', '[id^="merchant-detail-"]', function (e) {
        $.ajaxSetup({
            headers: {'Authorization': 'JWT ' + accessToken},
        });

        var merchant_id = $(this).data('merchant_id');

        $('#merchant_detail').modal("show");

        $.get(url_api + '/api/merchant/' + merchant_id + '/detail/', {}, function (response) {
             $("#merchant_code").text(response.data.merchant_code);
             $("#merchant_brand").text(response.data.merchant_brand);
             $("#merchant_name").text(response.data.merchant_name);
             $("#merchant_address").text(response.data.address);
             $("#merchant_type").text(response.data.type);
             $("#merchant_staff").text(response.data.staff.email);
             $("#merchant_created_date").text(response.data.created_date);
             $("#merchant_status").html(response.data.status);
             $("#number_of_new_customer").html(response.data.merchant_cube.number_of_new_customer);
             $("#number_of_tran").html(response.data.merchant_cube.number_of_tran);
             $("#value_of_tran").html(response.data.merchant_cube.value_of_tran);
             $("#number_of_tran_7d").html(response.data.merchant_cube.number_of_tran_7d);
             $("#number_of_tran_30d").html(response.data.merchant_cube.number_of_tran_30d);

        }).fail(function (response) {
            if (response.status == 403) {
                new PNotify({
                    title: 'Lỗi',
                    text: 'Bạn không có quyền thực hiện hành động này',
                    addclass: 'bg-danger border-danger'
                });
            } else {
                new PNotify({
                    title: 'Truy cập bị lỗi',
                    text: 'Lỗi kết nối, vui lòng liên hệ admin',
                    addclass: 'bg-warning border-warning'
                });
            }
        });
    });

    datatable.on('click', '[id^="merchant-edit-"]', function (e) {
        $.ajaxSetup({
            headers: {'Authorization': 'JWT ' + accessToken},
        });

        var merchant_id = $(this).data('merchant_id');

        $('#merchant_edit').modal("show");

        $('#merchant_edit').on('shown.bs.modal', function () {
            $(document).off('focusin.modal');
        });

        $.get(url_api + '/api/merchant/' + merchant_id + '/detail/', {}, function (response) {
            if (!response.status) {
                $("#history_ticket_show").append("<p>Do not have data to show !!!</p>");
            } else {
                $("#edit_merchant_id").val(response.data.merchant_id);
                $("#edit_merchant_code").val(response.data.merchant_code);
                $("#edit_merchant_name").val(response.data.merchant_name);
                $("#edit_type").val(response.data.type);

                if (response.data.pic.id != '') {
                    $option = $("<option selected></option>").val(response.data.pic.id).text(response.data.pic.full_name + ' - ' + response.data.pic.email);
                    $('#pic_id').append($option).trigger('change');
                } else {
                    $option = $("<option selected></option>").val('').text('');
                    $('#pic_id').append($option).trigger('change');
                }
            }
        }).fail(function (response) {
            if (response.status == 403) {
                new PNotify({
                    title: 'Lỗi',
                    text: 'Bạn không có quyền thực hiện hành động này',
                    addclass: 'bg-danger border-danger'
                });
            } else {
                new PNotify({
                    title: 'Truy cập bị lỗi',
                    text: 'Lỗi kết nối, vui lòng liên hệ admin',
                    addclass: 'bg-warning border-warning'
                });
            }
        });
    });

});