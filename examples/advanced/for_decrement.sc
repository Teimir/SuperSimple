// Test decrement in for loop
function main() {
    uint32 sum = 0;
    uint32 i;
    uint32 count = 10;  // Count from 9 down to 0 (10 iterations)
    
    // Using -- in for loop increment
    // Important: For unsigned integers, "i >= 0" is always true because
    // when i is 0 and we do i--, it wraps to 4294967295 (max uint32).
    // So we use a counter to limit iterations instead.
    for (i = 9; count > 0; i--) {
        sum = sum + i;
        count = count - 1;
    }
    
    return sum;  // 9+8+7+...+0 = 45
}
