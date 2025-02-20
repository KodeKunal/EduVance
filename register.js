document.addEventListener("DOMContentLoaded", () => {
    const registrationForm = document.getElementById("registration-form");

    registrationForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Get form values (match the IDs with your form fields)
        const username = document.getElementById("username").value.trim(); // Match ID
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const confirmPassword = document.getElementById("confirm-password").value.trim(); // Match ID
        const className = document.getElementById("class").value.trim();

        // Basic validation
        if (!username || !email || !password || !confirmPassword || !className) {
            alert("Please fill in all fields.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        // Form submission data
        const formData = {
            username: username,
            email: email,
            password: password,
            className: className,
            progress: 0 // Initialize user's progress to 0
        };

        try {
            const response = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                // Show success message with better UI
                Swal.fire({
                    icon: 'success',
                    title: 'Registration Successful!',
                    text: 'Your account has been created. Please login to continue.',
                    showConfirmButton: false,
                    timer: 2000
                }).then(() => {
                    window.location.href = 'login.html';
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Registration Failed',
                    text: data.message || 'An error occurred during registration'
                });
            }
        } catch (error) {
            console.error('Error during registration:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'An error occurred during registration. Please try again.'
            });
        }
    });
});
