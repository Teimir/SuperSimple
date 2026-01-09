# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Изменено
- Обновлена документация для соответствия текущей структуре проекта
- Удалены упоминания несуществующих директорий из документации
- Добавлена документация для директории `uart_number/`

### Добавлено
- `COMPILATION_INSTRUCTIONS.md` - инструкции по компиляции LaTeX документации
- `CHANGELOG.md` - журнал изменений проекта

## [Исторические изменения]

### Упрощение примеров

#### Объединены дублирующиеся примеры:
- `array_example.sc` + `array_init_example.sc` + `array_init_partial.sc` → `arrays.sc`
- `increment_test.sc` + `prefix_vs_postfix.sc` → `increment_decrement.sc`
- `for_increment.sc` + `for_decrement.sc` → `for_loops.sc`

#### Удалены избыточные примеры:
- Удален `test_example/test_example.sc` (дублировал hello_world)
- Удален `simple_return/simple_return.sc` (слишком простой)

**Результат:** Уменьшено количество примеров с 43 до 37 файлов

### Улучшение архитектуры массивов

- Массивы теперь размещаются в памяти (data section), а не в стеке
- r:30 используется только как указатель на программный стек для переменных
- Упрощена логика доступа к массивам
- Исправлена проблема с переопределением массивов

### Обновление документации

- Обновлен `test_examples/README.md` с актуальной структурой
- Добавлены примеры использования
- Улучшены описания примеров
- Обновлен `README.md` с актуальными примерами:
  - Заменены устаревшие примеры (`prefix_vs_postfix.sc`, `increment_test.sc` → `increment_decrement.sc`)
  - Заменены `for_increment.sc` и `for_decrement.sc` → `for_loops.sc`
  - Добавлена информация о массивах и указателях
  - Обновлена структура проекта
- Удалены упоминания пустых папок из структуры проекта

### Очистка структуры проекта

- Удалены пустые папки: `test_examples/simple_return/` и `test_examples/test_example/`
- Удален временный тестовый файл: `test/test_and_simple.sc`

### Очистка кода

- Удалена неиспользуемая переменная `next_memory_address`
- Исправлены типы для `array_addresses` (теперь `Dict[str, str]`)
- Упрощена логика работы с массивами
- Удалены все блоки `debug.log` из `interpreter.py`
- Удален неиспользуемый импорт `json`
- Код стал чище и быстрее (нет лишних операций записи в файл)

### Улучшение типизации

Добавлены type hints для всех методов генерации кода в `codegen.py`:
- `generate_function() -> None`
- `generate_statement() -> None`
- `generate_expression() -> int`
- `generate_var_decl() -> None`
- `generate_assignment() -> None`
- `generate_return() -> None`
- `generate_if() -> None`
- `generate_while() -> None`
- `generate_for() -> None`
- `generate_array_decl() -> None`
- `generate_pointer_decl() -> None`
- `generate_array_assignment() -> None`
- `generate_pointer_assignment() -> None`
- `generate_block() -> None`
- `generate_break() -> None`
- `generate_continue() -> None`
- И другие методы генерации выражений

### Улучшение обработки ошибок

Все сообщения об ошибках в `codegen.py` теперь содержат:
- Префикс "Code generation error:" для идентификации
- Контекст (имя функции, где произошла ошибка)
- Более информативные описания

Примеры улучшенных сообщений:
- `"Code generation error: Too many variables (register allocation failed for 'x' in function 'main')"`
- `"Code generation error: Unknown expression type 'CustomExpr' in function 'foo'"`
- `"Code generation error: Undefined variable 'y' in function 'bar'"`

### Улучшение docstrings

Добавлены подробные docstrings для основных методов генерации кода:
- `generate_literal()` - описание параметров и возвращаемого значения
- `generate_binary_op()` - список поддерживаемых операторов
- `generate_unary_op()` - список поддерживаемых операторов
- `generate_function_call()` - описание соглашения о вызовах
- `generate_hardware_function()` - список поддерживаемых аппаратных функций

## Метрики улучшений

- **Примеры:** 43 → 37 файлов (-14%)
- **Дубликаты:** 6 → 0 (-100%)
- **Избыточные:** 2 → 0 (-100%)
- **Пустые папки:** 2 → 0 (-100%)
- **Отладочный код:** Удалено ~50 строк debug.log записей
- **Type hints:** Добавлено для 20+ методов
- **Docstrings:** Улучшено для 10+ ключевых методов
- **Сообщения об ошибках:** Все содержат контекст и префикс
- **Читаемость:** Улучшена за счет объединения связанных примеров и улучшения документации
- **Поддерживаемость:** Улучшена за счет упрощения структуры, типизации и лучших сообщений об ошибках

## Типы изменений

- `Добавлено` - для новых функций
- `Изменено` - для изменений в существующей функциональности
- `Устарело` - для функций, которые скоро будут удалены
- `Удалено` - для удаленных функций
- `Исправлено` - для исправления ошибок
- `Безопасность` - в случае уязвимостей
