// Example: Arrays and pointers together
function main() {
    uint32 arr[5];
    
    // Initialize array
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    arr[3] = 40;
    arr[4] = 50;
    
    // Get pointer to first element
    uint32* ptr = &arr[0];
    
    // Access elements through pointer
    uint32 val1 = *ptr;      // val1 = 10
    ptr = ptr + 1;
    uint32 val2 = *ptr;      // val2 = 20
    ptr = ptr + 1;
    uint32 val3 = *ptr;      // val3 = 30
    
    // Access elements using array indexing
    uint32 val4 = arr[3];    // val4 = 40
    uint32 val5 = arr[4];    // val5 = 50
    
    // Calculate sum
    return val1 + val2 + val3 + val4 + val5;  // Returns 150
}
