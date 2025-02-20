const API_BASE_URL = 'https://your-backend-api.com/api';

async function fetchAssignments() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('No token found. Please log in.');
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/assignments`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch assignments.');
        }

        const assignments = await response.json();
        displayAssignments(assignments);
    } catch (error) {
        console.error('Error fetching assignments:', error);
        alert(error.message);
    }
}

function displayAssignments(assignments) {
    const assignmentsContainer = document.getElementById('assignments-container');
    assignments.forEach(assignment => {
        const assignmentCard = document.createElement('div');
        assignmentCard.className = 'bg-[#f9fafb] p-6 rounded-lg shadow-md';
        assignmentCard.innerHTML = `
            <h4 class="text-xl font-semibold mb-2">${assignment.title}</h4>
            <p class="text-[#647987] mb-4">${assignment.description}</p>
        `;
        assignmentsContainer.appendChild(assignmentCard);
    });
}

document.addEventListener('DOMContentLoaded', fetchAssignments);
