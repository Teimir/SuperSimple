// Example: Partial array initialization
function main() {
    // Initialize array with fewer values than size
    // Remaining elements are zero-initialized
    uint32 arr[8] = {1, 2, 3};
    
    // arr[0] = 1, arr[1] = 2, arr[2] = 3, arr[3..7] = 0
    uint32 sum = arr[0] + arr[1] + arr[2] + arr[3] + arr[4];
    
    return sum;  // Returns 6 (1+2+3+0+0)
}
