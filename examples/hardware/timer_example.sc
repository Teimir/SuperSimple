// Timer example
// TIMER_PERIODIC = 1

function main() {
    // Configure timer for periodic mode
    timer_set_mode(1);  // TIMER_PERIODIC
    
    // Set period to 1 second (1000000 microseconds)
    timer_set_period(1000000);
    
    // Start timer
    timer_start();
    
    // Check timer (in real hardware, this would be done via interrupt)
    uint32 count = 0;
    uint32 iterations = 0;
    while (count < 5 && iterations < 100) {  // Safety limit
        if (timer_expired()) {
            count++;
            timer_reset();
        }
        iterations++;  // Prevent infinite loop
    }
    
    timer_stop();
    return count;  // Should return 5
}
