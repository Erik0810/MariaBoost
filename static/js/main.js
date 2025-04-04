document.addEventListener('DOMContentLoaded', function() {
    function updateWorkoutGif(completedCount) {
        const workoutGif = document.getElementById('workoutGif');
        let gifName = 'Workout_Zero.gif';
        if (completedCount >= 3) {
            gifName = 'Workout_Completed.gif';
        } else if (completedCount === 2) {
            gifName = 'Workout_Two.gif';
        } else if (completedCount === 1) {
            gifName = 'Workout_One.gif';
        }
        workoutGif.src = `/static/images/${gifName}`;
    }

    const daysContainer = document.querySelector('.days-container');
    const workoutButton = document.getElementById('workoutButton');
    const messageInput = document.getElementById('workoutMessage');
    const prizeBox = document.getElementById('prizeBox');
    const prizePopup = document.getElementById('prizePopup');
    const prizeImage = document.getElementById('prizeImage');
    const prizeName = document.getElementById('prizeName');
    const prizeDescription = document.getElementById('prizeDescription');
    const workoutPopup = document.getElementById('workoutPopup');
    const workoutMessage = document.getElementById('workoutMessageContent');
    
    let currentWorkouts = {};

    // Initialize donut chart
    const ctx = document.getElementById('workoutDonutChart').getContext('2d');
    const donutChart = createDonutChart(ctx);

    // Prize popup handling
    function showPrizePopup(prizeDetails) {
        prizeImage.src = prizeDetails.image;
        prizeName.textContent = prizeDetails.name;
        prizeDescription.textContent = prizeDetails.description;
        prizePopup.classList.add('active');
    }

    function hidePrizePopup() {
        prizePopup.classList.remove('active');
    }

    // Get today's date in YYYY-MM-DD format
    function getTodayString() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }

    prizePopup.addEventListener('click', function(e) {
        if (e.target === prizePopup) {
            hidePrizePopup();
        }
    });

    workoutPopup.addEventListener('click', function(e) {
        if (e.target === workoutPopup) {
            workoutPopup.classList.remove('active');
        }
    });

    prizeBox.addEventListener('click', function() {
        const completedWorkouts = Object.values(currentWorkouts)
            .filter(w => w.completed).length;
        
        if (completedWorkouts >= 3) {
            fetch(`/prize`)
                .then(response => response.json())
                .then(data => {
                    showPrizePopup(data);
                })
                .catch(error => console.error('Error fetching prize:', error));
        }
    });

    // Create day boxes based on server dates
    function createDayBoxes(dates, workoutsData) {
        console.log('Creating day boxes with workouts:', workoutsData);
        currentWorkouts = workoutsData;
        daysContainer.innerHTML = '';
        
        const todayStr = getTodayString();
        
        dates.forEach((dateStr) => {
            const date = new Date(dateStr + 'T00:00:00');  // Ensure consistent timezone
            const dayBox = document.createElement('div');
            dayBox.className = 'day-box';
            
            if (dateStr === todayStr) {
                dayBox.classList.add('current');
                console.log('Today is:', dateStr);
            }

            if (workoutsData[dateStr]?.completed) {
                dayBox.classList.add('checked');
                console.log(`Day ${dateStr} is checked`);
            }
            
            if (workoutsData[dateStr]?.message) {
                dayBox.classList.add('has-message');
                const dots = document.createElement('div');
                dots.className = 'message-dots';
                dots.innerHTML = '<span></span><span></span><span></span>';
                dayBox.appendChild(dots);
            }
            
            const dayName = document.createElement('div');
            dayName.className = 'day-name';
            dayName.textContent = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.getDay() === 0 ? 6 : date.getDay() - 1];
            
            const dayDate = document.createElement('div');
            dayDate.className = 'day-date';
            dayDate.textContent = date.getDate();
            
            const checkbox = document.createElement('div');
            checkbox.className = 'checkbox';
            
            dayBox.appendChild(dayName);
            dayBox.appendChild(dayDate);
            dayBox.appendChild(checkbox);
            daysContainer.appendChild(dayBox);
            
            // Add click handler for previous days
            if (dateStr !== todayStr) {
                dayBox.addEventListener('click', function() {
                    if (workoutsData[dateStr]?.message) {
                        workoutMessage.textContent = workoutsData[dateStr].message;
                        workoutPopup.classList.add('active');
                    }
                });
            }

            if (dateStr === todayStr && workoutsData[dateStr]?.message) {
                messageInput.value = workoutsData[dateStr].message;
            }
        });

        // Update donut chart with initial data
        updateDonutChart(donutChart, workoutsData);
        const completedCount = Object.values(workoutsData).filter(w => w.completed).length;
        console.log('Completed workouts count:', completedCount);
    }

    // Toggle today's workout
    function toggleTodayWorkout() {
        const todayStr = getTodayString();
        const workoutButton = document.getElementById('workoutButton');
            
        const dayBox = Array.from(daysContainer.children)
            .find(box => box.classList.contains('current'));
            
        if (dayBox) {
            const currentMessage = messageInput.value.trim();
            
            const isCompleted = !currentWorkouts[todayStr].completed;
            dayBox.classList.toggle('checked');
            if (isCompleted) {
                workoutButton.classList.add('completed');
                workoutButton.textContent = 'Lødde har trent😇';
            } else {
                workoutButton.classList.remove('completed');
                workoutButton.textContent = 'Registrer økt😈';
            }
            currentWorkouts[todayStr] = currentWorkouts[todayStr] || {};
            currentWorkouts[todayStr].completed = !currentWorkouts[todayStr].completed;
            currentWorkouts[todayStr].message = currentMessage;
            
            if (window.navigator && window.navigator.vibrate) {
                window.navigator.vibrate(50);
            }
            
            updateDonutChart(donutChart, currentWorkouts);
            const completedCount = Object.values(currentWorkouts).filter(w => w.completed).length;
            updateWorkoutGif(completedCount);
            checkPrizeReveal();
            
            fetch('/toggle_workout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: todayStr,
                    message: currentMessage
                })
            }).catch(error => {
                console.error('Error saving workout:', error);
                dayBox.classList.toggle('checked');
                currentWorkouts[todayStr].completed = !currentWorkouts[todayStr].completed;
                updateDonutChart(donutChart, currentWorkouts);
            });
        }
    }

    function checkPrizeReveal() {
        const completedWorkouts = Object.values(currentWorkouts)
            .filter(w => w.completed).length;
        
        if (completedWorkouts >= 3) {
            fetch(`/prize`)
                .then(response => response.json())
                .then(data => {
                    prizeBox.innerHTML = `<img src="${data.image}" alt="${data.name}">`;
                })
                .catch(() => {
                    prizeBox.textContent = "❓";
                });
        } else {
            prizeBox.textContent = "❓";
        }
    }

    // Update button state on load
    function updateButtonState(workouts) {
        const todayStr = getTodayString();
        const workoutButton = document.getElementById('workoutButton');
        if (workouts[todayStr]?.completed) {
            workoutButton.classList.add('completed');
            workoutButton.textContent = 'Lødde har trent😇';
        } else {
            workoutButton.classList.remove('completed');
            workoutButton.textContent = 'Registrer økt😈';
        }
    }

    // Load initial data
    fetch(`/workouts`)
        .then(response => response.json())
        .then(data => {
            console.log('Received workout data:', data);
            createDayBoxes(data.dates, data.workouts);
            updateButtonState(data.workouts);
            const completedCount = Object.values(data.workouts).filter(w => w.completed).length;
            updateWorkoutGif(completedCount);
            checkPrizeReveal();
        })
        .catch(error => {
            console.error('Error loading workouts:', error);
            createDayBoxes([], {});
        });

    // Event listeners
    workoutButton.addEventListener('click', toggleTodayWorkout);
    workoutButton.addEventListener('touchstart', function(e) {
        e.preventDefault();
        toggleTodayWorkout();
    });

    messageInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter' || e.keyCode === 13) {
            e.target.blur();
        }
    });
});
