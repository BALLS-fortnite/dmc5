// function for showing and hiding password
document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    const togglePasswordRepeat = document.querySelector("#togglePasswordRepeat");
    const passwordRepeatInput = document.querySelector("#password_repeat")

    // toggle for password input box
    togglePassword.addEventListener("click", function() {
        const currentPasswordType = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", currentPasswordType);

        this.src = currentPasswordType  === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
    // toggle for repeat password input box
    togglePasswordRepeat.addEventListener("click", function() {
        const currentRepeatPasswordType = passwordRepeatInput.getAttribute("type") === "password" ? "text" : "password";
        passwordRepeatInput.setAttribute("type", currentRepeatPasswordType);

        this.src = currentRepeatPasswordType  === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
});

// function to show character count for updating strategy
function updateCharCount() {
    const textarea = document.getElementById('strategy');
    const charCount = document.getElementById('charCount');
    charCount.textContent = `${textarea.value.length} / 1000 characters`;
}