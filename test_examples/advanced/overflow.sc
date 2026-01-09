// Test integer overflow/wrap-around behavior
function main() {
    uint32 max = 4294967295;  // Maximum uint32 value
    uint32 result1 = max + 1;  // Should wrap to 0
    uint32 result2 = 0 - 1;    // Should wrap to max
    
    // Verify wrap-around
    if (result1 == 0 && result2 == 4294967295) {
        return 1;  // Overflow works correctly
    }
    return 0;
}
