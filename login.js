document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm"); // Ensure the form has id="loginForm"

    // Replace the alert div creation with new enhanced version
    const alertDiv = document.createElement('div');
    alertDiv.className = 'fixed top-0 left-1/2 -translate-x-1/2 max-w-sm w-full mx-auto p-4 rounded-b-lg shadow-lg hidden transform transition-all duration-500 ease-in-out z-50';
    alertDiv.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <span class="alert-icon flex-shrink-0"></span>
                <p class="alert-message text-sm font-medium"></p>
            </div>
            <button class="text-gray-400 hover:text-gray-500">
                <svg class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    `;
    document.body.appendChild(alertDiv);

    // Enhanced showAlert function
    function showAlert(message, isSuccess = true) {
        const alertMessage = alertDiv.querySelector('.alert-message');
        const alertIcon = alertDiv.querySelector('.alert-icon');
        
        // Set colors and icon based on status
        if (isSuccess) {
            alertDiv.className = `fixed top-0 left-1/2 -translate-x-1/2 max-w-sm w-full mx-auto p-4 rounded-b-lg shadow-lg transform transition-all duration-500 ease-in-out z-50 bg-green-50 border-t-4 border-green-500`;
            alertIcon.innerHTML = `
                <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
            `;
        } else {
            alertDiv.className = `fixed top-0 left-1/2 -translate-x-1/2 max-w-sm w-full mx-auto p-4 rounded-b-lg shadow-lg transform transition-all duration-500 ease-in-out z-50 bg-red-50 border-t-4 border-red-500`;
            alertIcon.innerHTML = `
                <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>
            `;
        }

        alertMessage.textContent = message;
        alertDiv.classList.remove('hidden');
        
        // Animate in
        alertDiv.style.transform = 'translate(-50%, -100%)';
        setTimeout(() => {
            alertDiv.style.transform = 'translate(-50%, 0)';
        }, 100);

        // Auto dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.style.transform = 'translate(-50%, -100%)';
            setTimeout(() => {
                alertDiv.classList.add('hidden');
            }, 500);
        }, 3000);
    }

    // Add click handler for close button
    alertDiv.querySelector('button').addEventListener('click', () => {
        alertDiv.style.transform = 'translate(-50%, -100%)';
        setTimeout(() => {
            alertDiv.classList.add('hidden');
        }, 500);
    });

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Get form values
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Basic validation (optional since HTML5 'required' is already used)
        if (!username || !password) {
            showAlert("Please enter both username and password.", false);
            return;
        }

        // Prepare the data to send
        const formData = { username, password };

        const button = event.target.querySelector('button[type="submit"]');
        button.classList.add('btn-loading');
        button.disabled = true;

        try {
            // Send POST request to the backend login route
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData),
            });

            console.log('Response status:', response.status); // Check response status
            const data = await response.json(); // Get JSON response

            console.log('Response data:', data); // Log the response

            if (response.ok) {
                // Store user data properly
                sessionStorage.clear(); // Clear any existing data
                sessionStorage.setItem('user_id', data.user.id);
                sessionStorage.setItem('username', username); // Use the actual username
                sessionStorage.setItem('email', data.user.email);
                sessionStorage.setItem('class_name', data.user.class_name);
                sessionStorage.setItem('isLoggedIn', 'true');

                showAlert(`Welcome back, ${username}!`, true);
                
                // Delay redirect to show the welcome message
                setTimeout(() => {
                    window.location.href = "dashboard.html"; // Update this to your dashboard page's path
                }, 1500);
            } else {
                showAlert(data.message || 'Login failed', false);
            }
        } catch (error) {
            console.error('Error during login:', error);
            showAlert('An error occurred. Please try again.', false);
        } finally {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    });

    // Add smooth appearance animation to form elements
    document.querySelectorAll('.floating-label input').forEach((input, index) => {
        input.style.opacity = '0';
        input.style.transform = 'translateY(20px)';
        setTimeout(() => {
            input.style.transition = 'all 0.3s ease';
            input.style.opacity = '1';
            input.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});
