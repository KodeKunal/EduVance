document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm"); // Ensure the form has id="loginForm"

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Get form values
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Basic validation (optional since HTML5 'required' is already used)
        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        // Prepare the data to send
        const formData = { username, password };

        try {
            // Send POST request to the backend login route
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            console.log('Response status:', response.status); // Check response status
            const data = await response.text(); // Get raw response text

            console.log('Response data:', data); // Log the raw response

            if (response.ok) {
                const jsonData = JSON.parse(data); // Safely parse JSON
                alert(jsonData.message); // Show success message
                // Store the username in sessionStorage for access on the next page
                sessionStorage.setItem('username', username);
                sessionStorage.setItem('password', password);
                // Redirect to the dashboard after successful login
                window.location.href = "dashboard.html"; // Update this to your dashboard page's path
            } else {
                // Attempt to parse the error message
                try {
                    const errorData = JSON.parse(data);
                    alert(errorData.message);
                } catch (e) {
                    // If the response is not JSON, show the raw data
                    alert(data);
                }
            }
        } catch (error) {
            console.error('Error during login:', error);
            alert('An error occurred. Please try again.');
        }
    });
});
