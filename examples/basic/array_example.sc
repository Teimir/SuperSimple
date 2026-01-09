// Example: Working with arrays
function main() {
    uint32 arr[10];
    
    // Initialize array with values
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    arr[3] = 4;
    arr[4] = 5;
    
    // Calculate sum of first 5 elements
    uint32 sum = 0;
    uint32 i = 0;
    while (i < 5) {
        sum = sum + arr[i];
        i = i + 1;
    }
    
    return sum;  // Returns 15 (1+2+3+4+5)
}
