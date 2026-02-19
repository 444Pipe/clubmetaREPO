// main.js — interactions for CLUB EL META
// Smooth scroll for internal links, reveal-on-scroll, and simple button effects

document.addEventListener('DOMContentLoaded', function () {
  // Eliminar la clase no-js del body para mostrar el menú de escritorio solo cuando el JS y CSS están listos
  document.body.classList.remove('no-js');
  // --- Menú móvil: ocultar/mostrar usando atributo hidden para evitar FOUC ---
  var mobileMenu = document.getElementById('mobileMenu');
  var mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
  var mobileMenuToggle = document.getElementById('mobileMenuToggle');
  if (mobileMenu && mobileMenuOverlay && mobileMenuToggle) {
    // Mostrar menú
    mobileMenuToggle.addEventListener('click', function () {
      mobileMenu.removeAttribute('hidden');
      mobileMenuOverlay.removeAttribute('hidden');
      mobileMenu.setAttribute('aria-hidden', 'false');
    });
    // Ocultar menú al hacer click en overlay
    mobileMenuOverlay.addEventListener('click', function () {
      mobileMenu.setAttribute('hidden', '');
      mobileMenuOverlay.setAttribute('hidden', '');
      mobileMenu.setAttribute('aria-hidden', 'true');
    });
  }
  // Smooth scroll for links with href starting with # or data-scroll-target
  function smoothScrollTo(targetEl) {
    if (!targetEl) return;
    const top = targetEl.getBoundingClientRect().top + window.pageYOffset - 70; // offset for header
    window.scrollTo({ top, behavior: 'smooth' });
  }

  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (!href || href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        smoothScrollTo(target);
      }
    });
  });

  // Data attribute-driven scroll (e.g., <button data-scroll-target="#contacto">)
  document.querySelectorAll('[data-scroll-target]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const sel = this.getAttribute('data-scroll-target');
      const target = document.querySelector(sel);
      if (target) smoothScrollTo(target);
    });
  });

  // Reveal on scroll using IntersectionObserver
  const revealElements = document.querySelectorAll('.reveal');
  if (revealElements.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    revealElements.forEach(el => io.observe(el));
  }

  // Simple button press animation (keyboard + pointer)
  document.querySelectorAll('.btn, button').forEach(btn => {
    btn.addEventListener('pointerdown', () => btn.classList.add('pressed'));
    btn.addEventListener('pointerup', () => btn.classList.remove('pressed'));
    btn.addEventListener('pointerleave', () => btn.classList.remove('pressed'));
    btn.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') btn.classList.add('pressed'); });
    btn.addEventListener('keyup', () => btn.classList.remove('pressed'));
  });

});
