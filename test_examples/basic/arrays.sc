// Comprehensive array examples
// Demonstrates array declaration, initialization, and access

function main() {
    // Example 1: Array declaration and manual initialization
    uint32 arr1[10];
    arr1[0] = 1;
    arr1[1] = 2;
    arr1[2] = 3;
    arr1[3] = 4;
    arr1[4] = 5;
    
    // Example 2: Array initialization with values
    uint32 arr2[5] = {10, 20, 30, 40, 50};
    
    // Example 3: Partial array initialization (remaining elements are zero)
    uint32 arr3[8] = {1, 2, 3};
    // arr3[0] = 1, arr3[1] = 2, arr3[2] = 3, arr3[3..7] = 0
    
    // Calculate sum of first array
    uint32 sum1 = 0;
    uint32 i = 0;
    while (i < 5) {
        sum1 = sum1 + arr1[i];
        i = i + 1;
    }
    
    // Calculate sum of second array
    uint32 sum2 = arr2[0] + arr2[1] + arr2[2] + arr2[3] + arr2[4];
    
    // Calculate sum of third array (first 5 elements)
    uint32 sum3 = arr3[0] + arr3[1] + arr3[2] + arr3[3] + arr3[4];
    
    // Return combined sum: 15 + 150 + 6 = 171
    return sum1 + sum2 + sum3;
}
