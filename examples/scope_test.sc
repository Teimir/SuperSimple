// Variable shadowing and scope testing
function test_scope(x) {
    uint32 x = 10;  // Shadow parameter
    {
        uint32 x = 20;  // Shadow outer x
        {
            uint32 x = 30;  // Shadow again
        }
        // x should be 20 again here
    }
    // x should be 10 here
    return x;
}

function main() {
    uint32 x = 5;
    uint32 result = test_scope(100);
    // x in main should still be 5
    return x + result;  // 5 + 10 = 15
}
