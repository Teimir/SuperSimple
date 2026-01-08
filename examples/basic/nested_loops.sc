// Nested loops example
function main() {
    uint32 result = 0;
    uint32 i;
    uint32 j;
    for (i = 0; i < 5; i = i + 1) {
        for (j = 0; j < 3; j = j + 1) {
            result = result + 1;
        }
    }
    return result;  // returns 15
}
