#include "div_lib.sc"

function hello_world() {
    int32 arr1[9] = {66, 121, 101, 32, 87, 111, 114, 108, 100};
    for (int32 i = 0; i < 9; i++){
      uart_write(arr1[i]);  
    }
    return 0;
}


function main() {
    // Initialize UART (optional, but recommended)
    uart_set_baud(115200);
    
    hello_world();
    int32 arr1[12] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    int32 a = 123456789;
    
    // Handle sign
    uint32 is_negative = 0;
    if (a < 0) {
        is_negative = 1;
        arr1[0] = 45;  // '-' in ASCII
        a = -a;  // Make positive for processing
    } else {
        arr1[0] = 32;  // Space in ASCII (or could be omitted)
    }
    
    // Extract digits (right to left) and store in reverse
    uint32 digits[10];
    uint32 count = 0;
    uint32 num = a;
    
    if (num == 0) {
        digits[0] = 0;
        count = 1;
    } else {
        while (num > 0) {
            digits[count] = umod(num,10);
            count = count + 1;
            num = udiv(num,10);
        }
    }
    
    // Write digits to array (left to right)
    uint32 start_index = 0;
    if (is_negative) {
        start_index = 1;
    }
    
    uint32 i = count;
    uint32 j = start_index;
    
    while (i > 0) {
        i = i - 1;
        arr1[j] = 48 + digits[i];  // Convert to ASCII
        j = j + 1;
    }
    
    arr1[j] = 0;  // Null terminator
    
    // Output via UART
    uint32 len = count;
    if (is_negative) {
        len = count + 1;
    }
    for (int32 k = 0; k < len; k++) {
        uart_write(arr1[k]);
    }
    
    return 0;
}