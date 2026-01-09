// Test increment and decrement operators
function main() {
    uint32 x = 5;
    uint32 y = 10;
    
    // Test prefix increment
    ++x;
    
    // Test postfix increment
    y++;
    
    // Test prefix decrement
    --x;
    
    // Test postfix decrement
    y--;
    
    return x + y;  // (6-1) + (11-1) = 5 + 10 = 15
}
