(function () {
    function getToggleField() {
        return document.querySelector('[name$="-enable_pro_pack"]');
    }

    function togglePackSections(enable) {
        var sections = document.querySelectorAll('.pack-three-fields');
        sections.forEach(function (fieldset) {
            fieldset.style.display = enable ? '' : 'none';
        });
        var notices = document.querySelectorAll('.pack-three-disabled-hint');
        notices.forEach(function (notice) {
            notice.hidden = enable;
        });
    }

    function initPackControls() {
        var toggle = getToggleField();
        if (!toggle) {
            return;
        }
        var handler = function () {
            togglePackSections(Boolean(toggle.checked));
        };
        toggle.addEventListener('change', handler);
        handler();
    }

    document.addEventListener('DOMContentLoaded', initPackControls);
})();
