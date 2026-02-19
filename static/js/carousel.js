/* carousel.js – auto-playing image carousel */
(function () {
  const slides  = document.querySelectorAll('.slide');
  const dotsEl  = document.getElementById('carouselDots');
  const chipsEl = document.getElementById('slideChips');

  if (!slides.length) return;

  let current = 0;
  let timer;

  /* build dots + chips */
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

  resetTimer();
})();
