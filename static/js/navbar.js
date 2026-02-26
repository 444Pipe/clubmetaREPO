document.addEventListener('DOMContentLoaded', function(){
  const toggle = document.querySelector('.nav-toggle');
  const menu = document.getElementById('primary-menu');
  if(toggle && menu){
    toggle.addEventListener('click', function(){
      const expanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', String(!expanded));
      menu.classList.toggle('open');
      // add body class so CSS can reveal mobile submenu / global menu-info when nav is open
      document.body.classList.toggle('nav-open');
    });
  }

  // Mobile: make dropdown toggles expandable
  document.querySelectorAll('.has-dropdown > .dropdown-toggle').forEach(function(btn){
    btn.addEventListener('click', function(e){
      // On mobile, dropdown-toggle should always behave as a toggle (do not navigate)
      if(window.innerWidth <= 900){
        e.preventDefault();
        const parent = btn.parentElement;
        parent.classList.toggle('expanded');
        const panel = parent.querySelector('.dropdown-panel');
        if(panel){
          panel.style.display = parent.classList.contains('expanded') ? 'block' : 'none';
        }
      }
    });
  });

  // Handle menu_info groups (desktop hover + mobile expand)
  document.querySelectorAll('.menu-info .menu-group > a').forEach(function(btn){
    btn.addEventListener('click', function(e){
      const parent = btn.parentElement;
      const submenu = parent.querySelector('.submenu');
      if(window.innerWidth <= 900){
        // mobile: if the link points to a real href (e.g. index) allow navigation.
        const href = btn.getAttribute('href');
        if(href && href.trim() !== '#' && href.trim() !== ''){
          // allow default navigation to happen
          return;
        }
        // otherwise toggle submenu
        e.preventDefault();
        const isOpen = parent.classList.toggle('expanded');
        if(submenu) submenu.style.display = isOpen ? 'block' : 'none';
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      } else {
        // desktop: allow hover behavior, but ensure aria toggles for keyboard
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!expanded));
      }
    });

    // Touch handling to distinguish scroll vs tap
    let startX=0, startY=0, moved=false;
    btn.addEventListener('touchstart', function(ev){ moved=false; const t = ev.touches && ev.touches[0]; if(t){ startX=t.clientX; startY=t.clientY; } }, {passive:true});
    btn.addEventListener('touchmove', function(ev){ const t = ev.touches && ev.touches[0]; if(!t) return; const dx=Math.abs(t.clientX-startX); const dy=Math.abs(t.clientY-startY); if(dy>10 && dy>dx) moved=true; }, {passive:true});
    btn.addEventListener('touchend', function(ev){ if(moved) return; // treat as tap
      if(window.innerWidth <= 900){ ev.preventDefault(); btn.click(); }
    }, {passive:false});
  });

  // Keyboard navigation for menu-info
  document.querySelectorAll('.menu-info [role="menuitem"]').forEach(function(item){
    item.addEventListener('keydown', function(e){
      const key = e.key;
      if(key === 'ArrowRight' || key === 'Right'){
        e.preventDefault(); const next = item.closest('li') && item.closest('li').nextElementSibling; if(next) next.querySelector('[role="menuitem"]').focus();
      }
      if(key === 'ArrowLeft' || key === 'Left'){
        e.preventDefault(); const prev = item.closest('li') && item.closest('li').previousElementSibling; if(prev) prev.querySelector('[role="menuitem"]').focus();
      }
      if(key === 'Enter' || key === ' '){
        const parent = item.closest('li'); if(parent && parent.classList.contains('menu-group')){ e.preventDefault(); item.click(); }
      }
    });
  });

  // Close menu on outside click (mobile)
  document.addEventListener('click', function(e){
    const isClickInside = menu && menu.contains(e.target) || toggle && toggle.contains(e.target);
    if(!isClickInside && menu && menu.classList.contains('open')){
      menu.classList.remove('open');
      if(toggle) toggle.setAttribute('aria-expanded','false');
      // remove body class too
      document.body.classList.remove('nav-open');
    }
  });
});
