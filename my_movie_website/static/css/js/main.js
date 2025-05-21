// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
  console.log("main.js loaded and DOM is ready!");

  // You can add client-side JavaScript here as your project grows.
  // For example, dynamic content loading, animations, more complex form validations, etc.

  // Example: Fading out flash messages after a few seconds (optional)
  const flashMessages = document.querySelectorAll(".alert");
  if (flashMessages.length > 0) {
    flashMessages.forEach(function (message) {
      setTimeout(function () {
        message.style.transition = "opacity 1s ease-out";
        message.style.opacity = "0";
        // Remove the element after the fade out to clear up space
        message.addEventListener("transitionend", function () {
          message.remove();
        });
      }, 5000); // Messages fade out after 5 seconds
    });
  }
});
