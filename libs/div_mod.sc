// Функции целочисленного деления и вычисления остатка
// Простая реализация для беззнаковых чисел (uint32)

// Функция целочисленного деления
// Возвращает частное от деления dividend на divisor
function div(dividend, divisor) {
    // Обработка деления на ноль
    if (divisor == 0) {
        return 0;  // Деление на ноль - возвращаем 0 как индикатор ошибки
    }
    
    // Если делимое меньше делителя, результат равен 0
    if (dividend < divisor) {
        return 0;
    }
    
    // Оптимизация: деление на 1
    if (divisor == 1) {
        return dividend;
    }
    
    // Алгоритм последовательного вычитания
    // Вычитаем divisor из dividend до тех пор, пока dividend >= divisor
    uint32 quotient = 0;
    uint32 remainder = dividend;
    
    while (remainder >= divisor) {
        remainder = remainder - divisor;
        quotient = quotient + 1;
    }
    
    return quotient;
}

// Функция вычисления остатка от деления
// Возвращает остаток от деления dividend на divisor
function mod(dividend, divisor) {
    // Обработка деления на ноль
    if (divisor == 0) {
        return 0;  // Деление на ноль - возвращаем 0 как индикатор ошибки
    }
    
    // Если делимое меньше делителя, остаток равен делимому
    if (dividend < divisor) {
        return dividend;
    }
    
    // Оптимизация: деление на 1, остаток всегда 0
    if (divisor == 1) {
        return 0;
    }
    
    // Алгоритм последовательного вычитания
    // Вычитаем divisor из dividend до тех пор, пока dividend >= divisor
    // Остаток - это то, что осталось после всех вычитаний
    uint32 remainder = dividend;
    
    while (remainder >= divisor) {
        remainder = remainder - divisor;
    }
    
    return remainder;
}
