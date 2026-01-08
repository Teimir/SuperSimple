// Comprehensive logical operator tests
function main() {
    uint32 result = 0;
    
    // Test AND (&&)
    if (1 && 1) { result = result + 1; }  // true
    if (1 && 0) { result = result + 1; }  // false
    if (0 && 1) { result = result + 1; }  // false
    if (0 && 0) { result = result + 1; }  // false
    
    // Test OR (||)
    if (1 || 1) { result = result + 1; }  // true
    if (1 || 0) { result = result + 1; }  // true
    if (0 || 1) { result = result + 1; }  // true
    if (0 || 0) { result = result + 1; }  // false
    
    // Test NOT (!)
    if (!0) { result = result + 1; }      // true
    if (!1) { result = result + 1; }      // false
    if (!!1) { result = result + 1; }     // true (double negation)
    
    // Test complex logical expressions
    if (1 && 0 || 1) { result = result + 1; }  // true
    if (0 || 1 && 0) { result = result + 1; }  // false
    if (!0 && !0) { result = result + 1; }     // true
    
    return result;  // Should be 8: 1 + 3 + 2 + 2 = 8
}
