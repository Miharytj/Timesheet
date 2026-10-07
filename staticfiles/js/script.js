document.addEventListener("DOMContentLoaded", function() {
    // Sélection des éléments du DOM
    const prevWeekBtn = document.getElementById('prevWeek');
    const nextWeekBtn = document.getElementById('nextWeek');
    const currentWeekElem = document.getElementById('currentWeek');
    const daysContainer = document.getElementById('daysContainer');

    // Fonction pour charger la semaine suivante ou précédente
    function changeWeek(offset) {
        const currentWeek = currentWeekElem.textContent.trim();
        const newDate = new Date(currentWeek);
        
        // Calcul de la nouvelle semaine en fonction de l'offset (1 semaine avant ou après)
        newDate.setDate(newDate.getDate() + offset * 7);
        const newWeek = newDate.toISOString().split('T')[0];  // Format YYYY-MM-DD
        
        // Mise à jour de l'affichage de la semaine
        currentWeekElem.textContent = newWeek;
        
        // Rechargement dynamique des jours (exemple simple ici, vous devrez intégrer avec Django)
        loadWeek(newWeek);
    }

    // Fonction pour charger une nouvelle semaine
    function loadWeek(newWeek) {
        // Utilisation d'un appel AJAX pour récupérer les données de la nouvelle semaine
        fetch(`/get_week_schedule/${newWeek}/`)
            .then(response => response.json())
            .then(data => {
                updateCalendar(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des données de la semaine:', error);
            });
    }

    // Fonction pour mettre à jour l'affichage du calendrier
    function updateCalendar(data) {
        // Réinitialisation du conteneur des jours
        daysContainer.innerHTML = '';

        data.days.forEach(day => {
            const dayColumn = document.createElement('div');
            dayColumn.classList.add('day-column');

            const dayHeader = document.createElement('div');
            dayHeader.classList.add('day-header');
            dayHeader.textContent = `${day.date} ${day.name}`;

            dayColumn.appendChild(dayHeader);

            day.time_slots.forEach(slot => {
                const timeSlotDiv = document.createElement('div');
                timeSlotDiv.classList.add('time-slot');

                if (slot.event) {
                    const eventDiv = document.createElement('div');
                    eventDiv.classList.add('event');
                    eventDiv.textContent = slot.event.name;
                    timeSlotDiv.appendChild(eventDiv);
                }

                dayColumn.appendChild(timeSlotDiv);
            });

            daysContainer.appendChild(dayColumn);
        });
    }

    // Gestion des clics pour naviguer entre les semaines
    prevWeekBtn.addEventListener('click', () => changeWeek(-1));
    nextWeekBtn.addEventListener('click', () => changeWeek(1));

    // Charger la semaine initiale au chargement de la page
    loadWeek(currentWeekElem.textContent.trim());
});

// scripts.js
function addNotification(message) {
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    const newNotification = {
        id: Date.now(),
        message: message,
        isRead: false,
        timestamp: new Date().toISOString(),
    };
    notifications.push(newNotification);
    localStorage.setItem('notifications', JSON.stringify(notifications));
    updateNotificationBadge();
}

function updateNotificationBadge() {
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    const unreadCount = notifications.filter(n => !n.isRead).length;
    const badge = document.getElementById('notification-badge');

    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }
}