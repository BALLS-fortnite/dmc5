document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    const togglePasswordRepeat = document.querySelector("#togglePasswordRepeat");
    const passwordRepeatInput = document.querySelector("#password_repeat")

    togglePassword.addEventListener("click", function() {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);

        // change the image
        this.src = type === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
    // toggle for repeat password input box
    togglePasswordRepeat.addEventListener("click", function() {
        const type = passwordRepeatInput.getAttribute("type") === "password" ? "text" : "password";
        passwordRepeatInput.setAttribute("type", type);

        // change the image
        this.src = type === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
});