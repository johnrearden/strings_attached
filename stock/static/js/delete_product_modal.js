/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */
/**
 * Opens a confirmation modal to give the staff member a chance to change their mind
 */
const onDeleteProductButtonClick = (event, productID) => {
  // Prevent the row click listener from firing, as it redirects the user to a different page.
  event.stopPropagation();

  // Store the product id in the confirm buttons data attribute
  const hiddenProductIDInput = document.getElementById('hidden-product-id-input');
  hiddenProductIDInput.value = productID;

  // Open a modal dialog to ask user to confirm action.
  $('#delete-product-confirmation').modal('show');
};

/**
 * If the user doesn't confirm the product deletion, simply hides the confirmation
 * modal.
 * @param {Event} event
 */
const onRefuseDeleteProductClick = (event) => {
  $('#delete-product-confirmation').modal('hide');
};

/**
 * Makes a POST request to the backend to delete a product.
 */
const onConfirmDeleteProductClick = (event) => {
  // Hide the dialog again.
  $('#delete-product-confirmation').modal('hide');

  // Get the trackID from the confirm button.
  const form = document.getElementById('confirm-delete-form');
  form.submit();
};
