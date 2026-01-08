function main() {
    for (uint32 i = 65; i < 127; i++){
    uart_write(i);   // B
    }
    return 0;
}