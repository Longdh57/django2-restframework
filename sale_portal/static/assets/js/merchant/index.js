var superuser = localStorage.getItem("is_superuser");
var permissions = JSON.parse(localStorage.getItem("permissions"));

function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

$(function () {
    accessToken = localStorage.getItem("accessToken");
    var datatable = $('#datatables').DataTable({
        searching: false,
        serverSide: true,
        processing: true,
        paging: true,
        ajax: {
            url: url_api + "/api/merchant/datatables/?format=datatables",
            headers: {'Authorization': 'JWT ' + accessToken},
            data: function (d) {
                d.merchant_code = $('input[name=merchant_code]').val();
                d.staff_id = $('select[name=staff_id]').val();
                d.status = $('select[name=status]').val();
                d.from_date = $('input[name=from_date]').val();
                d.to_date = $('input[name=to_date]').val();
            },
            error: function (xhr, e) {
                if (xhr.status == 403) {
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
            }
        },
        columns: [
            {data: "merchant_code"},
            {data: "merchant_brand"},
            {data: "merchant_name", "sortable": false},
            {data: "staff", "sortable": false},
            {data: "created_date"},
            {data: "count_ter", className: 'text-right', sortable: false},
            {
                data: "merchant_cube",
                className: 'text-right',
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = formatNumber(data.number_of_new_customer);
                    } else {
                        data = 0
                    }
                    return data;
                }
            },
            {
                data: "merchant_cube",
                className: 'text-right',
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = formatNumber(data.number_of_tran);
                    } else {
                        data = 0
                    }
                    return data;
                }
            },
            {
                data: "merchant_cube",
                className: 'text-right',
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = formatNumber(data.value_of_tran);
                    } else {
                        data = 0
                    }
                    return data;
                }
            },
            {
                data: "merchant_cube",
                className: 'text-right',
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = formatNumber(data.number_of_tran_7d);
                    } else {
                        data = 0
                    }
                    return data;
                }
            },
            {
                data: "merchant_cube",
                className: 'text-right',
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = formatNumber(data.number_of_tran_30d);
                    } else {
                        data = 0
                    }
                    return data;
                }
            },
            {data: "status", "sortable": false},
            {
                data: "id",
                sortable: false,
                render: function (data, type, row, meta) {
                    var display = '';
                    if (data != null) {
                        display = '<div class="list-icons">' +
                                '<a href="/merchant/' + data + '/detail" class="list-icons-item">' +
                                '<i class="text-dark icon-info22"></i>' +
                                '</a></div>';
                    }
                    return display;
                }
            }
          ],
        order: [[4, "desc"]],
        autoWidth: false,
        dom: '<"datatable-header"fl><"datatable-scroll"t><"datatable-footer"ip>',
        language: {
            info: '<span>Hiển thị từ</span> _START_ <span>tới</span> _END_ <span>của</span> _TOTAL_ <span>bản ghi</span>',
            infoEmpty: '<span>Hiển thị từ 0 tới 0 của 0 bản ghi</span>',
            lengthMenu: '<span>Hiển thị:</span> _MENU_ <span> bản ghi</span>',
            paginate: {
                'first': 'First',
                'last': 'Last',
                'next': $('html').attr('dir') == 'rtl' ? 'Trước' : 'Sau',
                'previous': $('html').attr('dir') == 'rtl' ? 'Sau' : 'Trước'
            }
          }
    });

    $('#search-form').on('submit', function (e) {
        var from_date = $('input[name=from_date]').val();
        var to_date = $('input[name=to_date]').val();
        if (Date.parse(from_date) > Date.parse(to_date)) {
            alert("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!");
            return false;
        }
        datatable.draw();
        e.preventDefault();
    });

    $('.datatable-basic').DataTable();

    // ===============================================================================================

    $('#staff_id').select2({
        ajax: {
            url: url_api + '/api/staff/list-staffs/',
            headers: {'Authorization': 'JWT ' + accessToken},
            type: 'GET',
            dataType: 'json',
            data: function (params) {
                return {
                    email: params.term
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
});