// /* carousel.js – auto-playing image carousel */
// (function () {
//   const slides  = document.querySelectorAll('.slide');
//   const dotsEl  = document.getElementById('carouselDots');
//   const chipsEl = document.getElementById('slideChips');

//   if (!slides.length) return;

//   let current = 0;
//   let timer;

//   /* build dots + chips */
//   slides.forEach((slide, i) => {
//     const dot = document.createElement('button');
//     dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
//     dot.setAttribute('aria-label', `Slide ${i + 1}`);
//     dot.addEventListener('click', () => goTo(i));
//     dotsEl.appendChild(dot);

//     const chip = document.createElement('button');
//     chip.className = 'slide-chip' + (i === 0 ? ' active' : '');
//     chip.textContent = slide.dataset.label || `Slide ${i + 1}`;
//     chip.addEventListener('click', () => goTo(i));
//     chipsEl.appendChild(chip);
//   });

//   function goTo(n) {
//     slides[current].classList.remove('active');
//     dotsEl.children[current].classList.remove('active');
//     chipsEl.children[current].classList.remove('active');

//     current = (n + slides.length) % slides.length;

//     slides[current].classList.add('active');
//     dotsEl.children[current].classList.add('active');
//     chipsEl.children[current].classList.add('active');

//     resetTimer();
//   }

//   function resetTimer() {
//     clearInterval(timer);
//     timer = setInterval(() => goTo(current + 1), 4500);
//   }

//   document.getElementById('next').addEventListener('click', () => goTo(current + 1));
//   document.getElementById('prev').addEventListener('click', () => goTo(current - 1));

//   resetTimer();
// })();

/* carousel.js – auto-playing image carousel with touch/swipe support */
(function () {
  const slides    = document.querySelectorAll('.slide');
  const dotsEl    = document.getElementById('carouselDots');
  const chipsEl   = document.getElementById('slideChips');
  const slideWrap = document.getElementById('carousel');

  if (!slides.length) return;

  let current = 0;
  let timer;

  /* ── BUILD DOTS + CHIPS ───────────────────────────────── */
  slides.forEach((slide, i) => {
    const dot = document.createElement('button');
    dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', `Slide ${i + 1}`);
    dot.addEventListener('click', () => goTo(i));
    dotsEl.appendChild(dot);

    const chip = document.createElement('button');
    chip.className = 'slide-chip' + (i === 0 ? ' active' : '');
    chip.textContent = slide.dataset.label || `Slide ${i + 1}`;
    chip.addEventListener('click', () => goTo(i));
    chipsEl.appendChild(chip);
  });

  /* ── NAVIGATION ───────────────────────────────────────── */
  function goTo(n) {
    slides[current].classList.remove('active');
    dotsEl.children[current].classList.remove('active');
    chipsEl.children[current].classList.remove('active');

    current = (n + slides.length) % slides.length;

    slides[current].classList.add('active');
    dotsEl.children[current].classList.add('active');
    chipsEl.children[current].classList.add('active');

    resetTimer();
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => goTo(current + 1), 4500);
  }

  document.getElementById('next').addEventListener('click', () => goTo(current + 1));
  document.getElementById('prev').addEventListener('click', () => goTo(current - 1));

  /* ── TOUCH / SWIPE ────────────────────────────────────── */
  const SWIPE_THRESHOLD  = 40;   // px — minimum horizontal travel to count as a swipe
  const SWIPE_MAX_VERT   = 80;   // px — maximum vertical drift before we bail (user is scrolling)

  let touchStartX = 0;
  let touchStartY = 0;
  let touchDeltaX = 0;
  let isSwiping   = false;

  slideWrap.addEventListener('touchstart', (e) => {
    const t     = e.changedTouches[0];
    touchStartX = t.clientX;
    touchStartY = t.clientY;
    touchDeltaX = 0;
    isSwiping   = true;
    clearInterval(timer);           // pause auto-advance while user is touching
  }, { passive: true });

  slideWrap.addEventListener('touchmove', (e) => {
    if (!isSwiping) return;
    const t    = e.changedTouches[0];
    touchDeltaX      = t.clientX - touchStartX;
    const deltaY     = t.clientY - touchStartY;

    // if the user is clearly scrolling vertically, cancel swipe detection
    if (Math.abs(deltaY) > SWIPE_MAX_VERT && Math.abs(touchDeltaX) < SWIPE_THRESHOLD) {
      isSwiping = false;
    }
  }, { passive: true });

  slideWrap.addEventListener('touchend', () => {
    if (!isSwiping) { resetTimer(); return; }

    if (touchDeltaX < -SWIPE_THRESHOLD) {
      goTo(current + 1);   // swipe left  → next
    } else if (touchDeltaX > SWIPE_THRESHOLD) {
      goTo(current - 1);   // swipe right → prev
    } else {
      resetTimer();         // tap or tiny movement — just resume
    }

    isSwiping   = false;
    touchDeltaX = 0;
  }, { passive: true });

  // also handle touchcancel (e.g. incoming call interrupts touch)
  slideWrap.addEventListener('touchcancel', () => {
    isSwiping = false;
    resetTimer();
  }, { passive: true });

  resetTimer();
})();
