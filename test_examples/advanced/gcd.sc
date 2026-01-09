// Greatest Common Divisor using Euclidean algorithm
function gcd(a, b) {
    while (b != 0) {
        uint32 temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

function main() {
    uint32 a = 48;
    uint32 b = 18;
    return gcd(a, b);  // returns 6
}
