/* ============================================================
   BANDBUNK — main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Mobile nav toggle ───────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mainNav   = document.getElementById('main-nav');
  if (hamburger && mainNav) {
    hamburger.addEventListener('click', () => {
      mainNav.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !mainNav.contains(e.target)) {
        mainNav.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss messages after 5 seconds ───────────────
  const messages = document.querySelectorAll('.alert');
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.4s ease';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });

  // ── Star rating inputs ───────────────────────────────────
  document.querySelectorAll('.star-rating-input').forEach(widget => {
    const labels = widget.querySelectorAll('label');
    labels.forEach(label => {
      label.addEventListener('mouseenter', () => {
        label.style.color = 'var(--purple-bright)';
      });
    });
  });

  // ── Image preview for file inputs ───────────────────────
  document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
    const previewId = input.dataset.preview;
    const preview   = document.getElementById(previewId);
    if (!preview) return;
    input.addEventListener('change', () => {
      const file = input.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => {
          preview.src = e.target.result;
          preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  });

  // ── Date validation: check-out must be after check-in ───
  const checkIn  = document.getElementById('id_check_in');
  const checkOut = document.getElementById('id_check_out');
  if (checkIn && checkOut) {
    checkIn.addEventListener('change', () => {
      if (checkOut.value && checkOut.value <= checkIn.value) {
        checkOut.value = '';
      }
      checkOut.min = checkIn.value;
    });
  }

  // ── Confirm before destructive actions ──────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Animate elements on scroll (IntersectionObserver) ───
  const fadeEls = document.querySelectorAll('.fade-up');
  if ('IntersectionObserver' in window && fadeEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animationPlayState = 'running';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    fadeEls.forEach(el => {
      el.style.animationPlayState = 'paused';
      observer.observe(el);
    });
  }

  // ── Listing type icon helper ─────────────────────────────
  window.getListingIcon = (type) => {
    const icons = {
      sofa: '🛋️',
      spare_room: '🚪',
      floor_space: '💨',
      garage: '🎸',
    };
    return icons[type] || '🏠';
  };

  // ── Format price ─────────────────────────────────────────
  window.formatPrice = (p) => `£${parseFloat(p).toFixed(2)}`;

});


/* ── Map initialisation (called from map templates) ───────── */
window.initMap = (listings, options = {}) => {
  const mapEl = document.getElementById('map');
  if (!mapEl) return;

  const map = L.map('map', {
    center: options.center || [54.5, -3.5],
    zoom: options.zoom || 6,
    zoomControl: true,
  });

  // Dark tile layer that matches the BandBunk aesthetic
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors © CARTO',
    maxZoom: 19,
  }).addTo(map);

  // Custom marker icon
  const purpleIcon = L.divIcon({
    className: '',
    html: `<div style="
      background: #9b1dfa;
      border: 2px solid #f5f5f5;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      width: 28px; height: 28px;
      box-shadow: 0 0 10px rgba(155,29,250,0.6);
    "></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -30],
  });

  listings.forEach(listing => {
    if (!listing.lat || !listing.lng) return;
    const marker = L.marker([listing.lat, listing.lng], { icon: purpleIcon }).addTo(map);
    marker.bindPopup(`
      <div style="min-width:200px; font-family:'Barlow',sans-serif; background:#111; color:#f5f5f5; border:1px solid #9b1dfa; border-radius:8px; overflow:hidden;">
        <div style="padding:0.75rem 1rem; border-bottom:1px solid #2e2e2e;">
          <strong style="font-size:0.95rem;">${listing.title}</strong><br>
          <span style="font-size:0.8rem; color:#999;">${listing.type_display} · ${listing.town_city}</span>
        </div>
        <div style="padding:0.75rem 1rem; display:flex; justify-content:space-between; align-items:center;">
          <span style="color:#b44dff; font-weight:700;">£${listing.price}/night</span>
          <a href="/listings/${listing.id}/" style="background:#9b1dfa; color:#f5f5f5; padding:0.3rem 0.7rem; border-radius:4px; font-size:0.78rem; text-decoration:none; font-weight:600;">View</a>
        </div>
      </div>
    `, { className: 'bb-popup' });
  });

  return map;
};
