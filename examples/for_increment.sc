// Test increment/decrement in for loop
function main() {
    uint32 sum = 0;
    uint32 i;
    
    // Using ++ in for loop increment
    for (i = 0; i < 10; i++) {
        sum = sum + i;
    }
    
    return sum;  // 0+1+2+...+9 = 45
}
