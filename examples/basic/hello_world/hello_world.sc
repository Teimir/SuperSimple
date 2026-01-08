// Hello World example - outputs "Hello World" to UART

function main() {
    // Output "Hello World" character by character using uart_write
    // H = 72, e = 101, l = 108, l = 108, o = 111
    // space = 32
    // W = 87, o = 111, r = 114, l = 108, d = 100
    
    uart_write(72);   // H
    uart_write(101);  // e
    uart_write(108);  // l
    uart_write(108);  // l
    uart_write(111);  // o
    uart_write(32);   // space
    uart_write(87);   // W
    uart_write(111);  // o
    uart_write(114);  // r
    uart_write(108);  // l
    uart_write(100);  // d
    
    return 0;
}