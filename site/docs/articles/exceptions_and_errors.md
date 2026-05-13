


<article>

## Исключения и обработка ошибок

### Базовая обработка исключений

```csharp
try
{
    // Код, который может вызвать исключение
    int result = Divide(10, 0);
    Console.WriteLine($"Результат: {result}");
}
catch (DivideByZeroException ex)
{
    // Обработка конкретного типа исключения
    Console.WriteLine($"Ошибка деления на ноль: {ex.Message}");
}
catch (FormatException ex)
{
    Console.WriteLine($"Ошибка формата: {ex.Message}");
}
catch (Exception ex)
{
    // Обработка всех остальных исключений (ловить последним!)
    Console.WriteLine($"Непредвиденная ошибка: {ex.GetType().Name} - {ex.Message}");
}
finally
{
    // Выполняется ВСЕГДА, даже если было исключение
    Console.WriteLine("Очистка ресурсов...");
}

int Divide(int a, int b)
{
    return a / b;  // При b=0 бросит DivideByZeroException
}
```

### Создание пользовательских исключений

```csharp
// Кастомное исключение - наследуемся от Exception или более специфичного
public class InsufficientFundsException : Exception
{
    public decimal Balance { get; }
    public decimal Required { get; }
    
    public InsufficientFundsException(decimal balance, decimal required)
        : base($"Недостаточно средств. Баланс: {balance}, требуется: {required}")
    {
        Balance = balance;
        Required = required;
    }
    
    // Конструктор для сериализации (хорошая практика)
    protected InsufficientFundsException(
        System.Runtime.Serialization.SerializationInfo info,
        System.Runtime.Serialization.StreamingContext context)
        : base(info, context) { }
}

// Использование
public class BankAccount
{
    private decimal _balance;
    
    public void Withdraw(decimal amount)
    {
        if (amount < 0)
            throw new ArgumentException("Сумма не может быть отрицательной", nameof(amount));
            
        if (amount > _balance)
            throw new InsufficientFundsException(_balance, amount);
            
        _balance -= amount;
    }
}

// Обработка кастомного исключения
try
{
    var account = new BankAccount();
    account.Withdraw(1000);
}
catch (InsufficientFundsException ex)
{
    Console.WriteLine($"Не хватает {ex.Required - ex.Balance} руб.");
}
```

### Best practices работы с исключениями

```csharp
// ✅ ПРАВИЛЬНО: Ловить конкретные исключения
try
{
    var data = File.ReadAllText("config.json");
    var config = JsonConvert.DeserializeObject<Config>(data);
}
catch (FileNotFoundException)
{
    Console.WriteLine("Файл конфигурации не найден, использую настройки по умолчанию");
    UseDefaultConfig();
}
catch (JsonException ex)
{
    Logger.LogError($"Ошибка парсинга JSON: {ex.Message}");
    throw;  // Перебросить дальше, если не можем обработать
}

// ❌ НЕПРАВИЛЬНО: Пустой catch или ловля Exception без необходимости
try
{
    DoSomething();
}
catch
{
    // Тихое "проглатывание" ошибки - сложно отлаживать!
}

// ✅ Использование using для гарантированной очистки
using (var stream = new FileStream("data.txt", FileMode.Open))
{
    // Работа с файлом
}  // stream.Dispose() вызывается автоматически

// ✅ Throw с сохранением стека вызовов
try
{
    RiskyOperation();
}
catch (SpecificException ex)
{
    // Логирование
    Logger.Warn("Ошибка в RiskyOperation", ex);
    throw;  // Сохраняет оригинальный стек вызовов
    // throw ex;  // ❌ Сбрасывает стек! Использовать только если создаёте новое исключение
}

// ✅ Исключения для исключительных ситуаций, не для потока управления
// ❌ Плохо:
try
{
    int value = int.Parse(input);
}
catch
{
    value = 0;  // Ожидается, что ввод может быть некорректным
}

// ✅ Лучше:
if (int.TryParse(input, out int value))
{
    // Успех
}
else
{
    value = 0;  // Ожидаемый сценарий, не исключение
}
```

### Асинхронная обработка исключений

```csharp
// Обработка исключений в async/await
public async Task<User> GetUserAsync(int id)
{
    try
    {
        return await _httpClient.GetFromJsonAsync<User>($"/api/users/{id}");
    }
    catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
    {
        // Фильтр исключений (C# 6.0+): ловим только 404
        return null;
    }
    catch (HttpRequestException ex)
    {
        // Другие ошибки сети
        _logger.LogError(ex, "Ошибка загрузки пользователя {UserId}", id);
        throw;
    }
}

// AggregateException при работе с Task.WhenAll
public async Task ProcessAllAsync(IEnumerable<int> ids)
{
    var tasks = ids.Select(id => ProcessItemAsync(id));
    
    try
    {
        await Task.WhenAll(tasks);
    }
    catch (AggregateException ex)
    {
        foreach (var inner in ex.InnerExceptions)
        {
            _logger.LogError(inner, "Ошибка обработки элемента");
        }
    }
}
```

</article>
