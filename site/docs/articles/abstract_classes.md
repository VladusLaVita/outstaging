

<article>

## Абстрактные классы и интерфейсы

### Интерфейсы: контракт без реализации

```csharp
// Интерфейс определяет ЧТО должно делать, но не КАК
public interface ILogger
{
    // Только объявления (по умолчанию public abstract)
    void Log(string message);
    void LogError(Exception ex);
    
    // Свойства
    LogLevel Level { get; set; }
    
    // Методы с реализацией по умолчанию (C# 8.0+)
    void LogWarning(string msg) => Log($"[WARN] {msg}");
}

public enum LogLevel { Debug, Info, Warning, Error }

// Реализация интерфейса
public class ConsoleLogger : ILogger
{
    public LogLevel Level { get; set; } = LogLevel.Info;
    
    public void Log(string message)
    {
        if (Level <= LogLevel.Info)
            Console.WriteLine($"[LOG] {message}");
    }
    
    public void LogError(Exception ex)
    {
        if (Level <= LogLevel.Error)
            Console.WriteLine($"[ERROR] {ex.Message}");
    }
}

// Другая реализация - тот же интерфейс, другое поведение
public class FileLogger : ILogger
{
    private string _filePath;
    public LogLevel Level { get; set; }
    
    public FileLogger(string path) => _filePath = path;
    
    public void Log(string message)
    {
        File.AppendAllText(_filePath, $"[LOG] {message}\n");
    }
    
    public void LogError(Exception ex)
    {
        File.AppendAllText(_filePath, $"[ERROR] {ex}\n");
    }
}
```

### Множественная реализация интерфейсов

```csharp
public interface ISaveable
{
    bool Save();
}

public interface ILoadable
{
    bool Load(string id);
}

// Класс может реализовывать несколько интерфейсов
public class Document : ISaveable, ILoadable
{
    public string Content { get; set; }
    
    public bool Save()
    {
        // Сохранение на диск
        return true;
    }
    
    public bool Load(string id)
    {
        // Загрузка по ID
        return true;
    }
}

// Явная реализация интерфейса (когда имена методов конфликтуют)
public class AdvancedDoc : ISaveable, ILoadable
{
    // Явная реализация: доступен только через интерфейс
    bool ISaveable.Save()
    {
        Console.WriteLine("Сохраняю как ISaveable");
        return true;
    }
    
    // Обычная реализация
    public bool Load(string id) => true;
}

// Использование явной реализации
AdvancedDoc doc = new AdvancedDoc();
// doc.Save();  // ОШИБКА: метод не виден
((ISaveable)doc).Save();  // OK: приведение к интерфейсу
```

### Абстрактный класс против интерфейса

```csharp
/*
КОГДА использовать абстрактный класс:
✓ Есть общая реализация для наследников
✓ Нужно хранить состояние (поля)
✓ Планируется эволюция базового функционала
✓ Отношение "является" (is-a)

КОГДА использовать интерфейс:
✓ Нужен контракт для НЕ связанных классов
✓ Требуется множественное "наследование"
✓ Важно разделение абстракции и реализации
✓ Отношение "может делать" (can-do)

ПРИМЕР: Система уведомлений
*/

// Интерфейс - контракт отправки
public interface INotificationSender
{
    Task<bool> SendAsync(string recipient, string message);
}

// Абстрактный класс - общая логика
public abstract class NotificationService
{
    protected INotificationSender _sender;
    
    protected NotificationService(INotificationSender sender)
    {
        _sender = sender;
    }
    
    // Шаблонный метод (Template Method)
    public async Task<bool> NotifyAsync(User user, string template)
    {
        var message = BuildMessage(user, template);  // Абстрактный шаг
        Validate(user);                               // Виртуальный шаг
        return await _sender.SendAsync(user.Email, message);
    }
    
    protected abstract string BuildMessage(User user, string template);
    protected virtual void Validate(User user) { /* базовая валидация */ }
}

// Конкретные реализации
public class EmailNotificationService : NotificationService
{
    public EmailNotificationService(INotificationSender sender) : base(sender) { }
    
    protected override string BuildMessage(User user, string template)
    {
        return $"Уважаемый {user.Name},\n\n{template}";
    }
}
```

</article>