<article>

## Методы: параметры, перегрузка и рекурсия

### Объявление и вызов методов

```csharp
// Базовый метод
public int Add(int a, int b)
{
    return a + b;
}

// Вызов
int result = Add(5, 3);  // 8

// Метод без возвращаемого значения
public void PrintMessage(string message)
{
    Console.WriteLine(message);
}

// Метод с несколькими return
public string GetGrade(int score)
{
    if (score >= 90) return "A";
    if (score >= 75) return "B";
    if (score >= 60) return "C";
    return "F";
}
```

### Параметры методов

```csharp
// Параметры по умолчанию
public void Connect(string host, int port = 80, bool ssl = false)
{
    Console.WriteLine($"{host}:{port}, SSL={ssl}");
}
Connect("example.com");              // example.com:80, SSL=False
Connect("api.com", 443, true);       // api.com:443, SSL=True

// Именованные аргументы
Connect(host: "test.com", ssl: true);  // test.com:80, SSL=True

// Передача по значению и по ссылке
void ModifyValue(int x) { x = 100; }  // копия, оригинал не изменится

void ModifyReference(ref int x) { x = 100; }  // работает с оригиналом
int num = 10;
ModifyReference(ref num);  // num = 100

// out-параметры (обязательное присваивание внутри метода)
bool TryParseInt(string input, out int result)
{
    return int.TryParse(input, out result);
}
if (TryParseInt("123", out int value))
{
    Console.WriteLine(value);  // 123
}

// params - переменное количество аргументов
public int Sum(params int[] numbers)
{
    int total = 0;
    foreach (int n in numbers) total += n;
    return total;
}
Sum(1, 2, 3);           // 6
Sum(new int[] {4, 5});  // 9
```

### Перегрузка методов

```csharp
public class Calculator
{
    // Перегрузка по количеству и типам параметров
    public int Add(int a, int b) => a + b;
    
    public double Add(double a, double b) => a + b;
    
    public int Add(int a, int b, int c) => a + b + c;
    
    public string Add(string a, string b) => a + b;  // конкатенация
    
    // НЕЛЬЗЯ перегружать только по типу возвращаемого значения!
    // public double Add(int a, int b) => a + b;  // ОШИБКА компиляции
}
```

### Рекурсия

```csharp
// Факториал: n! = n * (n-1)!
public long Factorial(int n)
{
    if (n <= 1) return 1;  // базовый случай
    return n * Factorial(n - 1);  // рекурсивный вызов
}

// Числа Фибоначчи (неэффективная рекурсия)
public long Fibonacci(int n)
{
    if (n <= 1) return n;
    return Fibonacci(n - 1) + Fibonacci(n - 2);
}

// Фибоначчи с мемоизацией (эффективно)
private Dictionary<int, long> _cache = new();
public long FibonacciMemo(int n)
{
    if (n <= 1) return n;
    if (_cache.ContainsKey(n)) return _cache[n];
    
    long result = FibonacciMemo(n - 1) + FibonacciMemo(n - 2);
    _cache[n] = result;
    return result;
}

// Обход файловой системы (рекурсивный)
public void PrintDirectory(string path, string indent = "")
{
    Console.WriteLine(indent + Path.GetFileName(path));
    
    if (Directory.Exists(path))
    {
        foreach (var subDir in Directory.GetDirectories(path))
        {
            PrintDirectory(subDir, indent + "  ");
        }
    }
}
```

### Локальные функции (C# 7.0+)

```csharp
public void ProcessData(int[] data)
{
    // Локальная функция видна только внутри ProcessData
    bool IsValid(int value) => value > 0 && value < 100;
    
    foreach (var item in data)
    {
        if (IsValid(item))
        {
            Console.WriteLine(item);
        }
    }
    
    // Можно вызывать рекурсивно
    void Helper(int step)
    {
        if (step <= 0) return;
        Console.WriteLine(step);
        Helper(step - 1);
    }
    Helper(3);  // 3, 2, 1
}
```

</article>