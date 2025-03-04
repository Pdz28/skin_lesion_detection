function logout() {
  fetch('/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      window.location.href = '/login';
    }
  });
}

function processNewImage() {
  const fileInput = document.getElementById('new-image-upload');
  const file = fileInput.files[0];

  if (file && file.size <= 20000000) { // Check file size (max 20MB)
    const formData = new FormData();
    formData.append('image', file);

    fetch('/process-image', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.original_image && data.result_image) {
        // Redirect to results page with the image filenames
        window.location.href = `/results?original_image=${data.original_image}&result_image=${data.result_image}&status=${encodeURIComponent(JSON.stringify(data.status))}`;
      } else {
        alert('Error processing image.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  } else {
    alert('Please select an image file (max 20MB).');
  }
}
