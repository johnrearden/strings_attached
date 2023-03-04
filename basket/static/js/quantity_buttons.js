/* eslint-disable no-loop-func */
/* eslint-disable no-restricted-syntax */
/* eslint-disable no-restricted-globals */
/* eslint no-undef: "error" */
/* eslint-env browser */

/**
 * This function disables the increment and decrement buttons if they are
 * currently set to the max or min values as specified in the html element itself.
 * It also checks to ensure that the user has not manually entered an out-of-range
 * value, and corrects this value to the max or min as appropriate.
*/
const disableButtonsIfRangeExceeded = (id) => {
  const input = document.getElementById(`quantity-input-${id}`);
  const plusButton = document.getElementById(`increment-${id}`);
  const minusButton = document.getElementById(`decrement-${id}`);
  const min = input.getAttribute('data-min');
  const max = input.getAttribute('data-max');
  const value = parseInt(input.value, 10);
  minusButton.disabled = value <= min;
  plusButton.disabled = value >= max;

  // Check to ensure user has not manually entered an out-of-range value.
  if (value < min) {
    input.value = min;
  }
  if (value > max) {
    input.value = max;
  }
  if (isNaN(value)) {
    input.value = 1;
  }
};

/**
 * This function runs on page load, and iterates through any quantity inputs
 * on the page, adding listeners to their respective increment and decrement
 * buttons. It also adds a change listener to the input that calls the validation
 * function disableButtonsIfRangeExceeded().
 */

document.addEventListener('DOMContentLoaded', () => {
  const valueInputs = document.getElementsByClassName('quantity-input');
  let quantitySubmitTimerID;
  for (const input of valueInputs) {
    const id = input.id.replace('quantity-input-', '');
    const form = document.getElementById(`form_${id}`);
    const shouldSubmitOnChange = input.getAttribute('data-should_submit') === 'true';
    disableButtonsIfRangeExceeded(id);
    input.addEventListener('change', () => {
      disableButtonsIfRangeExceeded(id);
    });

    const incrementButton = document.getElementById(`increment-${id}`);
    incrementButton.addEventListener('click', (event) => {
      event.preventDefault();
      let value = parseInt(input.value, 10);
      value += 1;
      input.value = value;
      disableButtonsIfRangeExceeded(id);
      if (shouldSubmitOnChange) {
        clearTimeout(quantitySubmitTimerID);
        quantitySubmitTimerID = setTimeout(() => {
          form.submit();
        }, 500);
      }
    });
    const decrementButton = document.getElementById(`decrement-${id}`);
    decrementButton.addEventListener('click', (event) => {
      event.preventDefault();
      let value = parseInt(input.value, 10);
      value -= 1;
      input.value = value;
      disableButtonsIfRangeExceeded(id);
      if (shouldSubmitOnChange) {
        clearTimeout(quantitySubmitTimerID);
        quantitySubmitTimerID = setTimeout(() => {
          form.submit();
        }, 500);
      }
    });
  }
});
