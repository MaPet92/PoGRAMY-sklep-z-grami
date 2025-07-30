document.addEventListener('DOMContentLoaded', function () {
  const messageBox = document.getElementById('cart-message');
  const cartCount = document.getElementById('cart-count');

  document.querySelectorAll('.add-to-cart-btn').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const quantity = this.dataset.quantity || 1;
      ajaxCartUpdate('/add_to_cart_ajax/', productId, quantity);
    });
  });

  document.querySelectorAll('.remove-from-cart-btn').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const quantity = this.dataset.quantity || 1;
      ajaxCartUpdate('/remove_from_cart_ajax/', productId, quantity);
    });
  });

  function ajaxCartUpdate(url, productId, quantity) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        messageBox.textContent = data.message;
        messageBox.style.color = 'green';
        updateCartCount();
      } else {
        messageBox.textContent = data.error;
        messageBox.style.color = 'red';
      }
    })
    .catch(error => {
      console.error('Błąd:', error);
      messageBox.textContent = 'Wystąpił błąd';
      messageBox.style.color = 'red';
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function updateCartCount() {
    fetch('/cart_count_ajax/')
      .then(response => response.json())
      .then(data => {
        cartCount.textContent = data.count;
      })
      .catch(() => {
        cartCount.textContent = '0';
      });
  }

  updateCartCount();
});