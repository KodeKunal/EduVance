document.addEventListener("DOMContentLoaded", () => {
    const registrationForm = document.getElementById("registration-form");

    registrationForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Get form values (match the IDs with your form fields)
        const fullName = document.getElementById("name").value.trim(); // Match ID
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const confirmPassword = document.getElementById("confirm-password").value.trim(); // Match ID

        // Basic validation
        if (!fullName || !email || !password || !confirmPassword) {
            alert("Please fill in all fields.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        // Form submission data
        const formData = {
            name: fullName,  // Adjust field name to match the backend schema
            email: email,
            password: password,
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
                // Show success message
                alert(data.message);

                // Mark profile as incomplete in localStorage (this will be used to guide users to complete their profile later)
                localStorage.setItem('profileComplete', 'false');

                // Redirect to the profile completion page (after registration)
                window.location.href = 'profile_completion.html';
            } else {
                alert(data.message); // Display error message if registration fails
            }
        } catch (error) {
            console.error('Error during registration:', error);
            alert('An error occurred during registration. Please try again.');
        }
    });
});
