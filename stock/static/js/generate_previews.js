/* eslint-disable no-undef */

// This javascript snippet generates previews for the audio_clip and image
// inputs on the ProductAdd and ProductEdit forms

const imageInput = document.getElementById('id_image');
const imagePreview = document.getElementById('image-preview');
imageInput.addEventListener('change', () => {
  const source = URL.createObjectURL(imageInput.files[0]);
  imagePreview.src = source;
});
const audioInput = document.getElementById('id_audio_clip');
const audioElement = document.getElementById('audio-preview');
audioInput.addEventListener('change', () => {
  const source = URL.createObjectURL(audioInput.files[0]);
  audioElement.src = source;
});
