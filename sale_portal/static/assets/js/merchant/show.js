$(function () {
    accessToken = localStorage.getItem("accessToken");

    $.ajax({
        url: url_api + '/api/merchant/' + window.MERCHANT_ID + '/detail/',
        headers: {'Authorization': 'JWT ' + accessToken},
        type: "GET",
        success: function (response) {
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
        },
        error: function (response) {
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
        }
    });

    var datatable = $('#datatables').DataTable({
        searching: false,
        serverSide: true,
        processing: true,
        paging: true,
        ajax: {
            url: url_api + "/api/terminal/datatables/?format=datatables",
            headers: {'Authorization': 'JWT ' + accessToken},
            data: function (d) {
                d.merchant_id = window.MERCHANT_ID;
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
            {data: "terminal_id"},
            {data: "terminal_name"},
            {data: "terminal_address", sortable: false},
            {
                data: "shop",
                sortable: false,
                render: function (data, type, row, meta) {
                    if (data != null) {
                        data = data.id;
                    } else {
                        data = ''
                    }
                    return data;
                }
            },
            {data: "created_date"},
            {data: "status", "sortable": false},
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
});

function goBack() {
    var parts = document.referrer.split('/');
    console.log(parts);
    if (parts.length > 1 && parts[parts.length-2] == 'merchant') {
        window.history.back();
    } else {
        window.location.href = '/merchant';
    }
}