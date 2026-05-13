
<article>

## Dependency Injection и современные возможности C#

### Основы Dependency Injection в ASP.NET Core

```csharp
// Интерфейс и реализация
public interface IEmailService
{
    Task SendEmailAsync(string to, string subject, string body);
}

public class SmtpEmailService : IEmailService
{
    private readonly IConfiguration _config;
    
    public SmtpEmailService(IConfiguration config)
    {
        _config = config;
    }
    
    public async Task SendEmailAsync(string to, string subject, string body)
    {
        // Реализация отправки через SMTP
    }
}

// Регистрация сервисов в Program.cs
builder.Services
    // Transient: новый экземпляр при каждом запросе
    .AddTransient<IEmailService, SmtpEmailService>()
    
    // Scoped: один экземпляр на запрос (для веб-приложений)
    .AddScoped<IUserRepository, UserRepository>()
    
    // Singleton: один экземпляр на всё время жизни приложения
    .AddSingleton<ICacheService, MemoryCacheService>();

// Внедрение через конструктор (рекомендуемый способ)
public class UserService
{
    private readonly IEmailService _email;
    private readonly IUserRepository _users;
    
    // Все зависимости объявляются в конструкторе
    public UserService(
        IEmailService email, 
        IUserRepository users)
    {
        _email = email;
        _users = users;
    }
    
    public async Task RegisterUserAsync(User user)
    {
        await _users.AddAsync(user);
        await _email.SendEmailAsync(user.Email, "Добро пожаловать!", "...");
    }
}
```

### Жизненные циклы сервисов

```csharp
// ⚠️ Важно: не внедрять Scoped в Singleton!
public class ProblematicService  // Singleton (по умолчанию для фоновых задач)
{
    // ❌ ОШИБКА: Scoped сервис в Singleton
    public ProblematicService(AppDbContext db) { }  // Db - Scoped!
}

// ✅ Решение: использовать IServiceScopeFactory
public class BackgroundProcessor
{
    private readonly IServiceScopeFactory _scopeFactory;
    
    public BackgroundProcessor(IServiceScopeFactory scopeFactory)
    {
        _scopeFactory = scopeFactory;
    }
    
    public async Task ProcessAsync()
    {
        // Создаём область для запроса
        using var scope = _scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        
        // Работа с контекстом БД
        await db.SaveChangesAsync();
    }
}

// Проверка времени жизни
public class LifetimeDemo
{
    private readonly Guid _id;
    
    public LifetimeDemo() => _id = Guid.NewGuid();
    
    public Guid Id => _id;
}

// Регистрация для демонстрации
services.AddTransient<LifetimeDemo>();  // Новый GUID каждый раз
services.AddScoped<LifetimeDemo>();     // Один GUID на запрос
services.AddSingleton<LifetimeDemo>();  // Один GUID на всё приложение
```

### Современные возможности C# 10-12

```csharp
// 🔹 Records (C# 9.0) - неизменяемые ссылочные типы
public record UserRecord(int Id, string Name, string Email);

var user1 = new UserRecord(1, "Alice", "a@test.com");
var user2 = user1 with { Email = "new@test.com" };  // Копия с изменением

// 🔹 Init-only свойства и required (C# 9.0)
public class Config
{
    public required string ApiKey { get; init; }
    public int Timeout { get; init; } = 30;
}

var cfg = new Config { ApiKey = "secret" };  // Timeout = 30 по умолчанию
// cfg.ApiKey = "new";  // ❌ Ошибка: init-свойства неизменяемы

// 🔹 Pattern matching улучшения (C# 10-12)
public string Describe(object obj) => obj switch
{
    null => "null",
    string s when s.Length == 0 => "пустая строка",
    string s => $"строка: {s}",
    int i when i < 0 => "отрицательное число",
    int i => $"число: {i}",
    List<int> { Count: > 0 } list => $"список из {list.Count} элементов",
    _ => "что-то другое"
};

// 🔹 Global using (C# 10)
// В одном файле: global using System; global using System.Linq;
// Доступно во всём проекте

// 🔹 File-scoped namespaces (C# 10)
namespace MyApp.Services;  // Вместо: namespace MyApp { ... }

// 🔹 Raw string literals (C# 11)
var json = """
    {
      "name": "Alice",
      "roles": ["admin", "user"]
    }
    """;

// 🔹 Collection expressions (C# 12)
int[] numbers = [1, 2, 3];  // Вместо: new int[] {1, 2, 3}
List<string> list = ["a", "b", "c"];
int[] combined = [..numbers, 4, 5];  // Spread-оператор

// 🔹 Primary constructors (C# 12)
public class UserService(AppDbContext db, IEmailService email)
{
    // Параметры конструктора доступны во всём классе
    public async Task NotifyAsync(User user)
    {
        await email.SendEmailAsync(user.Email, "Hi", "...");
        db.Users.Update(user);
        await db.SaveChangesAsync();
    }
}
```

### Лучшие практики и советы

```csharp
/*
✅ DI и архитектура:
• Внедряйте интерфейсы, а не реализации
• Используйте Scoped для DbContext в веб-приложениях
• Избегайте сервиса-бога: один класс = одна ответственность
• Используйте Options Pattern для конфигурации

✅ Асинхронность:
• Помечайте async все методы, которые вызывают await
• Возвращайте Task/Task<T>, а не void (кроме event handlers)
• Используйте ConfigureAwait(false) в библиотечном коде
• Не блокируйте асинхронные вызовы через .Result/.Wait()

✅ Производительность:
• Используйте AsNoTracking() для read-only запросов в EF
• Пагинация: .Skip().Take() вместо загрузки всех данных
• Кэширование частых запросов
• Используйте IAsyncEnumerable<T> для потоковой передачи больших данных

✅ Безопасность:
• Валидируйте все входные данные (Data Annotations / FluentValidation)
• Используйте параметризованные запросы (EF защищает от SQL-инъекций)
• Хэшируйте пароли (BCrypt, Argon2)
• Включайте HTTPS и CORS-политики

✅ Тестируемость:
• Внедряйте зависимости для мокирования в тестах
• Избегайте статических классов с состоянием
• Используйте интерфейсы для внешних сервисов (почта, БД, API)
*/
```

</article>
