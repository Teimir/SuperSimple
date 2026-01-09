// Пример вывода заранее заданного числа на UART
// Извлекает цифры из числа через цикл

function main() {
    // Инициализация UART
    uart_set_baud(115200);
    
    // Заранее заданное число для вывода
    uint32 number = 12345;
    
    // Массив степеней 10 для извлечения цифр
    uint32 powers[10] = {1000000000, 100000000, 10000000, 1000000, 100000, 10000, 1000, 100, 10, 1};
    
    // Флаг для пропуска ведущих нулей
    uint32 started = 0;
    
    // Извлекаем и выводим цифры слева направо через цикл
    uint32 i = 0;
    while (i < 10) {
        uint32 power = powers[i];
        uint32 digit = 0;
        
        // Вычисляем цифру через вычитание
        uint32 temp = number;
        while (temp >= power) {
            temp = temp - power;
            digit = digit + 1;
        }
        
        // Выводим цифру, если она не является ведущим нулем
        if (digit > 0 || started > 0 || i == 9) {
            started = 1;
            uint32 ascii_digit = 48 + digit;
            uart_write(ascii_digit);
        }
        
        // Убираем обработанную часть числа
        while (number >= power) {
            number = number - power;
        }
        
        i = i + 1;
    }
    
    // Выводим символ новой строки для читаемости
    uart_write(10);  // '\n'
    uart_write(13);  // '\r'
    
    return 0;
}
