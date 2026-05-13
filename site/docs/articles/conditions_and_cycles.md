<article>

## Управляющие конструкции: условия и циклы

### Условные операторы

```csharp
// if-else if-else
int temperature = 25;

if (temperature < 0)
{
    Console.WriteLine("Замерзнешь!");
}
else if (temperature < 15)
{
    Console.WriteLine("Прохладно");
}
else if (temperature < 25)
{
    Console.WriteLine("Комфортно");
}
else
{
    Console.WriteLine("Тепло");
}

// switch выражение (современный синтаксис C# 8.0+)
string day = "Monday";
string message = day switch
{
    "Monday" => "Начало недели",
    "Friday" => "Почти выходные!",
    "Saturday" or "Sunday" => "Выходной!",
    _ => "Рабочий день"
};
Console.WriteLine(message);

// Классический switch с case
int option = 2;
switch (option)
{
    case 1:
        Console.WriteLine("Выбран пункт 1");
        break;  // обязательно!
    case 2:
        Console.WriteLine("Выбран пункт 2");
        break;
    case 3:
    case 4:  // "проваливание" к следующему case
        Console.WriteLine("Выбран 3 или 4");
        break;
    default:
        Console.WriteLine("Неизвестный выбор");
        break;
}
```

### Циклы

```csharp
// for - когда известно количество итераций
for (int i = 0; i < 5; i++)
{
    Console.WriteLine($"Итерация {i}");
}

// foreach - обход коллекций (только чтение в теле цикла)
string[] fruits = { "Яблоко", "Банан", "Апельсин" };
foreach (string fruit in fruits)
{
    Console.WriteLine(fruit);
}

// while - проверка условия перед итерацией
int count = 3;
while (count > 0)
{
    Console.WriteLine($"Обратный отсчёт: {count}");
    count--;
}

// do-while - проверка условия после итерации (выполнится минимум 1 раз)
int input;
do
{
    Console.Write("Введите положительное число: ");
    input = Convert.ToInt32(Console.ReadLine());
} while (input <= 0);

// Управление циклами: break, continue, goto
for (int i = 0; i < 10; i++)
{
    if (i == 3) continue;  // пропустить итерацию
    if (i == 7) break;     // выйти из цикла
    Console.WriteLine(i);  // выведет: 0,1,2,4,5,6
}
```

### Практические примеры

```csharp
// Пример 1: Поиск простого числа
bool IsPrime(int number)
{
    if (number < 2) return false;
    if (number == 2) return true;
    if (number % 2 == 0) return false;
    
    for (int i = 3; i * i <= number; i += 2)
    {
        if (number % i == 0) return false;
    }
    return true;
}

// Пример 2: Таблица умножения
for (int i = 1; i <= 10; i++)
{
    for (int j = 1; j <= 10; j++)
    {
        Console.Write($"{i * j,4}");
    }
    Console.WriteLine();
}

// Пример 3: Обработка пользовательского ввода с валидацией
string GetUserChoice(string[] options)
{
    while (true)
    {
        Console.WriteLine("Выберите опцию:");
        for (int i = 0; i < options.Length; i++)
        {
            Console.WriteLine($"{i + 1}. {options[i]}");
        }
        
        if (int.TryParse(Console.ReadLine(), out int choice) 
            && choice > 0 
            && choice <= options.Length)
        {
            return options[choice - 1];
        }
        Console.WriteLine("Неверный ввод, попробуйте снова.");
    }
}
```

</article>