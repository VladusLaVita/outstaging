
<article>

## Делегаты, события и лямбда-выражения

### Делегаты: типы-ссылки на методы

```csharp
// Объявление делегата (сигнатура метода)
public delegate int MathOperation(int a, int b);

// Методы, соответствующие сигнатуре
public static int Add(int a, int b) => a + b;
public static int Multiply(int a, int b) => a * b;

// Использование делегата
MathOperation op = Add;  // Присваиваем метод
int result1 = op(5, 3);  // 8

op = Multiply;           // Меняем на другой метод
int result2 = op(5, 3);  // 15

// Делегаты с несколькими методами в цепочке (multicast)
public delegate void NotifyHandler(string message);

NotifyHandler notifier = ShowInConsole;
notifier += LogToFile;  // Добавляем второй метод
notifier += SendEmail;

notifier("Важное сообщение");  // Вызовутся ВСЕ три метода по очереди

notifier -= LogToFile;  // Убираем один метод

// Встроенные делегаты (не нужно объявлять свои)
Func<int, int, int> func = Add;  // Func<параметры, возвращаемый тип>
Action<string> action = Console.WriteLine;  // Action<параметры>, void возврат
Predicate<int> isPositive = x => x > 0;  // Predicate<T> возвращает bool
```

### Лямбда-выражения и замыкания

```csharp
// Лямбда: (параметры) => выражение/блок
Func<int, int> square = x => x * x;
Console.WriteLine(square(5));  // 25

// Лямбда с несколькими параметрами
Func<int, int, int> sum = (a, b) => a + b;

// Лямбда с блоком кода
Func<int, string> describe = (n) =>
{
    if (n > 0) return "положительное";
    if (n < 0) return "отрицательное";
    return "ноль";
};

// Замыкание: лямбда "запоминает" внешние переменные
public Func<int, int> CreateMultiplier(int factor)
{
    // factor "захватывается" замыканием
    return x => x * factor;
}

var doubleIt = CreateMultiplier(2);
var tripleIt = CreateMultiplier(3);

Console.WriteLine(doubleIt(5));  // 10
Console.WriteLine(tripleIt(5));  // 15

// Осторожно с изменяемыми переменными в циклах!
var actions = new List<Action>();
for (int i = 0; i < 3; i++)
{
    int captured = i;  // Создаём копию для замыкания
    actions.Add(() => Console.WriteLine(captured));
}
foreach (var action in actions) action();  // 0, 1, 2

// ❌ Без копии: все лямбды выведут 3 (последнее значение i)
```

### События: типобезопасные делегаты

```csharp
// Паттерн события с EventArgs
public class DownloadProgressEventArgs : EventArgs
{
    public int Percent { get; }
    public string FileName { get; }
    
    public DownloadProgressEventArgs(string fileName, int percent)
    {
        FileName = fileName;
        Percent = percent;
    }
}

public class Downloader
{
    // Объявление события (всегда с EventHandler или EventHandler<T>)
    public event EventHandler<DownloadProgressEventArgs> ProgressChanged;
    
    // Метод для "поднятия" события
    protected virtual void OnProgressChanged(DownloadProgressEventArgs e)
    {
        // Копия делегата для потокобезопасности (C# 6.0+ можно проще)
        ProgressChanged?.Invoke(this, e);
    }
    
    public async Task DownloadAsync(string url, string path)
    {
        // Эмуляция загрузки
        for (int i = 0; i <= 100; i += 10)
        {
            await Task.Delay(100);
            OnProgressChanged(new DownloadProgressEventArgs(path, i));
        }
    }
}

// Подписка на событие
var downloader = new Downloader();
downloader.ProgressChanged += (sender, args) =>
{
    Console.WriteLine($"{args.FileName}: {args.Percent}%");
};

// Отписка (важно для предотвращения утечек памяти!)
// downloader.ProgressChanged -= handler;

// Событие с синтаксисом C# 8.0+ (упрощённый)
public event Action<string, int> SimpleProgress;
SimpleProgress?.Invoke("file.zip", 50);
```

### Практическое применение: LINQ и делегаты

```csharp
var users = new List<User>
{
    new User("Alice", 25),
    new User("Bob", 30),
    new User("Charlie", 25)
};

// Делегаты в действии: предикаты, проекции, компараторы

// Where принимает Predicate<T> / Func<T, bool>
var adults = users.Where(u => u.Age >= 18);

// Select принимает Func<T, TResult>
var names = users.Select(u => u.Name);

// OrderBy принимает Func<T, TKey> и компаратор
var byName = users.OrderBy(u => u.Name);
var byAgeDesc = users.OrderByDescending(u => u.Age);

// Aggregate: свёртка коллекции
int totalAge = users.Aggregate(0, (sum, u) => sum + u.Age);

// Custom comparer через делегат
var sorted = users.OrderBy(u => u.Name, 
    Comparer<string>.Create((a, b) => a.Length.CompareTo(b.Length)));
```

</article>
