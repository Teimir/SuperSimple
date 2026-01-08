// Example demonstrating #include directive
#include "utils.sc"

function main() {
    uint32 a = 5;
    uint32 b = 3;
    uint32 sum = add(a, b);
    uint32 product = multiply(a, b);
    uint32 squared = square(a);
    
    return sum + product + squared;  // 8 + 15 + 25 = 48
}
