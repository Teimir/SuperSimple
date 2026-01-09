function main() {
    int32 a = 76;
    int32 arr2[12];
    int32 arr1[9] = {66, 121, 101, 32, 87, 111, 114, 108, 100};
    for (int32 i = 0; i < 9; i++){
      uart_write(arr1[i]);  
    }

    int32 j = 0;
    while (a > 64){
      arr2[j] = a;
      j++;
      a--;
    }
    for (int32 i = 0; i < 12; i++){
      uart_write(arr2[i]);  
    }

    int32 arr1[9] = {66, 121, 101, 32, 87, 111, 114, 108, 100};
    for (int32 j = 0; j < 9; j++){
      uart_write(arr1[j]);  
    }
    return 0;
}