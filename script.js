// Function to handle lab completion
document.querySelector('[aria-label="Mark as Complete"]').addEventListener('click', function() {
    const labId = 1; // Replace with actual lab ID if needed
    fetch('/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ lab_id: labId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Display the response message
    })
    .catch(error => console.error('Error:', error));
});
