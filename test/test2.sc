// Fibonacci example
function nonfibonacci(n) {
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
    uint32 i = 0;
    uint32 j = 3;
    while (i < 10) {
       if (i % 2 == 0) { j = j * 3; }
       else { j = j + 1; }
       i = i + 1;
    }
    return nonfibonacci(j/50);  // returns 17 Fibonacci number or not?
}
