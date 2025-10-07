(function () {
    "use strict";

    let intervalIds = [];
    let originalMessage = '';

    function stopAllTimers() {
        intervalIds.forEach(clearInterval);
        intervalIds = [];
    }

    function updateTimers() {
        let stopExecution = false;

        document.querySelectorAll('.o-mail-Message-body p').forEach(function (element) {

            if (element.textContent.includes("Rest ended")) {
                stopExecution = true;
                stopAllTimers(); 

                if (originalMessage) {
                    document.querySelectorAll('.o-mail-Message-body p').forEach(function (internal_elements) {
                        if (internal_elements.textContent.includes("Rest in progress")) {
                            internal_elements.textContent = originalMessage;
                        }
                    });
                }
                return;
            }

            var match = element.textContent.match(/Rest started: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);

            if (match) {
                var startTime = new Date(match[1]);

                if (!originalMessage) {
                    originalMessage = element.textContent;
                }

                startTime.setHours(startTime.getHours() - 3);

                function update() {
                    if (stopExecution) {
                        return;
                    }

                    var currentTime = new Date();
                    var diff = currentTime - startTime;

                    if (diff < 0) {
                        element.textContent = originalMessage;
                        return;
                    }

                    var seconds = Math.floor((diff / 1000) % 60);
                    var minutes = Math.floor((diff / (1000 * 60)) % 60);
                    var hours = Math.floor((diff / (1000 * 60 * 60)) % 24);

                    element.textContent = `⏳ Rest in progress: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }

                update();
                let intervalId = setInterval(update, 1000);
                intervalIds.push(intervalId);
            }
        });

        if (!stopExecution) {
            setTimeout(updateTimers, 1000);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        updateTimers();
    });

})();