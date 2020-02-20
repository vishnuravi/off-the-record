function toggleMessageArea() {
    var messageArea = document.getElementById("messageArea");
    var messageAreaOverlay = document.getElementById("messageAreaOverlay");
    var hideButton = document.getElementById("hideButtonText");
    var sendButton = document.getElementById("sendButton");
    var clearButton = document.getElementById("clearButton");

    if (messageArea.style.display === "none") {
        messageArea.style.display = "block";
        messageAreaOverlay.style.display = "none";
        sendButton.disabled = false;
        clearButton.disabled = false;
    } else {
        messageArea.style.display = "none";
        messageAreaOverlay.style.display = "block";
        sendButton.disabled = true;
        clearButton.disabled = true;
    }

    if (hideButton.innerHTML == "Hide") {
        hideButton.innerHTML = "Show";
    } else {
        hideButton.innerHTML = "Hide";
    }
}

function clearMessageArea() {
    document.getElementById("messageArea").value = ' ';
}