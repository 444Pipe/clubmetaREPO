// Animación de fade-in para la tarjeta de visión
window.addEventListener('DOMContentLoaded', function() {
  var card = document.querySelector('.vision-card');
  if(card) {
    setTimeout(function() {
      card.classList.add('visible');
    }, 200);
  }
});
