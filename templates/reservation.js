// Date and Time Selection Logic
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker
    const dateInput = document.querySelector('input[type="date"]');
    const timeInput = document.querySelector('input[type="time"]');
    const today = new Date();
    
    if (dateInput) {
        // Set minimum date to today
        dateInput.min = today.toISOString().split('T')[0];
        dateInput.value = today.toISOString().split('T')[0];
        
        // Add change listener
        dateInput.addEventListener('change', function() {
            validateDateTime();
            checkAvailability();
        });
    }
    
    if (timeInput) {
        // Set business hours
        timeInput.min = '09:00';
        timeInput.max = '18:00';
        timeInput.value = '09:00';
        
        // Add change listener
        timeInput.addEventListener('change', validateDateTime);
    }
});

function validateDateTime() {
    const dateInput = document.querySelector('input[type="date"]');
    const timeInput = document.querySelector('input[type="time"]');
    
    if (!dateInput || !timeInput) return;
    
    const selectedDate = new Date(dateInput.value + 'T' + timeInput.value);
    const now = new Date();
    
    // Validate date is not in the past
    if (selectedDate < now) {
        alert('No se puede seleccionar una fecha y hora en el pasado');
        resetDateTime();
        return false;
    }
    
    // Validate business hours (9:00 - 18:00)
    const hour = selectedDate.getHours();
    if (hour < 9 || hour >= 18) {
        alert('El horario de atención es de 9:00 a 18:00');
        resetDateTime();
        return false;
    }
    
    // Validate weekends
    const day = selectedDate.getDay();
    if (day === 0) { // Sunday
        alert('No hay atención los domingos');
        resetDateTime();
        return false;
    }
    if (day === 6) { // Saturday
        if (hour >= 13) {
            alert('Los sábados solo hay atención hasta las 13:00');
            resetDateTime();
            return false;
        }
    }
    
    return true;
}

function resetDateTime() {
    const dateInput = document.querySelector('input[type="date"]');
    const timeInput = document.querySelector('input[type="time"]');
    
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    if (timeInput) {
        timeInput.value = '09:00';
    }
}

function checkAvailability() {
    const dateInput = document.querySelector('input[type="date"]');
    if (!dateInput?.value) return;
    
    fetch(`/management/reservations/get-time-slots/?date=${dateInput.value}`)
        .then(response => response.json())
        .then(data => {
            const timeInput = document.querySelector('input[type="time"]');
            if (!timeInput) return;
            
            // Disable time input if no slots available
            timeInput.disabled = data.slots.length === 0;
            
            if (data.slots.length === 0) {
                alert('No hay horarios disponibles para esta fecha');
                return;
            }
            
            // Update available times
            const availableTimes = data.slots
                .filter(slot => slot.available)
                .map(slot => slot.time);
            
            // If current selected time is not available, reset to first available time
            if (!availableTimes.includes(timeInput.value)) {
                timeInput.value = availableTimes[0] || '09:00';
            }
        })
        .catch(error => {
            console.error('Error checking availability:', error);
            alert('Error al verificar disponibilidad');
        });
}