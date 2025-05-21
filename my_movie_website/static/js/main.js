// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.getElementById("movieCarousel");
  if (!carousel) {
    console.error(
      'Carousel element with ID "movieCarousel" not found. Automatic fading disabled.'
    );
    return;
  }

  const movieCards = carousel.querySelectorAll(".movie-card-fade"); // Select the correct class for fading cards
  if (movieCards.length === 0) {
    console.warn(
      "No movie cards found in carousel. Automatic fading disabled."
    );
    return;
  }

  let currentIndex = 0;
  const fadeIntervalTime = 4000; // 4 seconds

  // Function to show a specific slide and hide others
  function showSlide(index) {
    movieCards.forEach((card, i) => {
      if (i === index) {
        card.style.opacity = "1";
        card.style.zIndex = "1"; // Bring active card to front
      } else {
        card.style.opacity = "0";
        card.style.zIndex = "0"; // Send inactive cards to back
      }
    });
  }

  // Initialize: Show the first slide immediately
  showSlide(currentIndex);

  // Function to advance to the next slide
  function nextSlide() {
    currentIndex = (currentIndex + 1) % movieCards.length; // Loop back to start
    showSlide(currentIndex);
  }

  // Set interval for automatic fading
  // Clear any existing interval to prevent multiple intervals if script is re-run
  if (window.movieCarouselInterval) {
    clearInterval(window.movieCarouselInterval);
  }
  window.movieCarouselInterval = setInterval(nextSlide, fadeIntervalTime); // Store interval ID for clearing
});
