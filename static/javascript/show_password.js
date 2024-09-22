document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    togglePassword.addEventListener("click", function() {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);

        // Toggle the image
        this.src = type === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
});
