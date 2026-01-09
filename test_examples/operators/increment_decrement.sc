// Increment and decrement operators
// Demonstrates prefix and postfix increment/decrement

function main() {
    uint32 a = 5;
    uint32 b = 5;
    uint32 c = 5;
    uint32 d = 5;
    
    // Prefix increment
    ++a;
    
    // Postfix increment
    b++;
    
    // Prefix decrement
    --c;
    
    // Postfix decrement
    d--;
    
    // Verify all operations worked
    // a = 6, b = 6, c = 4, d = 4
    uint32 sum = a + b + c + d;  // 6 + 6 + 4 + 4 = 20
    
    return sum;
}
