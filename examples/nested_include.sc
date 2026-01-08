// Example with nested includes
#include "utils.sc"
#include "math_ops.sc"

function main() {
    uint32 x = 20;
    uint32 y = 5;
    
    uint32 sum = add(x, y);
    uint32 diff = subtract(x, y);
    uint32 prod = multiply(x, y);
    uint32 quot = divide(x, y);
    
    return sum + diff + prod + quot;  // 25 + 15 + 100 + 4 = 144
}
