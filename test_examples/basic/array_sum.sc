// Example: Calculate sum of array elements using pointers
function main() {
    uint32 arr[8];
    
    // Initialize array with values 1 to 8
    uint32 i = 0;
    while (i < 8) {
        arr[i] = i + 1;
        i = i + 1;
    }
    
    // Calculate sum using pointer arithmetic
    uint32* ptr = &arr[0];
    uint32 sum = 0;
    i = 0;
    while (i < 8) {
        sum = sum + *ptr;
        ptr = ptr + 1;
        i = i + 1;
    }
    
    return sum;  // Returns 36 (1+2+3+4+5+6+7+8)
}
