// GPIO Blink LED example
// GPIO constants
// GPIO_OUTPUT = 1, GPIO_NONE = 2, GPIO_HIGH = 1, GPIO_LOW = 0

function main() {
    // Configure pin 0 as output
    gpio_set(0, 1, 2);  // pin 0, OUTPUT, NONE
    
    uint32 i;
    for (i = 0; i < 10; i++) {
        // Turn LED on
        gpio_write(0, 1);  // GPIO_HIGH
        
        // Turn LED off
        gpio_write(0, 0);  // GPIO_LOW
    }
    
    return 0;
}
