<article>

## Типы данных и переменные в C#

### Классификация типов данных

```csharp
// ЗНАЧЕНИЯ (значимые типы - хранятся в стеке)

// Целочисленные типы
sbyte small = -128;           // 1 байт, от -128 до 127
byte b = 255;                 // 1 байт, от 0 до 255
short s = 32767;              // 2 байта
ushort us = 65535;            // 2 байта
int i = 2_147_483_647;        // 4 байта (наиболее часто используется)
uint ui = 4_294_967_295;      // 4 байта
long l = 9_223_372_036_854_775_807L;  // 8 байт
ulong ul = 18_446_744_073_709_551_615UL; // 8 байт

// Типы с плавающей точкой
float f = 3.14f;              // 4 байта, ~7 знаков точности
double d = 3.14159265359;     // 8 байт, ~15-16 знаков
decimal m = 999.99m;          // 16 байт, ~28-29 знаков (для финансов!)

// Логический тип
bool isActive = true;

// Символьный тип
char grade = 'A';             // 2 байта, один символ Unicode

// ССЫЛОЧНЫЕ ТИПЫ (хранятся в куче)
string name = "C# Developer"; // Строка (неизменяемая!)
object obj = "Любое значение"; // Базовый тип для всех

// Специальные типы
var auto = "Вывод типа компилятором"; // var определяет тип автоматически
dynamic dyn = "Проверка типов в рантайме"; // динамическая типизация
```

### Константы и только для чтения
```csharp
class Constants
{
    // const - компилируется, значение должно быть известно на этапе компиляции
    public const double Pi = 3.14159;
    
    // readonly - вычисляется в рантайме, можно присвоить в конструкторе
    public readonly DateTime CreatedAt;
    
    public Constants()
    {
        CreatedAt = DateTime.Now;
    }
}
```

### Преобразование типов
```csharp
// Неявное преобразование (upcasting) - безопасно
int intVal = 100;
long longVal = intVal;  // автоматическое расширение

// Явное преобразование (downcasting) - возможна потеря данных
double doubleVal = 99.99;
int truncated = (int)doubleVal;  // 99 (дробная часть отбрасывается)

// Преобразование через Convert
string str = "123";
int number = Convert.ToInt32(str);

// Преобразование через Parse и TryParse
if (int.TryParse("456", out int result))
{
    Console.WriteLine($"Успех: {result}");
}

// Boxing и Unboxing
int value = 42;
object boxed = value;        // Boxing: значение -> объект
int unboxed = (int)boxed;    // Unboxing: объект -> значение
```

### Nullable типы
```csharp
// Типы значений могут быть null с помощью ?
int? nullableInt = null;
double? price = 19.99;

// Проверка и доступ к значению
if (nullableInt.HasValue)
{
    int val = nullableInt.Value;
}

// Оператор ?? (null-coalescing)
int result = nullableInt ?? 0;  // Если null, вернуть 0

// C# 8+: Nullable reference types
string? maybeNull = null;  // Может быть null
string notNull = "Всегда имеет значение";  // Не должен быть null
```

</article>
