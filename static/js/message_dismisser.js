setTimeout(function () {
    let messages = document.getElementById('msg');
    if (messages) {
        let alert = new bootstrap.Alert(messages);
        alert.close();
    }
}, 2000);