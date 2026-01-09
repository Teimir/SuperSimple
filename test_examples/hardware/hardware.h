// Hardware constants and definitions

// Register numbers
#define R0  0
#define R1  1
#define R2  2
#define R3  3
#define R4  4
#define R5  5
#define R6  6
#define R7  7
#define R8  8
#define R9  9
#define R10 10
#define R11 11
#define R12 12
#define R13 13
#define R14 14
#define R15 15
#define R16 16
#define R17 17
#define R18 18
#define R19 19
#define R20 20
#define R21 21
#define R22 22
#define R23 23
#define R24 24
#define R25 25
#define R26 26
#define R27 27
#define R28 28
#define R29 29
#define R30 30
#define R31 31

// GPIO constants
#define GPIO_INPUT  0
#define GPIO_OUTPUT 1
#define GPIO_PULLUP 0
#define GPIO_PULLDOWN 1
#define GPIO_NONE 2
#define GPIO_HIGH 1
#define GPIO_LOW 0

// UART constants
#define UART_STATUS_TX_READY 1
#define UART_STATUS_RX_READY 2
#define UART_BAUD_9600 9600
#define UART_BAUD_115200 115200

// Timer constants
#define TIMER_ONESHOT 0
#define TIMER_PERIODIC 1
#define TIMER_CONTINUOUS 2

// Memory addresses (example)
#define GPIO_BASE    0x10000000
#define UART_BASE    0x10001000
#define TIMER_BASE   0x10002000
