// Example: Passing pointers to functions
function set_value(uint32* ptr, uint32 value) {
    *ptr = value;
    return 0;
}

function swap(uint32* a, uint32* b) {
    uint32 temp = *a;
    *a = *b;
    *b = temp;
    return 0;
}

function main() {
    uint32 x = 10;
    uint32 y = 20;
    
    // Use set_value to modify x
    set_value(&x, 100);
    // x is now 100
    
    // Use swap to exchange x and y
    swap(&x, &y);
    // x is now 20, y is now 100
    
    return x + y;  // Returns 120 (20 + 100)
}
