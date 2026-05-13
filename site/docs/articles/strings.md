<article>

## Строки и работа с текстом в C#

### Основы работы со строками

```csharp
// Строки неизменяемы (immutable)
string s1 = "Hello";
string s2 = s1 + " World";  // Создаётся НОВАЯ строка
Console.WriteLine(s1);  // "Hello" (не изменилась!)

// Сравнение строк
string a = "Test";
string b = "test";

Console.WriteLine(a == b);              // False (регистрозависимое)
Console.WriteLine(a.Equals(b));         // False
Console.WriteLine(a.Equals(b, StringComparison.OrdinalIgnoreCase));  // True

// Сравнение по порядку (лексикографическое)
Console.WriteLine(string.Compare("apple", "banana"));  // -1 (apple < banana)
```

### Методы строк

```csharp
string text = "  Hello, C# Developer!  ";

// Пробелы и регистр
Console.WriteLine(text.Trim());           // "Hello, C# Developer!"
Console.WriteLine(text.ToLower());        // "  hello, c# developer!  "
Console.WriteLine(text.ToUpper());        // "  HELLO, C# DEVELOPER!  "

// Поиск и проверка
Console.WriteLine(text.Contains("C#"));        // True
Console.WriteLine(text.StartsWith("  Hello")); // True
Console.WriteLine(text.EndsWith("!  "));       // True
Console.WriteLine(text.IndexOf("C#"));         // Позиция первого вхождения

// Замена и разделение
string modified = text.Replace("C#", ".NET");  // "  Hello, .NET Developer!  "
string[] words = "apple,banana,cherry".Split(',');  // ["apple", "banana", "cherry"]

// Подстроки
string substring = text.Substring(2, 5);  // "Hello" (начиная с позиции 2, длина 5)

// Форматирование
string name = "Alice";
int age = 30;

// String interpolation (C# 6.0+)
Console.WriteLine($"{name} is {age} years old");

// String.Format
Console.WriteLine("{0} is {1} years old", name, age);

// Выравнивание и форматирование чисел
double price = 1234.567;
Console.WriteLine($"Цена: {price,10:F2}");  // "Цена:    1234.57" (10 символов, 2 знака после запятой)
Console.WriteLine($"Процент: {0.856789:P1}");  // "85.7%" (P = Percent, 1 знак)
```

### StringBuilder для эффективной работы

```csharp
using System.Text;

// НЕЭФФЕКТИВНО: множество аллокаций памяти
string result = "";
for (int i = 0; i < 1000; i++)
{
    result += i + ",";  // Создаётся новая строка на каждой итерации!
}

// ЭФФЕКТИВНО: StringBuilder изменяется "на месте"
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++)
{
    sb.Append(i).Append(",");
}
string efficientResult = sb.ToString();

// Основные методы StringBuilder
sb.Clear();                    // Очистить
sb.Append("Текст");           // Добавить
sb.AppendLine(" с переносом"); // Добавить с \n
sb.AppendFormat("Число: {0}", 42);  // Форматирование
sb.Insert(0, "В начало ");    // Вставить по позиции
sb.Remove(0, 3);              // Удалить диапазон
sb.Replace("Текст", "Замена"); // Заменить подстроку
```

### Регулярные выражения

```csharp
using System.Text.RegularExpressions;

// Простая валидация email
string email = "user@example.com";
string pattern = @"^[^@\s]+@[^@\s]+\.[^@\s]+$";
bool isValid = Regex.IsMatch(email, pattern);

// Извлечение данных
string text = "Заказ №12345 от 2024-01-15 на сумму 999.99 руб.";
var match = Regex.Match(text, @"№(\d+).*(\d{4}-\d{2}-\d{2}).*([\d.]+)");

if (match.Success)
{
    string orderNum = match.Groups[1].Value;  // "12345"
    string date = match.Groups[2].Value;       // "2024-01-15"
    decimal amount = decimal.Parse(match.Groups[3].Value);  // 999.99
}

// Замена по шаблону
string phone = "+7 (999) 123-45-67";
string cleaned = Regex.Replace(phone, @"[^\d+]", "");  // "+79991234567"

// Разделение по нескольким разделителям
string[] tokens = Regex.Split("apple, banana;cherry|date", @"[,\s;|]+");
// ["apple", "banana", "cherry", "date"]
```

### Работа с кодировками и культурой

```csharp
using System.Globalization;

// Культура влияет на форматирование
double number = 1234.56;

Console.WriteLine(number.ToString("N", new CultureInfo("en-US")));  // "1,234.56"
Console.WriteLine(number.ToString("N", new CultureInfo("ru-RU")));  // "1 234,56"

// DateTime с культурой
DateTime now = DateTime.Now;
Console.WriteLine(now.ToString("D", new CultureInfo("ru-RU")));  // "28 апреля 2026 г."

// Кодировки при работе с файлами
string content = File.ReadAllText("file.txt", Encoding.UTF8);
File.WriteAllText("output.txt", content, Encoding.UTF8);
```

</article>
