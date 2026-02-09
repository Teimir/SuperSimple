# Simple C-Style Language (SuperSimple)

Минимальный образовательный язык в стиле C с поддержкой 32-битных беззнаковых целых, функций, циклов, условий, массивов, указателей, директивы `#include` и аппаратных операций (GPIO, UART, таймер, прерывания).

---

## Содержание

- [Установка и требования](#установка-и-требования)
- [Использование: main.py и compile.py](#использование-mainpy-и-compilepy)
- [Таблица поддержки возможностей](#таблица-поддержки-возможностей)
- [Структура проекта](#структура-проекта)
- [Архитектура](#архитектура)
- [Спецификация языка](#спецификация-языка)
- [Директива #include](#директива-include)
- [Компиляция в ассемблер и бинарник](#компиляция-в-ассемблер-и-бинарник)
- [ISA и int_pack](#isa-и-int_pack)
- [Примеры](#примеры)
- [Тестирование](#тестирование)
- [Разработка и контрибьюция](#разработка-и-контрибьюция)
- [Ограничения](#ограничения)
- [История изменений](#история-изменений)
- [Лицензия](#лицензия)

---

## Установка и требования

- **Python 3.7+**
- Внешние зависимости не требуются.

---

## Использование: main.py и compile.py

### main.py — интерпретатор

Запускает программу на SuperSimple без компиляции: препроцессор → лексер → парсер → выполнение AST. Результат — значение, возвращаемое из `main()`.

**Синтаксис:**

```bash
python main.py <исходный_файл>
```

**Аргументы:**

| Аргумент | Описание |
|----------|----------|
| `исходный_файл` | Путь к файлу `.sc` (обязательный). Поддерживается `#include`. |

**Вывод:**

- В stdout выводится строка вида: `Program executed successfully. Return value: <значение>`.
- Ошибки препроцессора, лексера, парсера или времени выполнения выводятся в stderr; при первом встреченном блоке `asm { }` в stderr выводится предупреждение о том, что asm в интерпретаторе не поддерживается.

**Коды завершения:**

- `0` — успешное выполнение.
- `1` — ошибка (файл не найден, ошибка препроцессора/лексера/парсера/рантайма).

**Примеры:**

```bash
python main.py test_examples/basic/sum_range.sc
python main.py test_examples/basic/arrays.sc
python main.py test_examples/hardware/uart_echo.sc
```

---

### compile.py — компилятор

Компилирует исходный файл `.sc` в FASM-ассемблер (`.asm`), затем при наличии FASM.EXE — в бинарник (`.bin`) и при необходимости в `.mif` (Memory Initialization File для Quartus).

**Синтаксис:**

```bash
python compile.py <исходный_файл> [выходной_файл.asm] [--run]
```

**Аргументы:**

| Аргумент | Описание |
|----------|----------|
| `исходный_файл` | Путь к файлу `.sc` (обязательный). Поддерживается `#include`. |
| `выходной_файл.asm` | Опционально. Путь к результирующему `.asm`. По умолчанию — `<исходный_файл>.asm` (рядом с исходником). |
| `--run` | Опционально. После успешной компиляции запустить бинарник через `int_pack/interpreter_x64.exe`. |

**Порядок работы:**

1. Препроцессор обрабатывает `#include`.
2. Лексер и парсер строят AST.
3. Кодогенератор пишет FASM-код в указанный (или производный) `.asm`.
4. Если в каталоге проекта есть `int_pack/FASM.EXE`, вызывается FASM: из `.asm` получаются `.bin` и при необходимости `.mif` в том же каталоге, что и `.asm`.
5. При указании `--run` вызывается `int_pack/interpreter_x64.exe` с путём к `.bin`.

**Вывод:**

- В stdout: сообщения о создании `.asm`, об успешной компиляции FASM, путях к `.bin`/`.mif`; при `--run` — вывод запущенного бинарника (последние 150 строк при большом объёме).
- Ошибки выводятся в stderr; при отсутствии FASM.EXE бинарник не создаётся, но `.asm` уже записан.

**Примеры:**

```bash
# Только .asm
python compile.py test_examples/basic/sum_range.sc

# .asm в указанный файл
python compile.py test_examples/basic/sum_range.sc out/sum.asm

# Компиляция и запуск бинарника
python compile.py test_examples/basic/sum_range.sc --run
python compile.py test_examples/hardware/gpio_blink.sc --run
```

**Требования для бинарника и --run:** в корне проекта должны быть каталог `int_pack` с `FASM.EXE` и при использовании `--run` — `interpreter_x64.exe`. Подключение макросов и формата — через `int_pack/ISA.inc`.

---

## Таблица поддержки возможностей

Ниже указано, что **работает** в интерпретаторе (`main.py`) и в компиляторе (`compile.py`). «Не поддерживается» для компилятора означает, что вызов такой функции в коде приведёт к ошибке кодогенерации (Unknown hardware function и т.п.).

| Возможность | main.py (интерпретатор) | compile.py (компилятор → .asm/.bin) |
|-------------|-------------------------|-------------------------------------|
| **Язык** | | |
| Переменные, типы uint32/int32 | Да | Да |
| Массивы, указатели | Да | Да |
| Условия, циклы (if/while/do-while/for), break/continue | Да | Да |
| Функции, рекурсия | Да | Да |
| #include | Да | Да |
| register uint32 r0…r31 | Да | Да |
| volatile | Да | Да |
| interrupt function | Да | Да |
| asm { ... }; | Нет (предупреждение, блок игнорируется) | Да (вставка в .asm как есть) |
| **GPIO** | | |
| gpio_set, gpio_read, gpio_write | Да | Да |
| **UART** | | |
| uart_set_baud, uart_read, uart_write | Да | Да |
| uart_get_status | Да | Нет |
| **Таймер** | | |
| timer_set_mode, timer_set_period, timer_start, timer_stop, timer_reset, timer_get_value, timer_expired | Да | Нет |
| **Задержки** | | |
| delay_ms, delay_us, delay_cycles | Да (эмуляция) | Нет |
| **Прерывания** | | |
| enable_interrupts, disable_interrupts | Да | Нет |
| **Битовые операции (аппаратные)** | | |
| set_bit, clear_bit, toggle_bit, get_bit | Да | Нет |

Итог: в **main.py** доступны все перечисленные аппаратные функции и конструкции языка (кроме выполнения кода внутри `asm {}`). В **compile.py** генерируются только пользовательские функции и вызовы GPIO/UART (gpio_set/read/write, uart_set_baud/read/write); остальные аппаратные вызовы в компилируемой программе приведут к ошибке.

---

## Структура проекта

```
SuperSimple/
├── main.py              # Точка входа интерпретатора
├── lexer.py             # Токенизатор (исходный код → токены)
├── parser.py            # Парсер (токены → AST)
├── interpreter.py      # Интерпретатор (AST → выполнение)
├── preprocessor.py     # Препроцессор (#include)
├── codegen.py          # Генератор кода (AST → ассемблер)
├── compile.py          # Скрипт компиляции
├── emulator_main.py    # Точка входа эмулятора (если используется)
│
├── emulator/            # Эмулятор (core, decoder, executor, memory, peripherals, debugger)
├── self_tests/          # Юнит-тесты (test_lexer, test_parser, test_interpreter, test_preprocessor, test_emulator, run_tests)
├── test_examples/       # Примеры по категориям (basic, hardware, operators, includes, advanced, …)
├── libs/                # Библиотеки (.sc)
├── isa/                 # Описание ISA (README, ISA.xlsx)
└── int_pack/            # FASM (FASM.EXE), интерпретатор (interpreter_x64.exe), ISA.inc, макросы, заголовки
```

**Роль модулей:**

- **lexer.py** — разбивает исходный код на токены.
- **parser.py** — строит AST.
- **interpreter.py** — выполняет AST, управляет окружением и аппаратными функциями.
- **preprocessor.py** — обрабатывает `#include` до лексирования.
- **main.py** — цепочка: препроцессор → лексер → парсер → интерпретатор.

---

## Архитектура

**Цепочка обработки:**

```
Исходный файл (.sc)
    → Препроцессор (#include)
    → Лексер (токены)
    → Парсер (AST)
    → Интерпретатор (результат)
```

**Генерация кода (compile.py):** AST → кодогенератор → FASM (.asm) → FASM.EXE → .bin, .mif.

**Регистры (кодогенератор):** r0–r10 — временные; r11–r25 — локальные переменные; r26–r30 — параметры функций; r31 — указатель команд. r30 также используется как указатель стека для локальных переменных.

**Ошибки:** препроцессор (`PreprocessingError`), лексер (токен ERROR), парсер (`SyntaxError`), среда выполнения (`RuntimeError`).

---

## Спецификация языка

### Типы данных

- Единственный тип: **uint32** (0 … 2³²−1). Переполнение по модулю 2³².

### Лексика

- **Идентификаторы:** буква/подчёркивание, далее буквы, цифры, подчёркивание.
- **Литералы:** десятичные числа; шестнадцатеричные: `0x`, `0X` (например, `0xFF`, `0x1A2B`).
- **Ключевые слова:** `uint32`, `function`, `do`, `for`, `while`, `if`, `else`, `return`, `register`, `volatile`, `interrupt`, `asm`.
- **Операторы:** арифметика `+ - * / %`; сравнение `== != < <= > >=`; логика `&& || !`; побитовые `& | ^ ~ << >>`; присваивание `=`, `++`, `--` (префикс и постфикс).
- **Комментарии:** `//` и `/* */`.

### Синтаксис

- Программа — набор определений функций. Точка входа — `main()` без параметров.
- Переменные: `uint32 x;` или `uint32 y = 42;`.
- Функции: `function name(param1, param2) { ... return value; }`. Параметры и возврат — uint32.
- Управление: `if (cond) { }` / `if (cond) { } else { }`, `while (cond) { }`, `do { } while (cond);`, `for (init; cond; step) { }`.
- **Вставки ассемблера:** `asm { ... };` — содержимое блока вставляется в сгенерированный FASM-код как есть (макросы ISA.inc: `mov`, `add`, `r:0`…`r:31` и т.д.). В интерпретаторе блок `asm` не выполняется (no-op).
- Массивы: `uint32 arr[N];` или `uint32 arr[N] = { ... };`. Частичная инициализация — остальное нули.
- Указатели: объявление указателя, `&x`, `*ptr`, присваивание через `*ptr = value`, арифметика указателей.

### Аппаратная поддержка

- **Регистры:** `register uint32 r0` … `r31` (r31 только чтение).
- **GPIO:** `gpio_set`, `gpio_read`, `gpio_write`.
- **UART:** `uart_set_baud`, `uart_get_status`, `uart_read`, `uart_write`.
- **Таймер:** `timer_set_mode`, `timer_set_period`, `timer_start`, `timer_stop`, `timer_reset`, `timer_get_value`, `timer_expired`.
- **Прерывания:** `interrupt function`, `enable_interrupts`, `disable_interrupts`.
- **Биты:** `set_bit`, `clear_bit`, `toggle_bit`, `get_bit`.
- **Задержки:** `delay_ms`, `delay_us`, `delay_cycles`.

### Пример

```c
function add(uint32 a, uint32 b) {
    return a + b;
}

function main() {
    uint32 result = add(5, 3);
    return result;  // 8
}
```

---

## Директива #include

- Синтаксис: `#include "файл"` или `#include <файл>`.
- Обработка до лексирования: содержимое файла подставляется в текст.
- Порядок поиска: абсолютный путь → относительно текущего файла → относительно базовой директории → текущая рабочая директория.
- Вложенные `#include` обрабатываются рекурсивно.
- Циклические включения запрещены — ошибка препроцессора.
- Расширение файла не важно (.h, .sc и т.д.).
- **#define:** `#define ИМЯ значение` или `#define ИМЯ` (пустая подстановка). Имя — идентификатор (буква или `_`, далее буквы/цифры/`_`). Значение — остаток строки (опционально). Препроцессор подставляет значение вместо целых слов с именем макроса; вложенные макросы раскрываются повторно до стабилизации.
- **#undef:** `#undef ИМЯ` — снимает определение макроса; дальнейшие вхождения имени не подставляются. Ошибка при #undef несуществующего имени не выдаётся.

---

## Компиляция в ассемблер и бинарник

- **Регистры:** r0–r10 временные, r11–r25 локальные, r26–r30 параметры, r31 IP.
- **Соглашение вызовов:** до 5 параметров в r26–r30, возврат в r0.
- **Массивы:** глобальные — в секции данных; локальные — через стек (r30).
- **Указатели и память:** адрес через метки/смещения, загрузка/сохранение через `lds`.
- Условные переходы и циклы генерируются с использованием `cmovz`/меток и r31 где применимо.

Ручная сборка:

```bash
int_pack/FASM.EXE путь/к/файлу.asm
```

Запуск бинарника:

```bash
int_pack/interpreter_x64.exe путь/к/файлу.bin
```

---

## ISA и int_pack

- **isa/** — описание набора команд (документация, ISA.xlsx).
- **int_pack/** — FASM-транслятор, инструкции «как есть», макросы (в т.ч. `lds`, `entry`, `_push`/`_pop`, `ccall`). Регистр 31 — указатель команд; по адресу 0xFFFF:0xFFFE — 64-битный счётчик тиков (Little Endian).
- Инструкции: nop, hlt, setu/getu/inu/outu, setg/getg/ing/outg, inm/outm, mov, not, add, sub, and, or, xor, shr, shl, sar, sal, shrd, shld, ror, rol, cmpa, cmpe, cmpb, cmovnz, cmovz.
- Формат программы: `include "ISA.inc"` (или полный путь к ISA.inc), затем код. Для .mif используется fasm.exe; в пакете есть интерпретатор для .bin (UART эмулируется консолью, GPIO в интерпретаторе не поддерживаются).
- Заголовки: uio.inc (print, input), math.inc (umul, деление, _bsr).

Для компиляции интерпретатора из int_pack при необходимости подключается подмодуль.

---

## Примеры

Примеры в `test_examples/` по категориям:

| Категория    | Описание |
|-------------|----------|
| **basic/**  | sum_range.sc, nested_loops.sc, arrays.sc, pointer_example.sc, array_pointer.sc, pointer_function.sc, array_sum.sc, hello_world/ |
| **hardware/** | gpio_blink.sc, uart_echo.sc, timer_example.sc, interrupt_example.sc, bit_manipulation.sc, bit_test_simple.sc, volatile_test.sc, заголовки gpio.h, uart.h, timer.h, hardware.h |
| **operators/** | hex_literals.sc, relational_operators.sc, operator_precedence.sc, increment_decrement.sc |
| **includes/** | nested_include.sc, circular_a.sc, circular_b.sc, utils.sc, math_ops.sc |
| **advanced/** | fibonacci.sc, recursion.sc, gcd.sc, scope_test.sc, complex_nested.sc, overflow.sc, for_loops.sc |
| **complex_example/** | complex_example.sc |
| **math_test/** | test_div_simple.sc, test6.sc, div_lib.sc |
| **uart_message/** | test5.sc |
| **uart_number/** | uart_number.sc, uart_number_div.sc, t.sc, t2.sc и др. |

Запуск примеров:

```bash
python main.py test_examples/basic/sum_range.sc
python compile.py test_examples/hardware/gpio_blink.sc --run
```

---

## Тестирование

Запуск всех тестов:

```bash
python self_tests/run_tests.py
```

Отдельные наборы:

```bash
python -m unittest self_tests.test_lexer
python -m unittest self_tests.test_parser
python -m unittest self_tests.test_interpreter
python -m unittest self_tests.test_preprocessor
python -m unittest self_tests.test_emulator
```

Используется стандартный `unittest`, без внешних зависимостей.

---

## Разработка и контрибьюция

- Стиль кода: PEP 8, по возможности type hints и docstrings для классов и публичных методов.
- Добавление оператора: новый тип токена и распознавание в лексере → парсер (при необходимости приоритет) → интерпретатор (evaluate_binary_op/evaluate_unary_op) → тесты и обновление описания языка.
- Новая аппаратная функция: реализация в интерпретаторе, регистрация в `_register_hardware_functions()`, документация и пример в test_examples/hardware/.
- Новый тип оператора/инструкции: AST в parser, разбор в parse_statement → выполнение в interpreter → тесты.
- Коммиты: понятные сообщения; перед PR — прохождение тестов и актуализация документации.

---

## Ограничения

- Нет строк и символов, нет чисел с плавающей точкой.
- Единственный тип данных — uint32 (и int32 где реализовано).
- Деление на ноль — ошибка времени выполнения.
- Переполнение целых — по модулю 2³².
- Поддерживаются директивы препроцессора: `#include`, `#define`, `#undef` (без `#ifdef`/`#ifndef`).

---

## История изменений

- Документация сведена в один README; устаревшие упоминания структуры обновлены.
- Примеры упрощены: объединены дубликаты (массивы, инкремент/декремент, циклы for), удалены избыточные и пустые папки.
- Массивы размещаются в памяти (data section); r30 — указатель программного стека для переменных.
- Удалён отладочный код (debug.log), улучшены типизация и сообщения об ошибках в codegen; добавлены docstrings для ключевых методов генерации кода.

---

## Лицензия

Образовательный проект.
