/* eslint-disable no-undef */

/**
 * This method makes an empty POST request to the Subscription Success view, prompting
 * it to call out to the Stripe subscription management url.
 */
const form = document.getElementById('form');
const csrfToken = document.getElementByName('csrfmiddlewaretoken');
form.addEventListener('submit', (event) => {
  event.preventDefault();
  url = 'video_lessons/subscription_succeeded/';
  fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
  }).then((response) => {
    window.location = response.url;
  });
});
