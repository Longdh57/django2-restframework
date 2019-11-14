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
            {data: "count_shop", sortable: false},
            {
                data: "merchant_cube",
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
                    if (data != null) {
                        display = '<div class="list-icons">' +
                                '<a data-merchant_id="' + data + '" id="merchant-detail-' + data + '" class="list-icons-item">' +
                                '<i class="text-dark icon-info22"></i>' +
                                '</a>';
                        if (superuser || permissions.includes("merchant_edit")) {
                            display = display + '<a data-merchant_id="' + data + '" id="merchant-edit-' + data + '" class="list-icons-item">' +
                                    '<i class="text-primary icon-pencil5"></i>' +
                                    '</a>';
                        }
                        display = display + '</div>'
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

      $('#pic_id').select2({
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
          placeholder: '--- Chọn NV Quản Lý ---',
          allowClear: true
      });

      datatable.on('click', '[id^="merchant-detail-"]', function (e) {
          $.ajaxSetup({
              headers: {'Authorization': 'JWT ' + accessToken},
          });

          var merchant_id = $(this).data('merchant_id');

          $('#merchant_detail').modal("show");

          $.get(url_api + '/api/merchant/' + merchant_id + '/detail/', {}, function (response) {
              if (!response.status) {
                  $("#history_ticket_show").append("<p>Do not have data to show !!!</p>");
              } else {
                  $("#merchant_code").html(response.data.merchant_code);
                  $("#merchant_name").html(response.data.merchant_name);
                  $("#address").html(response.data.address);
                  $("#department").html(response.data.department.name);
                  $("#staff").html(response.data.staff.full_name);
                  if (response.data.status == 1) {
                      $("#status").html('<span class="badge badge-success">Hoạt động</span>');
                  } else if (response.data.status == -1) {
                      $("#status").html('<span class="badge badge-danger">Không hoạt động</span>');
                  } else {
                      $("#status").html('<span class="badge badge-dark">Khác</span>');
                  }
                  if (response.data.type == 0) {
                      $("#type").html('<span class="badge badge-flat border-info text-info">Cố định</span>');
                  } else {
                      $("#type").html('<span class="badge badge-flat border-warning text-warning">Di chuyển</span>');
                  }
                  $("#created_date").html(response.data.created_date);
                  if (response.data.synchronized_status) {
                      $("#synchronized_status").html('<i class="text-success icon-checkmark">');
                  } else {
                      $("#synchronized_status").html('<i class="text-warning icon-reload-alt">');
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

      $('#button-update').on('click', function (e) {
          $.ajaxSetup({
              headers: {'Authorization': 'JWT ' + accessToken},
          });

          var merchant_id = $("#edit_merchant_id").val();

          $.post(url_api + '/api/merchant/' + merchant_id + '/edit/', {
              'type': $("#edit_type").val(),
              'pic_id': $("#pic_id").val()
          }, function (response) {
              if (response) {
                  $('#merchant_edit').modal("hide");
                  datatable.draw();
                  e.preventDefault();
              } else {
                  $("#history_ticket_show").append("<p>Do not have data to show !!!</p>");
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

      // ============================== Permission ============================================

      if (superuser) {
          $("#merchant-import").show();
          $("#button-search-advanced").show();
      }

});