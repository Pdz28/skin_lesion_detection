document.getElementById('login-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const data = {
    username: formData.get('username'),
    password: formData.get('password')
  };

  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => {
        throw new Error(err.message || 'An error occurred');
      });
    }
    return response.json();
  })
  .then(data => {
    let countdown = 5;
    const successMessage = document.getElementById('success-message');
    successMessage.textContent = `Login successful! Redirecting you to the main page in ${countdown} seconds.`;
    successMessage.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';

    const interval = setInterval(() => {
      countdown--;
      successMessage.textContent = `Login successful! Redirecting you to the main page in ${countdown} seconds.`;
      if (countdown === 0) {
        clearInterval(interval);
        window.location.href = '/';
      }
    }, 1000);
  })
  .catch(error => {
    document.getElementById('error-message').textContent = error.message;
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
  });
});