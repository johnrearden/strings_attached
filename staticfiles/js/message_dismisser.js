/* eslint-disable no-undef */
setTimeout(() => {
  const messages = document.getElementById('msg');
  if (messages) {
    const alert = new bootstrap.Alert(messages);
    alert.close();
  }
}, 2000);
