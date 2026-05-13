<article>

## Операторы и выражения в C#

### Арифметические операторы
```csharp
int a = 10, b = 3;

Console.WriteLine(a + b);   // 13  Сложение
Console.WriteLine(a - b);   // 7   Вычитание
Console.WriteLine(a * b);   // 30  Умножение
Console.WriteLine(a / b);   // 3   Целочисленное деление
Console.WriteLine(a % b);   // 1   Остаток от деления

double x = 10.0, y = 3.0;
Console.WriteLine(x / y);   // 3.333... Дробное деление

// Инкремент/декремент
int counter = 5;
Console.WriteLine(counter++);  // 5 (постфикс: сначала возврат, потом ++)
Console.WriteLine(counter);    // 6
Console.WriteLine(++counter);  // 7 (префикс: сначала ++, потом возврат)
```

### Операторы сравнения и логические
```csharp
int age = 25;

// Сравнение
bool isAdult = age >= 18;        // true
bool isTeen = age > 12 && age < 20;  // false (логическое И)
bool isChildOrSenior = age < 14 || age > 60;  // false (логическое ИЛИ)
bool notChild = !(age < 14);     // true (логическое НЕ)

// Проверка на равенство
string name1 = "Alice";
string name2 = "Alice";
Console.WriteLine(name1 == name2);  // true (для строк сравнивается значение)

// Операторы короткого замыкания
bool CheckA() { Console.WriteLine("A"); return true; }
bool CheckB() { Console.WriteLine("B"); return false; }

// && - если первое false, второе не выполняется
if (false && CheckA()) { }  // CheckA() не вызовется

// || - если первое true, второе не выполняется  
if (true || CheckB()) { }   // CheckB() не вызовется
```

### Операторы присваивания и тернарный оператор
```csharp
int score = 10;
score += 5;   // score = score + 5 → 15
score -= 3;   // 12
score *= 2;   // 24
score /= 4;   // 6
score %= 4;   // 2

// Тернарный оператор (условное выражение)
int grade = 85;
string result = grade >= 60 ? "Зачёт" : "Незачёт";
Console.WriteLine(result);  // "Зачёт"

// Вложенный тернарный оператор
string letterGrade = grade >= 90 ? "A" : 
                     grade >= 75 ? "B" : 
                     grade >= 60 ? "C" : "F";
```

### Операторы работы с битами
```csharp
byte flags = 0b_0000_1100;  // 12 в десятичной

// Побитовые операции
byte a = 0b_1100_1100;  // 204
byte b = 0b_1010_1010;  // 170

Console.WriteLine(Convert.ToString(a & b, 2));  // 10001010 (& - И)
Console.WriteLine(Convert.ToString(a | b, 2));  // 11101110 (| - ИЛИ)
Console.WriteLine(Convert.ToString(a ^ b, 2));  // 01100100 (^ - исключающее ИЛИ)
Console.WriteLine(Convert.ToString(~a, 2));     // 00110011 (~ - НЕ)

// Сдвиги
byte val = 0b_0000_1010;  // 10
Console.WriteLine(val << 2);  // 40 (сдвиг влево: 101000)
Console.WriteLine(val >> 1);  // 5  (сдвиг вправо: 101)
```

### Оператор is и as
```csharp
object obj = "Hello";

// Оператор is - проверка типа
if (obj is string str)
{
    Console.WriteLine($"Это строка: {str}");  // C# 7.0+: pattern matching
}

// Оператор as - безопасное приведение
string text = obj as string;
if (text != null)
{
    Console.WriteLine(text);
}

// Pattern matching (C# 8.0+)
object value = 42;
string description = value switch
{
    int i when i < 0 => "Отрицательное число",
    int i when i < 100 => "Положительное число < 100",
    string s => $"Строка: {s}",
    null => "null",
    _ => "Другой тип"
};
```

</article>
