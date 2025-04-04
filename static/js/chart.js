function createDonutChart(ctx) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Remaining'],
            datasets: [{
                data: [0, 3],
                backgroundColor: [
                    '#4C6B4C', // Dark Green
                    '#F4D3D8'  // Pastel Pink
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '70%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            animation: {
                duration: 800,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateDonutChart(chart, workoutsData) {
    // Count completed workouts from the workouts data object
    const completedWorkouts = Object.values(workoutsData)
        .filter(workout => workout.completed).length;
    
    // Update completed workouts text
    document.getElementById('completedWorkouts').textContent = completedWorkouts;
    
    // Animate to new values
    const currentCompleted = chart.data.datasets[0].data[0];
    const targetCompleted = completedWorkouts;
    
    // Create animation frames
    let startTime = null;
    const duration = 800; // Match the chart animation duration
    
    function animate(currentTime) {
        if (!startTime) startTime = currentTime;
        const progress = Math.min(1, (currentTime - startTime) / duration);
        
        // Easing function (easeInOutQuart)
        const eased = progress < 0.5
            ? 8 * progress * progress * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 4) / 2;
        
        // Calculate current value
        const current = currentCompleted + (targetCompleted - currentCompleted) * eased;
        
        // Update chart
        chart.data.datasets[0].data = [current, 3 - current];
        chart.update('none');
        
        // Continue animation if not complete
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}