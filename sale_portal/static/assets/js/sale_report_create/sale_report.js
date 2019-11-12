var latitude = 0;
var longitude = 0;
var current_draft_id = 0;

var isFirstSearchShop = true;
var isFirstSearchDraft = true;

function formatNumber(value) {
  if (value.length == 0) {
    return '';
  }
  if (value.length > 2) {
    value = value.substring(0, 2);
  }
  return value % 100;
}

function getLocation() {
  var domain = window.location.origin.split(".");
  var server = domain[domain.length - 1];
  if (server == 'local') {
    latitude = 21.0222089;
    longitude = 105.81729949999999;
    $("#location-success").show();
    $("#button-submit").show();
  } else {
    navigator.geolocation.getCurrentPosition(showPosition, errorCallback);
  }
}

function showPosition(position) {
  latitude = position.coords.latitude;
  longitude = position.coords.longitude;
  $("#location-success").show();
  $("#button-submit").show();
}

function errorCallback() {
  $(".location-error").show();
  $("#button-submit").hide();
}

function formatFormDataProperties(data) {
  for (var key of data.keys()) {
    if (typeof data.get(key) === "string") data.set(key, data.get(key).trim())
  }
}

function changeSelectNewResult(value) {
  if (value == 0) {
    $('#select_new_result').val('Đồng ý, đã ký được HĐ');
  }
  else if (value == 1) {
    $('#select_new_result').val('Đồng ý, chưa ký được HĐ');
  }
  else if (value == 2) {
    $('#select_new_result').val('Cần xem xét thêm');
  }
  else if (value == 3) {
    $('#select_new_result').val('Từ chối hợp tác');
  }

  $("div.select-new-result").each(function () {
    if ($(this).attr('value') == value) {
      $(this).find('i').css('opacity', 1);
    } else {
      $(this).find('i').css('opacity', 0);
    }
  });
}

function changeSelectPurpose(value) {
  if (value == 0) {
    $('#select_purpose').val('Mở mới');
  }
  else if (value == 1) {
    $('#select_purpose').val('Triển khai');
  }
  else if (value == 2) {
    $('#select_purpose').val('Chăm sóc');
  }

  $("div.select-purpose").each(function () {
    if ($(this).attr('value') == value) {
      $(this).find('i').css('opacity', 1);
    } else {
      $(this).find('i').css('opacity', 0);
    }
  });
}

function changeSelectShopStatus(value) {
  if (value == 0) {
    $('#select_shop_status').val('Đã nghỉ kinh doanh hoặc không có cửa hàng thực tế');
  }
  else if (value == 1) {
    $('#select_shop_status').val('Muốn thanh lý QR');
  }
  else if (value == 2) {
    $('#select_shop_status').val('Đang hoạt động');
  }
  else if (value == 3) {
    $('#select_shop_status').val('Không hợp tác');
  }
  else if (value == 4) {
    $('#select_shop_status').val('Đã chuyển địa điểm');
  }

  $("div.select-shop-status").each(function () {
    if ($(this).attr('value') == value) {
      $(this).find('i').css('opacity', 1);
    } else {
      $(this).find('i').css('opacity', 0);
    }
  });
}

function changeSelectVerifyShop(value) {
  if (value === "0") {
    $('#select_verify_shop').val('Tìm được cửa hàng đúng địa chỉ');
  }
  else if (value === "1") {
    $('#select_verify_shop').val('Tìm được cửa hàng sai địa chỉ/Đã chuyển địa điểm');
  }
  else if (value === "2") {
    $('#select_verify_shop').val('Không tìm được cửa hàng');
  }

  $("div.select-verify-shop").each(function () {
    if ($(this).attr('value') == value) {
      $(this).find('i').css('opacity', 1);
    } else {
      $(this).find('i').css('opacity', 0);
    }
  });
}

$.fn.setSelectionRange = function (start, end) {
  return this.each(function () {
    if (this.setSelectionRange) {
      this.focus();
      this.setSelectionRange(start, end);
    } else if (this.createTextRange) {
      var range = this.createTextRange();
      range.collapse(true);
      range.moveEnd('character', end);
      range.moveStart('character', start);
      range.select();
    }
  });
}

//============================================================================================================

$(function () {
  $('input[type=radio][name=purpose]').change(function () {
    if (current_draft_id === 0) {
      getLocation();
    } else {
      $("#location-success").show();
      $("#button-submit").show();
    }

    changeSelectPurpose(this.value);

    if (this.value == '0') {
      $('#open-new-content').show();
      $('#care-content').hide();
      $('#shop-info').hide();
      $('#verify_shop_wrapper').hide();
      $('#care-result-content').hide();
      $('#implement-content').hide();
      $('#list-images').hide();
      $('#cessation-of-business-content').hide();
    }
    else if (this.value == '1') {
      $('#open-new-content').hide();
      $('#care-content').hide();
      $('#shop-info').show();
      $('#verify_shop_wrapper').show();
      $('#implement-content').show();
      $('#care-result-content').hide();
      $('#list-images').show();
      $('#cessation-of-business-content').hide();
    }
    else if (this.value == '2') {
      $('#open-new-content').hide();
      $('#shop-info').show();
      $('#verify_shop_wrapper').hide();
      $('#care-content').show();
      $('#implement-content').hide();
      $('#care-result-content').hide();
      $('#list-images').hide();
    }

    $('#draft-list').hide();
  });

  $("div.select-purpose").each(function () {
    $(this).on('click', function () {
      $('#modal_purpose').modal('hide');
      $('input[name="purpose"][value="' + $(this).attr('value') + '"]').click();
    });
  });

  $('select[name=select_new_result]').on('change', function () {
    changeSelectNewResult(this.value);
  });

  $("div.select-new-result").each(function () {
    $(this).on('click', function () {
      $('#modal_new_result').modal('hide');
      $('select[name="select_new_result"]').val($(this).attr('value')).change();
    });
  });

  $("#modal_select_shop").on('shown.bs.modal', function () {
    if (isFirstSearchShop) {
      isFirstSearchShop = false;
      $('#search_shop').click();
    }
  });

  $('#search_shop').on('click', function () {
    $.ajax({
      url: url_root + '/api/shop/list_api/',
      type: "GET",
      headers: { 'Authorization': 'JWT ' + accessToken },
      data: {
        name: $('input[name=search_shop]').val()
      },
      success: function (response, txtStatus) {
        var content = '';
        if (response.data.length !== 0) {
          for (let d of response.data) {
            content += '<p id="result_shop_id-' + d.id + '" data-shop-id="' + d.id + '">' + d.name + '</p>'
          }
        } else {
          content = 'Không tìm thấy kết quả phù hợp!'
        }
        $('.search_shop_result').html(content);
        $('[id^="result_shop_id-"]').unbind();
        $('[id^="result_shop_id-"]').on('click', function () {
          $option = $("<option selected></option>").val($(this).data('shop-id')).text($(this).text());
          $('#shop_id').append($option).trigger('change');
          $('#modal_select_shop').modal('hide');
        });
      },
      error: function (response) {
        if (response.status == 403) {
          new PNotify({
            title: 'Lỗi',
            text: 'Bạn không có quyền thực hiện hành động này',
            addclass: 'bg-danger border-danger'
          });
        } else {
          swal({
            title: 'Lỗi',
            type: 'error',
            showConfirmButton: false,
            timer: 2000
          });
        }
      }
    });
  });

  //========================================================================================================
  //======================================  select draft==================================================================

  $("#modal_select_draft").on('shown.bs.modal', function () {
    if (isFirstSearchDraft) {
      isFirstSearchDraft = false;
      $('#search_draft').click();
    }
  });

  $('#search_draft').on('click', function () {
    $.ajax({
      url: url_root + '/api/sale-report-form/draft/list_api/',
      type: "GET",
      headers: { 'Authorization': 'JWT ' + accessToken },
      data: {
        name: $('input[name=search_draft]').val()
      },
      success: function (response, txtStatus) {
        var content = '';
        if (response.data.length !== 0) {
          for (let d of response.data) {
            content += '<p id="result_draft_id-' + d.id + '" data-draft-id="' + d.id + '">' + d.purpose + '</p>'
          }
        } else {
          content = 'Không tìm thấy kết quả phù hợp!'
        }
        $('.search_draft_result').html(content);
        $('[id^="result_draft_id-"]').unbind();
        $('[id^="result_draft_id-"]').on('click', function () {
          $option = $("<option selected></option>").val($(this).data('draft-id')).text($(this).text());
          $('#draft_id').append($option).trigger('change');
          $('#modal_select_draft').modal('hide');
        });
      },
      error: function (response) {
        if (response.status == 403) {
          new PNotify({
            title: 'Lỗi',
            text: 'Bạn không có quyền thực hiện hành động này',
            addclass: 'bg-danger border-danger'
          });
        } else {
          swal({
            title: 'Lỗi',
            type: 'error',
            showConfirmButton: false,
            timer: 2000
          });
        }
      }
    });
  });

  //========================================================================================================

  $('select[name=select_shop_status]').on('change', function () {
    if (this.value == '2') {
      $('#cessation-of-business-content').hide();
      $('#care-result-content').show();
      $('#list-images').show();
    } else {
      $('#cessation-of-business-content').show();
      if (this.value == '0') {
        $('#care_title').html('Nội dung chăm sóc - Cửa hàng nghỉ kinh doanh hoặc không có cửa hàng thực tế');
      }
      if (this.value == '1') {
        $('#care_title').html('Nội dung chăm sóc - Muốn thanh lý QR');
      }
      if (this.value == '3') {
        $('#care_title').html('Nội dung chăm sóc - Không hợp tác');
      }
      if (this.value == '4') {
        $('#care_title').html('Nội dung chăm sóc - Cửa hàng chuyển địa điểm ');
      }
      $('#care-result-content').hide();
      $('#list-images').hide();
    }
    changeSelectShopStatus(this.value);
  });

  $("div.select-shop-status").each(function () {
    $(this).on('click', function () {
      $('#modal_shop_status').modal('hide');
      $('select[name="select_shop_status"]').val($(this).attr('value')).change();
    });
  });

  //========================================================================================================

  // verify shop
  //==============================================================================================

  $('select[name=verify_shop]').on('change', function () {
    changeSelectVerifyShop(this.value);
  });

  $("div.select-verify-shop").each(function () {
    $(this).on('click', function () {
      $('#modal_verify_shop').modal('hide');
      $('select[name="verify_shop"]').val($(this).attr('value')).change();
    });
  });

  $('input[type=radio][name=shop_status]').change(function () {
    if (this.value == '2') {
      $('#cessation-of-business-content').hide();
      $('#care-result-content').show();
      $('#list-images').show();
    } else {
      $('#cessation-of-business-content').show();
      if (this.value == '0') {
        $('#care_title').html('Nội dung chăm sóc - Cửa hàng nghỉ kinh doanh hoặc không có cửa hàng thực tế');
      }
      if (this.value == '1') {
        $('#care_title').html('Nội dung chăm sóc - Muốn thanh lý QR');
      }
      if (this.value == '3') {
        $('#care_title').html('Nội dung chăm sóc - Không hợp tác');
      }
      if (this.value == '4') {
        $('#care_title').html('Nội dung chăm sóc - Cửa hàng chuyển địa điểm ');
      }
      $('#care-result-content').hide();
      $('#list-images').hide();
    }
  });

  //========================================================================================================

  accessToken = localStorage.getItem("accessToken");

  $('#shop_id').select2({
    ajax: {
      url: url_root + '/api/shop/list_api/',
      headers: { 'Authorization': 'JWT ' + accessToken },
      type: 'GET',
      dataType: 'json',
      delay: 600,
      data: function (params) {
        return {
          name: params.term
        };
      },
      processResults: function (data, params) {
        return {
          results: $.map(data.data, function (item) {
            return {
              text: item.name,
              id: item.id,
              data: item
            };
          })
        };
      }
    },
    placeholder: '--- Chọn Cửa hàng ---',
    allowClear: true
  });

  $('#shop_id').on('change', function () {
    $('#select_shop').val($(this).select2('data')[0]['text']);
    $('#select_shop').setSelectionRange(0, 0);
  });

  $('#draft_id').select2({
    ajax: {
      url: url_root + '/api/sale-report-form/draft/list_api/',
      headers: { 'Authorization': 'JWT ' + accessToken },
      type: 'GET',
      dataType: 'json',
      delay: 750,
      data: function (params) {
        return {
          name: params.term
        };
      },
      processResults: function (data, params) {
        return {
          results: $.map(data.data, function (item) {
            return {
              text: item.purpose,
              id: item.id,
              data: item
            };
          })
        };
      }
    },
    placeholder: '--- Chọn bản nháp ---',
    allowClear: true
  });

  $('#draft_id').on('change', function () {
    if ($('#draft_id').val() != '') {
      $.ajaxSetup({
        headers: { 'Authorization': 'JWT ' + accessToken },
      });

      var draft_id = $('#draft_id').val();

      $.get(url_root + '/api/sale-report-form/draft/' + draft_id + '/detail/', {}, function (response) {
        if (!response.status) {
          $("#history_ticket_show").append("<p>Do not have data to show !!!</p>");
        } else {
          var data = response.data;
          current_draft_id = data.id;
          latitude = data.latitude;
          longitude = data.longitude;
          $('input[name="purpose"][value="' + data.purpose + '"]').click();

          if (data.purpose == 0) {
            $("#new_merchant_name").val(data.new.new_merchant_name == null ? '' : data.new.new_merchant_name);
            $("#new_merchant_brand").val(data.new.new_merchant_brand == null ? '' : data.new.new_merchant_brand);
            $("#new_address").val(data.new.new_address == null ? '' : data.new.new_address);
            $("#new_note").val(data.new.new_note == null ? '' : data.new.new_note);
            $("#new_customer_name").val(data.new.new_customer_name == null ? '' : data.new.new_customer_name);
            $("#new_phone").val(data.new.new_phone == null ? '' : data.new.new_phone);
            if (data.new.new_result != null) {
              $('select[name="select_new_result"]').val(data.new.new_result).trigger('change');
            }
          } else {
            $option = $("<option selected></option>").val(data.shop.shop_id).text(data.shop.shop_id + ' - ' + data.shop.merchant_brand + ' - ' + data.shop.address);
            $('#shop_id').append($option).trigger('change');
          }
          if (data.purpose == 1) {

            if (data.implement_confirm != null) {
                $('select[name="verify_shop"]').val(data.implement_confirm).change();
                if (data.implement_confirm == 1 && data.implement_new_address != null) {
                    $("#new_address_input").val(data.implement_new_address);
                }
            }

            if (data.implement_posm != null && data.implement_posm != '') {
              var implement_posm = JSON.parse(data.implement_posm)[0];
              $("input[name=standeeQr]").val(implement_posm.standeeQr);
              $("input[name=stickerDoor]").val(implement_posm.stickerDoor);
              $("input[name=stickerTable]").val(implement_posm.stickerTable);
              $("input[name=guide]").val(implement_posm.guide);
              $("input[name=wobbler]").val(implement_posm.wobbler);
              $("input[name=poster]").val(implement_posm.poster);
              $("input[name=standeeCtkm]").val(implement_posm.standeeCtkm);
              $("input[name=tentcard]").val(implement_posm.tentcard);
            }

            if (data.implement_merchant_view != null && data.implement_merchant_view != "") {
              var merchant_views = data.implement_merchant_view.split(",");
              for (var i = 0; i < merchant_views.length; i++) {
                // $('input[name="implement_merchant_view"][value="2"]:checked').val() == merchant_views[i]
                $('input[name="implement_merchant_view"][value="' + merchant_views[i] + '"]').click();
              }
            }

            if (data.implement_career_guideline != null && data.implement_career_guideline != "") {
              var guidelines = data.implement_career_guideline.split(",");
              for (var i = 0; i < guidelines.length; i++) {
                $('input[name="implement_career_guideline"][value="' + guidelines[i] + '"]').click();
              }
            }
          }
          if (data.purpose == 2) {
            $('select[name="select_shop_status"]').val(data.shop_status).trigger('change');
            if (data.shop_status != 2) {
              $("#cessation_of_business_note").val(data.cessation_of_business_note)
            } else {
              if (data.customer_care_posm != null && data.customer_care_posm != '') {
                var care_posm = JSON.parse(data.customer_care_posm)[0];
                $("input[name=customer_care_standeeQr]").val(care_posm.customer_care_standeeQr);
                $("input[name=customer_care_stickerDoor]").val(care_posm.customer_care_stickerDoor);
                $("input[name=customer_care_stickerTable]").val(care_posm.customer_care_stickerTable);
                $("input[name=customer_care_guide]").val(care_posm.customer_care_guide);
                $("input[name=customer_care_wobbler]").val(care_posm.customer_care_wobbler);
                $("input[name=customer_care_poster]").val(care_posm.customer_care_poster);
                $("input[name=customer_care_standeeCtkm]").val(care_posm.customer_care_standeeCtkm);
                $("input[name=customer_care_tentcard]").val(care_posm.customer_care_tentcard);
                $("input[name=customer_care_line]").val(care_posm.customer_care_line);
              }
              $('input[name="customer_care_cashier_reward"][value="' + data.customer_care_cashier_reward + '"]').click();
              $("#customer_care_transaction").val(data.customer_care_transaction);
            }
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
    }
  });

  $('#verify_shop').on('change', function () {
    if (this.value == 1) {
      $('#add_address_input').css('display', 'flex');
    } else {
      $('#add_address_input').css('display', 'none');
    }
  })

  //========================================================================================================

  $("#save-draft").click(function () {
    if (!$('#sale_report_form')[0].checkValidity()) {
      $('#sale_report_form').find(':submit').click();
    } else {
      submitData(true);
    }
  });

  $("#sale_report_form").submit(function (e) {
    e.preventDefault();

    submitData(false);
  });

  var hash = window.location.hash.replace('#', '');
  if (hash != null && hash.length > 0) {
    window.history.replaceState("data", "Sale Report", window.location.href.split('#')[0]);
    var data = hash.split('&');

    if (data.length == 4) {
      $('input[name="purpose"][value="' + data[0] + '"]').click();
      $option = $("<option selected></option>").val(data[1]).text(data[1] + ' - ' + data[2] + ' - ' + decodeURIComponent(data[3]));
      $('#shop_id').append($option).trigger('change');
    }
  }
});

function submitData(is_draft) {
  $("#button-submit").hide();
  $('#loading').show();

  var form_data = new FormData();

  var implement_merchant_view = [];
  $.each($("input[name='implement_merchant_view']:checked"), function () {
    implement_merchant_view.push($(this).val());
  });

  var implement_career_guideline = [];
  $.each($("input[name='implement_career_guideline']:checked"), function () {
    implement_career_guideline.push($(this).val());
  });

  form_data.append("latitude", latitude);
  form_data.append("longitude", longitude);
  form_data.append("purpose", $("input[name='purpose']:checked").val());

  form_data.append("new_merchant_name", $("#new_merchant_name").val());
  form_data.append("new_merchant_brand", $("#new_merchant_brand").val());
  form_data.append("new_address", $("#new_address").val());
  form_data.append("new_note", $("#new_note").val());
  form_data.append("new_customer_name", $("#new_customer_name").val());
  form_data.append("new_phone", $("#new_phone").val());
  form_data.append("new_result", $("select[name='select_new_result']").val());

  form_data.append("shop_id", $("#shop_id").val());
  form_data.append("shop_status", $("select[name='select_shop_status']").val());
  form_data.append("verify_shop", $("#verify_shop option:selected").val());
  form_data.append("new_address_input", $("#new_address_input").val());

  if (document.getElementById("image-outside-upload").src != '' && !is_draft) {
    var outside = dataURItoBlob(document.getElementById("image-outside-upload").src);
  }
  if (document.getElementById("image-inside-upload").src != '' && !is_draft) {
    var inside = dataURItoBlob(document.getElementById("image-inside-upload").src);
  }
  if (document.getElementById("image-store-cashier-upload").src != '' && !is_draft) {
    var store_cashier = dataURItoBlob(document.getElementById("image-store-cashier-upload").src);
  }

  form_data.append("image_outside", outside);
  form_data.append("image_inside", inside);
  form_data.append("image_store_cashier", store_cashier);

  form_data.append("cessation_of_business_note", $("#cessation_of_business_note").val());

  if (document.getElementById("cessation-of-business-image-upload").src != '' && !is_draft) {
    var cessation_of_business_image = dataURItoBlob(document.getElementById("cessation-of-business-image-upload").src);
  }
  form_data.append("cessation_of_business_image", cessation_of_business_image);

  var customerCareArr = [];
  customerCareArr.push({
    'customer_care_standeeQr': $("input[name=customer_care_standeeQr]").val(),
    'customer_care_stickerDoor': $("input[name=customer_care_stickerDoor]").val(),
    'customer_care_stickerTable': $("input[name=customer_care_stickerTable]").val(),
    'customer_care_guide': $("input[name=customer_care_guide]").val(),
    'customer_care_wobbler': $("input[name=customer_care_wobbler]").val(),
    'customer_care_poster': $("input[name=customer_care_poster]").val(),
    'customer_care_standeeCtkm': $("input[name=customer_care_standeeCtkm]").val(),
    'customer_care_tentcard': $("input[name=customer_care_tentcard]").val(),
    'customer_care_line': $("input[name=customer_care_line]").val(),
  });
  form_data.append("customer_care_posm", JSON.stringify(customerCareArr));
  form_data.append("customer_care_cashier_reward", $("input[name='customer_care_cashier_reward']:checked").val());
  form_data.append("customer_care_transaction", $("#customer_care_transaction").val());

  var implementArr = [];
  implementArr.push({
    'standeeQr': $("input[name=standeeQr]").val(),
    'stickerDoor': $("input[name=stickerDoor]").val(),
    'stickerTable': $("input[name=stickerTable]").val(),
    'guide': $("input[name=guide]").val(),
    'wobbler': $("input[name=wobbler]").val(),
    'poster': $("input[name=poster]").val(),
    'standeeCtkm': $("input[name=standeeCtkm]").val(),
    'tentcard': $("input[name=tentcard]").val(),
  });
  form_data.append("implement_posm", JSON.stringify(implementArr));
  form_data.append("implement_merchant_view", implement_merchant_view);
  form_data.append("implement_career_guideline", implement_career_guideline);
  form_data.append("is_draft", is_draft);
  if (current_draft_id > 0) {
    form_data.append("current_draft_id", current_draft_id);
  }

  formatFormDataProperties(form_data);

  // validate
  $(".validation-invalid-label").text("");
  var isValidated = true;
  var validateMessage = "Lỗi";
  switch (form_data.get("purpose")) {
    case "0":
      try {
        check_new_merchant_name = form_data.get("new_merchant_name").trim().length > 0 && form_data.get("new_merchant_name").trim().length < 100;
        if (!check_new_merchant_name) {
          $("#check_new_merchant_name").text(validateMessage = "Tên mới của merchant không hợp lệ");
          isValidated = false;
        }
        check_new_merchant_brand = form_data.get("new_merchant_name").trim().length < 100;
        if (!check_new_merchant_brand) {
          $("#check_new_merchant_brand").text(validateMessage = "Tên merchant brand mới không hợp lệ, có thể để trống trường này");
          isValidated = false;
        }
        check_new_customer_name = form_data.get("new_customer_name").trim().length == 0 || /^[a-zA-Z AaĂăÂâĐđEeÊêIiOoÔôƠơUuƯưYyÁáẮắẤấÉéẾếÍíÓóỐốỚớÚúỨứÝýÀàẰằẦầÈèỀềÌìÒòỒồỜờÙùỪừỲỳẢảẲẳẨẩẺẻỂểỈỉỎỏỔổỞởỦủỬửỶỷÃãẴẵẪẫẼẽỄễĨĩÕõỖỗỠỡŨũỮữỸỹẠạẶặẬậẸẹỆệỊịỌọỘộỢợỤụỰựỴỵ]{1,50}$/.test(form_data.get("new_customer_name"));
        if (!check_new_customer_name) {
          $("#check_new_customer_name").text(validateMessage = "Tên người liên hệ mới không hợp lệ, có thể để trống trường này");
          isValidated = false;
        }
        check_new_phone = form_data.get("new_phone").trim().length == 0 || /^[+0][0-9]{9,12}$/.test(form_data.get("new_phone"));
        if (!check_new_phone) {
          $("#check_new_phone").text(validateMessage = "Sđt mới không hợp lệ, có thể để trống trường này");
          isValidated = false;
        }
        check_new_address = form_data.get("new_address").trim().length < 150;
        if (!check_new_address) {
          $("#check_new_address").text(validateMessage = "Địa chỉ mới không hợp lệ, có thể để trống trường này");
          isValidated = false;
        }
        if (form_data.get("new_result") === "undefined" || form_data.get("new_result") === "") {
          $("#check_result").text(validateMessage = "Chưa chọn kết quả");
          isValidated = false;
        }
        break;
      } catch (err) {
        validateMessage = "Có lỗi xảy ra khi tạo form mở mới :" + err;
        isValidated = false;
        break;
      }
    case "1":
      try {
        if (form_data.get("shop_id") === "undefined" || form_data.get("shop_id") === "") {
          $("#check_shop_id").text(validateMessage = "Chưa chọn cửa hàng");
          isValidated = false;
        }
        if (form_data.get("verify_shop") === "undefined" || form_data.get("verify_shop") === "") {
          $("#check_verify_shop").text(validateMessage = "Chưa chọn xác thực shop");
          isValidated = false;
        }
        if (form_data.get("verify_shop") === "1" && (form_data.get("new_address_input") === "undefined" || form_data.get("new_address_input") === "")) {
          $("#check_new_address_input").text(validateMessage = "Chưa nhập địa chỉ mới");
          isValidated = false;
        }
        if (form_data.get("implement_merchant_view") === "undefined" || form_data.get("implement_merchant_view") === "") {
          $("#check_implement_merchant_view").text(validateMessage = "Chưa chọn merchant view");
          isValidated = false;
        }
        if ((form_data.get("image_outside") === "undefined" || form_data.get("image_outside") === "") && !is_draft) {
          $("#check_image_outside").text(validateMessage = "Chưa có ảnh nghiệm thu (ngoài cửa hàng)");
          isValidated = false;
        }
        if ((form_data.get("image_inside") === "undefined" || form_data.get("image_inside") === "") && !is_draft) {
          $("#check_image_inside").text(validateMessage = "Chưa có ảnh nghiệm thu (trong cửa hàng)");
          isValidated = false;
        }
        if ((form_data.get("image_store_cashier") === "undefined" || form_data.get("image_store_cashier") === "") && !is_draft) {
          $("#check_image_store_cashier").text(validateMessage = "Chưa có ảnh nghiệm thu (quầy thu ngân)");
          isValidated = false;
        }
        break;
      } catch (err) {
        validateMessage = "Có lỗi xảy ra khi tạo form triển khai :" + err;
        isValidated = false;
        break;
      }
    case "2":
      try {
        if (form_data.get("shop_id") === "undefined" || form_data.get("shop_id") === "") {
          $("#check_shop_id").text(validateMessage = "Chưa chọn cửa hàng");
          isValidated = false;
        }
        if (form_data.get("shop_status") === "undefined" || form_data.get("shop_status") === "") {
          $("#check_shop_status").text(validateMessage = "Chưa chọn tình trạng cửa hàng");
          isValidated = false;
        }
        if (form_data.get("shop_status") != "2") {
          if ((form_data.get("cessation_of_business_image") === "undefined" || form_data.get("cessation_of_business_image") === "") && !is_draft) {
            $("#check_cessation_of_business_image").text(validateMessage = "Chưa có ảnh nghiệm thu");
            isValidated = false;
          }
          if (form_data.get("cessation_of_business_note") === "undefined" || form_data.get("cessation_of_business_note") === "") {
            $("#check_cessation_of_business_note").text(validateMessage = "Chưa nhập nội dung mô tả");
            isValidated = false;
          }
          break;
        }
        if (form_data.get("shop_status") === "2") {
          if (form_data.get("customer_care_cashier_reward") === "undefined" || form_data.get("customer_care_cashier_reward") === "") {
            $("#check_customer_care_cashier_reward").text(validateMessage = "Chưa chọn ký HĐ thưởng thu ngân");
            isValidated = false;
          }
          check_customer_care_transaction = /^[0-9]{1,25}$/.test(form_data.get("customer_care_transaction"));
          if (!check_customer_care_transaction) {
            $("#check_customer_care_transaction").text(validateMessage = "Số giao dịch không hợp lệ");
            isValidated = false;
          }
          if ((form_data.get("image_outside") === "undefined" || form_data.get("image_outside") === "") & !is_draft) {
            $("#check_image_outside").text(validateMessage = "Chưa có ảnh nghiệm thu (ngoài cửa hàng)");
            isValidated = false;
          }
          if ((form_data.get("image_inside") === "undefined" || form_data.get("image_inside") === "") & !is_draft) {
            $("#check_image_inside").text(validateMessage = "Chưa có ảnh nghiệm thu (trong cửa hàng)");
            isValidated = false;
          }
          if ((form_data.get("image_store_cashier") === "undefined" || form_data.get("image_store_cashier") === "") & !is_draft) {
            $("#check_image_store_cashier").text(validateMessage = "Chưa có ảnh nghiệm thu (quầy thu ngân)");
            isValidated = false;
          }
          break;
        }
      } catch (err) {
        validateMessage = "Có lỗi xảy ra khi tạo form chăm sóc :" + err;
        isValidated = false;
        break;
      }
  }
  if (!isValidated) {
    $("#button-submit").show();
    $('#loading').hide();
    console.log(validateMessage)
  } else {
    if (is_draft) {
      var r = confirm("Chú ý: Lưu bản nháp sẽ không kèm theo ảnh!");
      if (r == false) {
        $('#loading').hide();
        $("#button-submit").show();
        return;
      }
    }

    $("#button-submit").hide();
    $('#loading').show();
    $.ajax({
      url: url_root + '/api/sale-report-form/create/',
      processData: false,
      contentType: false,
      data: form_data,
      headers: { 'Authorization': 'JWT ' + accessToken },
      type: "POST",
      success: function (response) {
        window.location.replace('/sale-report-form/success');
      },
      error: function (xhr, status, error) {
        $("#button-submit").show();
        $('#loading').hide();
        var err = eval("(" + xhr.responseText + ")");
        swal({
          title: err.Message,
          type: 'error',
          showConfirmButton: false,
          timer: 2000
        });
      }
    })
  }
}