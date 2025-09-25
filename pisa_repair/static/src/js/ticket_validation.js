(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        document.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                let inputField = document.querySelector('.serial_number_wrapper input');
                let validateButton = document.querySelector('button[name="proceed_action"]');                

                if (inputField && validateButton && inputField === document.activeElement && inputField.value) {
                    validateButton.click();
                };
            }
        });
    });

})();