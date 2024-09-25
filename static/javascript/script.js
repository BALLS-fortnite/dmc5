// Navbar scripts
// taken and modified from w3schools; toggles dropdown on click
function toggleDropdown(event) {
    const dropdownContent = event.currentTarget.nextElementSibling;
    const arrow = event.currentTarget.querySelector('.dropdown-arrow');

    dropdownContent.classList.toggle("show");

    if (dropdownContent.classList.contains("show")) {
        arrow.src = "/static/images/arrow_drop_up.png";
    } else {
        arrow.src = "/static/images/arrow_drop_down.png";
    }
}

// Close the dropdown if the user clicks outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdownbutton') && !event.target.matches('.dropdown-arrow')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        const arrows = document.querySelectorAll('.dropdown-arrow');
        for (let dropdownIndex = 0; dropdownIndex < dropdowns.length; dropdownIndex++) {
            const openDropdown = dropdowns[dropdownIndex]; // More descriptive variable name
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
                arrows[dropdownIndex].src = "/static/images/arrow_drop_down.png"; 
            }
        }
    }
};

document.querySelectorAll('.dropdownbutton').forEach(button => {
    button.onclick = toggleDropdown;
});

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('show');
}

// scripts for showing and hiding password, for register and login page
document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    const togglePasswordRepeat = document.querySelector("#togglePasswordRepeat");
    const passwordRepeatInput = document.querySelector("#password_repeat")

    togglePassword.addEventListener("click", function() {
        const currentPasswordType = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", currentPasswordType);

        this.src = currentPasswordType  === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });

    togglePasswordRepeat.addEventListener("click", function() {
        const currentRepeatPasswordType = passwordRepeatInput.getAttribute("type") === "password" ? "text" : "password";
        passwordRepeatInput.setAttribute("type", currentRepeatPasswordType);

        this.src = currentRepeatPasswordType  === "password" ? "/static/images/visibility.png" : "/static/images/visibility_off.png";
    });
});

// script for strategy page
function updateCharCount() {
    const textarea = document.getElementById('strategy');
    const charCount = document.getElementById('charCount');
    const maxLength = textarea.getAttribute('maxlength');
    charCount.textContent = `${textarea.value.length} / ${maxLength} characters`;
}