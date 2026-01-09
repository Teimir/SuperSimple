function main() {
    // Test 1: Array access
    uint32 arr[5];
    uint32 x = arr[0];
    
    // Test 2: Address-of
    uint32 var = 10;
    uint32 y = &var;
    
    // Test 3: Dereference
    uint32 ptr = 1000;  // Address of 'var' (should be 1000 + 2 = 1002, but let's use 1000 for simplicity)
    // Actually, we need a valid address - let's use the address of var
    uint32 addr_var = &var;
    uint32 z = *addr_var;  // Dereference the address
    
    return 0;
}