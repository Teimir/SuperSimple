// UART Echo example
// UART_STATUS_RX_READY = 2

function main() {
    // Set UART baud rate to 115200
    uart_set_baud(115200);
    
    uint32 i;
    // Simulate receiving some data
    for (i = 0; i < 5; i++) {
        // Check if data available (in real hardware, this would be non-blocking)
        uint32 status = uart_get_status();
        if (status & 2) {  // UART_STATUS_RX_READY
            uint32 data = uart_read();
            uart_write(data);  // Echo back
        }
    }
    
    return 0;
}
