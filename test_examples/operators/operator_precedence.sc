// Complex expressions testing operator precedence
function main() {
    // Test arithmetic precedence: * and / before + and -
    uint32 result1 = 2 + 3 * 4;        // Should be 2 + 12 = 14
    uint32 result2 = 10 - 4 / 2;       // Should be 10 - 2 = 8
    uint32 result3 = 2 * 3 + 4 * 5;    // Should be 6 + 20 = 26
    
    // Test parentheses
    uint32 result4 = (2 + 3) * 4;      // Should be 5 * 4 = 20
    uint32 result5 = 2 * (3 + 4);      // Should be 2 * 7 = 14
    
    // Test relational and logical operators
    uint32 result6 = 1 + 2 < 3 + 4;    // Should be 3 < 7 = 1 (true)
    uint32 result7 = 5 > 3 && 2 < 4;   // Should be 1 && 1 = 1 (true)
    uint32 result8 = 1 || 0 && 1;      // Should be 1 || 0 = 1 (true)
    
    // Combine everything
    return result1 + result2 + result3 + result4 + result5 + result6 + result7 + result8;
    // 14 + 8 + 26 + 20 + 14 + 1 + 1 + 1 = 85
}
