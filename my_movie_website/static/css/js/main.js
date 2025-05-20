// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
  console.log("main.js loaded and DOM is ready!");

  // Example of a simple JavaScript interaction (optional, for demonstration)
  // You could add logic here for client-side validation, animations, etc.

  // Get the signup form
  const signupForm = document.querySelector('.auth-box form[action="#"]');

  if (signupForm) {
    signupForm.addEventListener("submit", function (event) {
      // For now, we are letting the form submit to the server.
      // If you wanted client-side validation, you'd add event.preventDefault()
      // and perform checks here before allowing submission.
      // For example:
      // const dobInput = document.getElementById('dob');
      // if (!dobInput.value) {
      //     alert('Please enter your date of birth!');
      //     event.preventDefault(); // Stop form submission
      // }
      console.log("Signup form submitted (client-side check)");
    });
  }
});
