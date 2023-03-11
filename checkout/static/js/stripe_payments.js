/* eslint-disable no-undef */

const stripePublicKey = document.getElementById('id_stripe_public_key').text.slice(1, -1);
const stripeClientSecret = document.getElementById('id_stripe_client_secret').text.slice(1, -1);

const options = {
  clientSecret: stripeClientSecret,
  appearance: {
    theme: 'night',
    variables: {
      colorPrimary: '#0570de',
      colorBackground: '#ffffff',
      colorText: '#30313d',
      colorDanger: '#df1b41',
      fontFamily: 'Ideal Sans, system-ui, sans-serif',
      spacingUnit: '2px',
      borderRadius: '4px',
    },
  },
};
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements(options);
const paymentElement = elements.create('payment');
const cardDiv = document.getElementById('card-element');
paymentElement.mount(cardDiv);

// Handle validation errors on the card.
paymentElement.addEventListener('change', (event) => {
  const errorDiv = document.getElementById('card-errors');
  if (event.error) {
    const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>
                ${event.error.message}
            </span>
        `;
    errorDiv.innerHTML = html;
  } else {
    errorDiv.textContent = '';
  }
});

const form = document.getElementById('payment-form');
form.addEventListener('submit', (event) => {
  event.preventDefault();

  // Disable all interactive elements on page while payment is processing
  paymentElement.update({ readOnly: true });
  document.getElementById('submit-button').disabled = true;
  document.getElementById('payment-overlay').classList.remove('d-none');
  document.getElementById('payment-overlay').classList.add('d-flex');
  document.getElementById('view-basket-link').style.pointerEvents = 'none';
  document.getElementById('cancel-purchase-link').style.pointerEvents = 'none';

  const shippingDetails = {
    name: form.full_name.value,
    phone: form.phone_number.value,
    address: {
      line1: form.street_address1.value,
      line2: form.street_address2.value,
      city: form.town_or_city.value,
      country: form.country.value,
      postal_code: form.postcode.value,
      state: form.county.value,
    },
  };

  // Post all of the form-data, the shouldSaveInfo flag and the Stripe client secret
  // to the backend so that this can all be saved before attempting to confirm payment.
  const url = '/checkout/save_order/';
  const formData = new FormData(form);
  formData.append('client_secret', stripeClientSecret);
  const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  const data = {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken,
    },
  };
  fetch(url, data).then(
    (response) => {
      // If the backend response returns ok, confirm the payment with Stripe.
      if (response.status === 200) {
        stripe.confirmPayment({
          elements,
          confirmParams: {
            shipping: shippingDetails,
          },
          redirect: 'if_required',
        }).then((result) => {
          // Handle any errors.
          if (result.error) {
            const html = `
                        <span class="icon" role="alert">
                            <i class="fas fa-times"></i>
                        </span>
                        <span>
                            ${result.error.message}
                        </span>
                    `;
            const errorDiv = document.getElementById('card-errors');
            errorDiv.innerHTML = html;

            // Reenable all interactive elements on page.
            paymentElement.disabled = 'false';
            paymentElement.update({ readOnly: false });
            document.getElementById('submit-button').disabled = false;
            document.getElementById('payment-overlay').classList.add('d-none');
            document.getElementById('payment-overlay').classList.remove('d-flex');
            document.getElementById('view-basket-link').style.pointerEvents = 'auto';
            document.getElementById('cancel-purchase-link').style.pointerEvents = 'auto';
          } else {
            // If there are no errors, make a POST request to the payment
            // confirmed view, and then redirect as indicated by the view.
            const confirmURL = '/checkout/payment_confirmed/';
            const payload = {
              payment_confirmed: 'True',
              client_secret: stripeClientSecret,
            };
            const fetchData = {
              method: 'POST',
              body: JSON.stringify(payload),
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
              },
            };
            fetch(confirmURL, fetchData).then(
              (res) => {
                console.log(res);
                console.log(res.url);
                // window.location = res.url;
              },
            );
          }
        });
      }
    },
  );
});
