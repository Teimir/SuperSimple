#include "div_lib.sc"

function main() {
    uart_set_baud(115200);
    
    // Test simple division
    uint32 a = 123;
    uint32 digit = umod(a, 10);
    
    // Output result
    uart_write(48 + digit);  // Should output '3'
    
    return 0;
}
