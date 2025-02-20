
    // Base URL of your backend API
    const API_BASE_URL = 'https://your-backend-api.com/api'; // Replace with your actual API URL

    // Function to fetch recommended courses
    async function fetchRecommendedCourses() {
        const token = localStorage.getItem('token');
        if (!token) {
            alert('No token found. Please log in.');
            window.location.href = 'index.html';
            return;
        }
    
        try {
            const response = await fetch(`${API_BASE_URL}/content`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to fetch courses.');
            }
    
            const courses = await response.json();
            displayCourses(courses);
        } catch (error) {
            console.error('Error fetching courses:', error);
            alert(error.message);
        }
    }
    
    // Function to display courses
    function displayCourses(courses) {
        const coursesContainer = document.querySelectorAll('.course-card');
        coursesContainer.forEach((container, index) => {
            if (courses[index]) {
                const course = courses[index];
                container.querySelector('h4').textContent = course.title;
                container.querySelector('p').textContent = course.description;
                container.querySelector('a').href = `course.html?id=${course._id}`; // Ensure course.html exists
                container.querySelector('button').dataset.courseId = course._id;
    
                // Add event listener to handle course enrollment
                container.querySelector('button').addEventListener('click', () => {
                    enrollInCourse(course._id);
                });
            } else {
                container.style.display = 'none'; // Hide empty course cards
            }
        });
    }
    
    // Function to enroll in a course (mock implementation)
    function enrollInCourse(courseId) {
        alert(`You have enrolled in course with ID: ${courseId}`);
    }
    
    // Function to display user progress
    function displayProgress() {
        const ctx = document.getElementById('progress-chart');
        if (!ctx) {
            console.error('Progress chart canvas not found.');
            return;
        }
    
        // Replace with actual data fetched from the backend
        const progressData = {
            labels: ['Courses Completed', 'Courses In Progress'],
            datasets: [{
                label: 'Progress',
                data: [5, 3], // Example data
                backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)']
            }]
        };
    
        new Chart(ctx, {
            type: 'bar',
            data: progressData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Function to handle logout
    function logoutUser() {
        localStorage.removeItem('token');
        window.location.href = 'index.html'; // Redirect to login page
    }
    
    // Function to initialize dashboard
    function initDashboard() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logoutUser);
        }
    
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'index.html'; // Redirect if no token is found
        } else {
            fetchRecommendedCourses(); // Fetch and display recommended courses
            displayProgress(); // Display progress chart
        }
    }
    
    // Initialize dashboard on page load
    document.addEventListener('DOMContentLoaded', initDashboard);
    