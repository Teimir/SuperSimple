// Demonstrate prefix vs postfix increment/decrement behavior
// Note: Since these are statements (not expressions), both prefix and postfix
// have the same effect in this language. This test shows they both work.
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
    uint32 sum = a + b + c + d;  // 6 + 6 + 4 + 4 = 20
    
    return sum;
}
