var SweetAlert = function () {
    var _componentSweetAlert = function () {
        // Defaults
        var setCustomDefaults = function () {
            swal.setDefaults({
                buttonsStyling: true,
                confirmButtonClass: 'btn btn-success',
                cancelButtonClass: 'btn btn-light'
            });
        }
        setCustomDefaults();

        if ($("#message_info").length) {
            $('#message_info').ready(function () {
                swal({
                    title: document.getElementById("message_info").textContent,
                    type: 'info',
                    showConfirmButton: false,
                    timer: 2000
                });
            });
        }

        if ($("#message_success").length) {
            $('#message_success').ready(function () {
                swal({
                    title: document.getElementById("message_success").textContent,
                    type: 'success',
                    showConfirmButton: false,
                    timer: 2000
                });
            });
        }

        if ($("#message_error").length) {
            $('#message_error').ready(function () {
                swal({
                    title: document.getElementById("message_error").textContent,
                    type: 'error',
                    showConfirmButton: false,
                    timer: 2000
                });
            });
        }

        if ($("#message_warning").length) {
            $('#message_warning').ready(function () {
                swal({
                    title: document.getElementById("message_warning").textContent,
                    type: 'warning',
                    showConfirmButton: false,
                    timer: 2000
                });
            });
        }


    };

    return {
        initComponents: function () {
            _componentSweetAlert();
        }
    }
}();

document.addEventListener('DOMContentLoaded', function () {
    SweetAlert.initComponents();
});
