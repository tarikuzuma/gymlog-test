function autoSubmitForm() {
    const inputField = document.getElementById('rfid'); // Make sure this ID matches your input field
    inputField.addEventListener('input', function() {
        if (inputField.value.length >= 10) {
            document.getElementById('autoSubmitInput').submit(); // Corrected form ID
        }
    });
}

function autoFocusInput() {
    const inputField = document.getElementById('rfid'); // Make sure this ID matches your input field
    inputField.focus();
    setInterval(function() {
        inputField.focus();
    }, 1000); // Adjust the interval as needed
}

// Initialize auto-submit form functionality when the page loads
document.addEventListener('DOMContentLoaded', function() {
    autoSubmitForm();
    autoFocusInput();
});

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.setAttribute('autocomplete', 'off');
    });
});