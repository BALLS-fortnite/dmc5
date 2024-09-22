document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");
    const passwordRepeatInput = document.querySelector("#password_repeat");

    togglePassword.addEventListener("click", function() {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        passwordRepeatInput.setAttribute("type", type);
        this.textContent = type === "password" ? "Show Password" : "Hide Password"; // Change button text
    });
});