// Factorial example
function factorial(n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    uint32 result = 1;
    uint32 i = 2;
    while (i <= n) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

function main() {
    uint32 n = 5;
    uint32 fact = factorial(n);
    return fact;  // returns 120
}
