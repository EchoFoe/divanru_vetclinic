(function() {
    "use strict";

    document.addEventListener('DOMContentLoaded', function() {
        var timeInputs = document.querySelectorAll('input[type="time"]');
        timeInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                var time = this.valueAsNumber;
                var minutes = new Date(time).getMinutes();
                if (minutes % 30 !== 0) {
                    this.value = '';
                }
            });
        });
    });
})();