document.addEventListener('DOMContentLoaded', function() {
    const daysContainer = document.querySelector('.days-container');
    const workoutButton = document.getElementById('workoutButton');
    const messageInput = document.getElementById('workoutMessage');
    let currentWeek = getCurrentWeek();
    let workouts = {};

    // Initialize donut chart with mobile-optimized settings
    const ctx = document.getElementById('workoutDonutChart').getContext('2d');
    const donutChart = new Chart(ctx, {
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
                duration: 500
            }
        }
    });

    // Get dates for the current week
    function getWeekDates() {
        const now = new Date();
        const monday = new Date(now);
        monday.setDate(monday.getDate() - (monday.getDay() || 7) + 1);
        
        return Array.from({ length: 7 }, (_, i) => {
            const date = new Date(monday);
            date.setDate(monday.getDate() + i);
            return {
                day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
                date: date.getDate(),
                full: date,
                iso: date.toISOString().split('T')[0]
            };
        });
    }

    // Create day boxes
    function createDayBoxes() {
        daysContainer.innerHTML = '';
        const weekDates = getWeekDates();
        const today = new Date();
        const todayISO = today.toISOString().split('T')[0];
        
        weekDates.forEach((dateInfo) => {
            const dayBox = document.createElement('div');
            dayBox.className = 'day-box';
            
            if (dateInfo.iso === todayISO) {
                dayBox.classList.add('current');
            }

            if (workouts[dateInfo.iso]?.completed) {
                dayBox.classList.add('checked');
            }
            
            const dayName = document.createElement('div');
            dayName.className = 'day-name';
            dayName.textContent = dateInfo.day;
            
            const dayDate = document.createElement('div');
            dayDate.className = 'day-date';
            dayDate.textContent = dateInfo.date;
            
            const checkbox = document.createElement('div');
            checkbox.className = 'checkbox';
            
            dayBox.appendChild(dayName);
            dayBox.appendChild(dayDate);
            dayBox.appendChild(checkbox);
            daysContainer.appendChild(dayBox);

            // If it's today's box, show any existing message
            if (dateInfo.iso === todayISO && workouts[dateInfo.iso]?.message) {
                messageInput.value = workouts[dateInfo.iso].message;
            }
        });
    }

    // Toggle today's workout
    function toggleTodayWorkout() {
        const today = new Date();
        const todayISO = today.toISOString().split('T')[0];
        
        // Update UI first
        const weekDates = getWeekDates();
        const todayIndex = weekDates.findIndex(date => date.iso === todayISO);
        
        if (todayIndex !== -1) {
            const dayBox = daysContainer.children[todayIndex];
            const currentMessage = messageInput.value.trim();
            
            // Toggle the workout status
            dayBox.classList.toggle('checked');
            workouts[todayISO] = workouts[todayISO] || {};
            workouts[todayISO].completed = !workouts[todayISO].completed;
            workouts[todayISO].message = currentMessage;
            
            // Add haptic feedback
            if (window.navigator && window.navigator.vibrate) {
                window.navigator.vibrate(50);
            }
            
            // Update chart
            updateDonutChart();
            
            // Save to server
            fetch('/toggle_workout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: todayISO,
                    message: currentMessage
                })
            }).catch(error => {
                console.error('Error saving workout:', error);
                // Revert UI on error
                dayBox.classList.toggle('checked');
                workouts[todayISO].completed = !workouts[todayISO].completed;
                updateDonutChart();
            });
        }
    }

    // Update donut chart
    function updateDonutChart() {
        const completedWorkouts = Object.values(workouts)
            .filter(w => w.completed).length;
        donutChart.data.datasets[0].data = [completedWorkouts, 3 - completedWorkouts];
        donutChart.update('none');
    }

    // Get current week in YYYY-WW format
    function getCurrentWeek() {
        const now = new Date();
        const start = new Date(now.getFullYear(), 0, 1);
        const week = Math.ceil((((now - start) / 86400000) + start.getDay() + 1) / 7);
        return `${now.getFullYear()}-${week.toString().padStart(2, '0')}`;
    }

    // Load initial data
    fetch(`/workouts?week=${currentWeek}`)
        .then(response => response.json())
        .then(data => {
            workouts = data.workouts || {};
            createDayBoxes();
            updateDonutChart();
        })
        .catch(() => {
            createDayBoxes();
        });

    // Add workout button event listeners
    workoutButton.addEventListener('click', toggleTodayWorkout);
    workoutButton.addEventListener('touchstart', function(e) {
        e.preventDefault();
        toggleTodayWorkout();
    });

    // Handle message input on mobile
    messageInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            e.target.blur();
        }
    });
});
