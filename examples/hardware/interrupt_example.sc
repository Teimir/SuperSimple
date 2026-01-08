// Timer interrupt example
volatile uint32 counter = 0;

// Timer interrupt service routine
interrupt function timer_isr() {
    counter++;
    timer_reset();
}

function main() {
    // Configure timer
    timer_set_mode(1);  // TIMER_PERIODIC
    timer_set_period(1000000);  // 1 second
    timer_start();
    
    // Enable interrupts (simulated)
    enable_interrupts();
    
    // Main loop - counter would be updated by ISR
    // In simulation, we manually increment counter to simulate ISR
    uint32 iterations = 0;
    while (counter < 10 && iterations < 100) {  // Safety limit
        // Simulate ISR calling (in real hardware, ISR would fire automatically)
        if (timer_expired()) {
            counter++;
            timer_reset();
        }
        iterations++;  // Prevent infinite loop
    }
    
    disable_interrupts();
    timer_stop();
    return counter;
}
