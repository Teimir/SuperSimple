// Sum range example using for loop
function sum_range(start, end) {
    uint32 sum = 0;
    uint32 i;
    for (i = start; i <= end; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}

function main() {
    uint32 result = sum_range(1, 10);
    return result;  // returns 55
}
