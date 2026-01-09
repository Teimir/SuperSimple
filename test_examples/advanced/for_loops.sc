// For loops with increment and decrement
// Demonstrates different for loop patterns

function main() {
    uint32 sum1 = 0;
    uint32 sum2 = 0;
    uint32 i;
    uint32 j;
    uint32 count = 10;
    
    // Example 1: For loop with increment (i++)
    for (i = 0; i < 10; i++) {
        sum1 = sum1 + i;
    }
    // sum1 = 0+1+2+...+9 = 45
    
    // Example 2: For loop with decrement (j--)
    // Note: For unsigned integers, we use a counter to limit iterations
    for (j = 9; count > 0; j--) {
        sum2 = sum2 + j;
        count = count - 1;
    }
    // sum2 = 9+8+7+...+0 = 45
    
    return sum1 + sum2;  // 45 + 45 = 90
}
