// Example demonstrating hexadecimal literal usage

function main() {
    // Basic hex literals
    uint32 hex_val = 0xFF;        // 255 in decimal
    uint32 bitmask = 0x0F;        // 15 in decimal (lower 4 bits)
    uint32 flags = 0x1234ABCD;    // 305441741 in decimal
    
    // Hex literals with uppercase prefix
    uint32 upper_hex = 0XFF;
    
    // Hex literals with mixed case
    uint32 mixed_case = 0xAbCd;   // 43981 in decimal
    
    // Hex literals in expressions
    uint32 result = hex_val & bitmask;  // 255 & 15 = 15
    result = 0x10 + 0x20;               // 16 + 32 = 48
    result = 0xFF | 0x00;               // 255 | 0 = 255
    result = 0xAA ^ 0x55;               // 170 ^ 85 = 255
    
    // Using hex in loops
    uint32 i;
    uint32 sum = 0;
    for (i = 0x00; i < 0x10; i++) {
        sum = sum + i;
    }
    // Sum of 0 + 1 + 2 + ... + 15 = 120
    
    // Boundary values
    uint32 zero = 0x0;
    uint32 max_val = 0xFFFFFFFF;  // Maximum uint32 value
    
    // Mixing hex and decimal
    uint32 mixed = 0xFF + 1;      // 255 + 1 = 256
    mixed = 16 + 0x10;            // 16 + 16 = 32
    
    return sum;  // returns 120
}
