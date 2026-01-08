// Fibonacci example
function fibonacci(n) {
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    uint32 a = 0;
    uint32 b = 1;
    uint32 i = 2;
    while (i <= n) {
        uint32 temp = a + b;
        a = b;
        b = temp;
        i = i + 1;
    }
    return b;
}

function main() {
    return fibonacci(10);  // returns 55
}
