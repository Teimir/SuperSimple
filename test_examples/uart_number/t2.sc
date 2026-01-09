uint32 aaaa = 0;

function divide(a,b){
    uint32 cnt = 0;
    while (a >= b) {
        cnt++;
        a = a - b;
    }
    return cnt;
}

function main() {
    // Инициализация UART
    uart_set_baud(115200);
    
    // Заранее заданное число для вывода
    uint32 number = 12345;
    
    uart_write(65);
    uart_write(10);  // '\n'

    // uint32 cnt = 0;
    // uint32 a = 10;
    // uint32 b = 5;
    // while (a >= b) {
    //     cnt++;
    //     a = a - b;
    // }
    aaaa = 2;
    
    for (uint32 i = 0; i < aaaa; i++){
        uart_write(65); 
        uart_write(10);  // '\n'
    }
    
    uart_write(65);
    uart_write(10);  // '\n'
    return divide(10,5);
}
