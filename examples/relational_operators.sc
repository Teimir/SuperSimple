// All relational operators comprehensive test
function main() {
    uint32 count = 0;
    
    // Test less than (<)
    if (3 < 5) { count++; }   // true
    if (5 < 3) { count++; }   // false
    if (3 < 3) { count++; }   // false
    
    // Test less than or equal (<=)
    if (3 <= 5) { count++; }  // true
    if (3 <= 3) { count++; }  // true
    if (5 <= 3) { count++; }  // false
    
    // Test greater than (>)
    if (5 > 3) { count++; }   // true
    if (3 > 5) { count++; }   // false
    if (3 > 3) { count++; }   // false
    
    // Test greater than or equal (>=)
    if (5 >= 3) { count++; }  // true
    if (3 >= 3) { count++; }  // true
    if (3 >= 5) { count++; }  // false
    
    // Test equality (==)
    if (5 == 5) { count++; }  // true
    if (3 == 5) { count++; }  // false
    if (0 == 0) { count++; }  // true
    
    // Test inequality (!=)
    if (3 != 5) { count++; }  // true
    if (5 != 5) { count++; }  // false
    if (0 != 1) { count++; }  // true
    
    // Test with variables
    uint32 a = 10;
    uint32 b = 20;
    if (a < b) { count++; }   // true
    if (b > a) { count++; }   // true
    if (a == 10) { count++; } // true
    if (a != b) { count++; }  // true
    
    return count;  // Should be 14
}
