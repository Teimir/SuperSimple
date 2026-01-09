// Пример вывода заранее заданного числа на UART
// Второй вариант: извлекает цифры из числа через цикл с использованием деления
// Использует функции деления и остатка, реализованные через вычитание

// Функция остатка от деления на 10
function mod_by_10(num) {
    uint32 remainder = num;
    while (remainder >= 10) {
        remainder = remainder - 10;
    }
    return remainder;
}

// Функция деления на 10 (оптимизированная версия с большими шагами)
function div_by_10(num) {
    if (num < 10) {
        return 0;
    }
    
    uint32 quotient = 0;
    uint32 temp = num;
    
    // Оптимизация: вычитаем большими шагами
    // Вычитаем по 10000 (для чисел >= 10000)
    while (temp >= 10000) {
        temp = temp - 10000;
        quotient = quotient + 1000;
    }
    // Вычитаем по 1000 (для чисел >= 1000)
    while (temp >= 1000) {
        temp = temp - 1000;
        quotient = quotient + 100;
    }
    // Вычитаем по 100 (для чисел >= 100)
    while (temp >= 100) {
        temp = temp - 100;
        quotient = quotient + 10;
    }
    // Вычитаем по 10 (для чисел >= 10)
    while (temp >= 10) {
        temp = temp - 10;
        quotient = quotient + 1;
    }
    
    return quotient;
}

function main() {
    // Инициализация UART
    uart_set_baud(115200);
    
    // Заранее заданное число для вывода
    uint32 number = 12345;
    
    // Массив для хранения цифр в обратном порядке
    uint32 digits[10];
    uint32 count = 0;
    uint32 num = number;
    
    // Извлекаем цифры справа налево через цикл с использованием деления
    if (num == 0) {
        digits[0] = 0;
        count = 1;
    } else {
        // Извлекаем цифры, строго ограничиваем до 10 цифр
        while (num > 0 && count < 10) {
            // Используем функцию mod_by_10 для получения остатка (num % 10)
            uint32 remainder = mod_by_10(num);
            digits[count] = remainder;
            count = count + 1;
            
            // Используем функцию div_by_10 для получения частного (num / 10)
            uint32 new_num = div_by_10(num);
            
            // Защита от бесконечного цикла: если число не уменьшилось, выходим
            if (new_num >= num) {
                break;
            }
            
            num = new_num;
        }
    }
    
    // Выводим цифры слева направо через UART в цикле
    // Цифры сохранены в обратном порядке (5, 4, 3, 2, 1), выводим с конца
    uint32 i = count;
    while (i > 0) {
        i = i - 1;
        // Преобразуем цифру в ASCII символ (48 = '0')
        uint32 digit = digits[i];
        uint32 ascii_digit = 48 + digit;
        uart_write(ascii_digit);
    }
    
    // Выводим символ новой строки для читаемости
    uart_write(10);  // '\n'
    uart_write(13);  // '\r'
    
    return 0;
}
