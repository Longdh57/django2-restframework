var InputsCheckboxesRadios = function () {
    var _componentSwitchery = function () {
        var elems = Array.prototype.slice.call(document.querySelectorAll('.form-check-input-switchery'));
        elems.forEach(function (html) {
            var switchery = new Switchery(html);
        });
    };

    return {
        initComponents: function () {
            _componentSwitchery();
        }
    }
}();

document.addEventListener('DOMContentLoaded', function () {
    InputsCheckboxesRadios.initComponents();
});
