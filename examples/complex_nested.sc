// Complex nested structures (nested loops, nested ifs, nested functions)
function nested_helper(x) {
    if (x > 0) {
        if (x < 10) {
            return x * 2;
        } else {
            return x + 10;
        }
    }
    return 0;
}

function main() {
    uint32 sum = 0;
    uint32 i;
    
    // Nested for loops with nested if statements
    for (i = 0; i < 3; i++) {
        uint32 j;
        for (j = 0; j < 2; j++) {
            if (i == 0) {
                if (j == 0) {
                    sum = sum + nested_helper(5);
                } else {
                    sum = sum + nested_helper(3);
                }
            } else {
                if (i == 1) {
                    sum = sum + nested_helper(2);
                } else {
                    sum = sum + nested_helper(1);
                }
            }
        }
    }
    
    return sum;
    // i=0, j=0: nested_helper(5) = 10
    // i=0, j=1: nested_helper(3) = 6
    // i=1, j=0: nested_helper(2) = 4
    // i=1, j=1: nested_helper(2) = 4
    // i=2, j=0: nested_helper(1) = 2
    // i=2, j=1: nested_helper(1) = 2
    // Total: 10 + 6 + 4 + 4 + 2 + 2 = 28
}
