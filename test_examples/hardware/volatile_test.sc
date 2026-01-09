// Test volatile variables
function main() {
    volatile uint32 hardware_reg = 0;
    
    // Read from hardware register (simulated)
    uint32 value = hardware_reg;
    
    // Write to hardware register
    hardware_reg = 42;
    
    return hardware_reg;
}
