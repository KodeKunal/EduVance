const API_BASE_URL = 'https://your-backend-api.com/api'; // Replace with your actual API URL

async function fetchCourses() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('No token found. Please log in.');
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/courses`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch courses.');
        }

        const courses = await response.json();
        displayCourses(courses);
    } catch (error) {
        console.error('Error fetching courses:', error);
        alert(error.message);
    }
}

function displayCourses(courses) {
    const coursesContainer = document.getElementById('courses-container');
    coursesContainer.innerHTML = ''; // Clear existing content

    courses.forEach(course => {
        const courseCard = document.createElement('div');
        courseCard.className = 'bg-[#f9fafb] p-6 rounded-lg shadow-md transition duration-200 hover:shadow-lg';

        courseCard.innerHTML = `
            <img src="${course.image}" alt="${course.title}" class="w-full h-32 object-cover rounded-t-lg mb-4">
            <div class="flex justify-between items-center mb-2">
                <h4 class="text-xl font-semibold">${course.title}</h4>
                <span class="bg-blue-200 text-blue-800 text-xs font-bold px-2 py-1 rounded">${course.difficulty}</span>
            </div>
            <p class="text-[#647987] mb-4">${course.description}</p>
            <div class="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div class="bg-blue-600 h-2 rounded-full" style="width: ${course.completionPercentage}%"></div>
            </div>
            <a href="course.html?id=${course.id}" class="text-blue-500 hover:underline">View Course</a>
        `;

        coursesContainer.appendChild(courseCard);
    });
}

document.addEventListener('DOMContentLoaded', fetchCourses);
