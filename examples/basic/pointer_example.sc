// Example: Working with pointers
function main() {
    uint32 x = 42;
    uint32 y = 100;
    
    // Declare pointer
    uint32* ptr;
    
    // Point to x
    ptr = &x;
    uint32 val1 = *ptr;  // val1 = 42
    
    // Change value through pointer
    *ptr = 55;
    uint32 val2 = x;  // val2 = 55
    
    // Point to y
    ptr = &y;
    *ptr = 200;
    uint32 val3 = y;  // val3 = 200
    
    return val2 + val3;  // Returns 255 (55 + 200)
}
