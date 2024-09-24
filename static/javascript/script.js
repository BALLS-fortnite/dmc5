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

// taken and modified from w3schools, toggles dropdown on click
function toggleDropdown(event) {
    const dropdownContent = event.currentTarget.nextElementSibling;
    const arrow = event.currentTarget.querySelector('.dropdown-arrow');

    // Toggle the dropdown content
    dropdownContent.classList.toggle("show");

    // Change the arrow image based on dropdown state
    if (dropdownContent.classList.contains("show")) {
        arrow.src = "/static/images/arrow_drop_up.png"; // Change to up arrow
    } else {
        arrow.src = "/static/images/arrow_drop_down.png"; // Change back to down arrow
    }
}

// Close the dropdown if the user clicks outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdownbutton') && !event.target.matches('.dropdown-arrow')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        const arrows = document.querySelectorAll('.dropdown-arrow');
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
                arrows[i].src = "/static/images/arrow_drop_down.png"; // Reset arrow to down
            }
        }
    }
};

// Attach the toggle function to the buttons
document.querySelectorAll('.dropdownbutton').forEach(button => {
    button.onclick = toggleDropdown;
});

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('show');
}