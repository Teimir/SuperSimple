
function main() {
    int32 arr1[9] = {66, 121, 101, 32, 87, 111, 114, 108, 100};
    for (int32 i = 0; i < 9; i++){
      uart_write(arr1[i]);  
    }
    return 0;
}