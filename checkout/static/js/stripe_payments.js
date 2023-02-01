const stripePublicKey = document.getElementById('id_stripe_public_key').text.slice(1, -1);
const stripeClientSecret = document.getElementById('id_stripe_client_secret').text.slice(1, -1);

const options = {
    clientSecret: stripeClientSecret,
    appearance: {
        theme: 'stripe',
        variables: {
            colorPrimary: '#0570de',
            colorBackground: '#ffffff',
            colorText: '#30313d',
            colorDanger: '#df1b41',
            fontFamily: 'Ideal Sans, system-ui, sans-serif',
            spacingUnit: '2px',
            borderRadius: '4px',
        }
    }
}
console.log(stripePublicKey);
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

    paymentElement.update({ 'disabled': true });
    document.getElementById('submit-button').disabled = 'true';
    document.getElementById('payment-form').opacity = 0.2;

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
        }
    }

    stripe.confirmPayment({
        elements,
        confirmParams: {
            shipping: shippingDetails,
        },
        redirect: 'if_required',
    }).then((result) => {
        if (result.error) {
            console.log('Weve got an error');
            const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>
                ${event.error.message}
            </span>
        `;
            errorDiv.innerHTML = html;
            paymentElement.disabled= "false";
        } else {
            console.log('No errors - submitting form');
            form.submit();
        }
    })
});


