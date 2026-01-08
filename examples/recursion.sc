// Deep recursion example - recursive factorial
function factorial_recursive(n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    return n * factorial_recursive(n - 1);
}

// Recursive Fibonacci
function fibonacci_recursive(n) {
    if (n == 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

function main() {
    uint32 fact5 = factorial_recursive(5);
    uint32 fib10 = fibonacci_recursive(10);
    return fact5 + fib10;  // 120 + 55 = 175
}
