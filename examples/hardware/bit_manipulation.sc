// Bit manipulation example

function main() {
    uint32 value = 0;
    
    // Set bits
    value = set_bit(value, 0);
    value = set_bit(value, 5);
    value = set_bit(value, 10);
    
    // Clear a bit
    value = clear_bit(value, 5);
    
    // Toggle a bit
    value = toggle_bit(value, 3);
    value = toggle_bit(value, 3);  // Toggle again (should clear it)
    
    // Get bit value
    uint32 bit0 = get_bit(value, 0);
    uint32 bit5 = get_bit(value, 5);
    uint32 bit10 = get_bit(value, 10);
    
    // Return sum: should be 2 (bit0=1, bit10=1)
    return bit0 + bit5 + bit10;
}
