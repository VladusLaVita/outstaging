
<article>

## Свойства, конструкторы и инициализация объектов

### Свойства (Properties)

```csharp
public class Product
{
    // Автоматическое свойство
    public string Name { get; set; }
    
    // Свойство только для чтения
    public Guid Id { get; } = Guid.NewGuid();
    
    // Свойство с валидацией
    private decimal _price;
    public decimal Price
    {
        get => _price;
        set
        {
            if (value < 0) throw new ArgumentException("Цена не может быть отрицательной");
            _price = value;
        }
    }
    
    // Вычисляемое свойство
    public decimal PriceWithTax => Price * 1.20m;
    
    // Expression-bodied свойства (C# 6.0+)
    public string DisplayName => $"{Name} (ID: {Id})";
}

// Использование
var product = new Product
{
    Name = "Ноутбук",
    Price = 99999.99m
};
Console.WriteLine(product.DisplayName);
```

### Конструкторы и инициализация

```csharp
public class Order
{
    public int OrderId { get; }
    public DateTime Created { get; }
    public List<string> Items { get; }
    
    // Основной конструктор
    public Order(int orderId)
    {
        OrderId = orderId;
        Created = DateTime.Now;
        Items = new List<string>();
    }
    
    // Перегрузка конструктора с цепочкой вызовов (:)
    public Order(int orderId, params string[] items) : this(orderId)
    {
        Items.AddRange(items);
    }
    
    // Инициализация коллекций при объявлении
    public Dictionary<string, int> Metadata { get; } = new();
}

// Object initializer (C# 3.0+)
var order = new Order(1001, "Товар1", "Товар2")
{
    // Дополнительные свойства можно задать после конструктора
    // (если у них есть public set)
};

// Collection initializer
var tags = new List<string> { "новинка", "акция", "хит" };

// Index initializer (C# 6.0+)
var config = new Dictionary<string, string>
{
    ["Host"] = "localhost",
    ["Port"] = "8080"
};
```

### Required свойства и init (C# 9.0+)

```csharp
public class User
{
    // required - обязательно задать при создании объекта
    public required string Username { get; init; }
    
    // init - можно задать только при инициализации (immutable после создания)
    public required string Email { get; init; }
    public DateTime Registered { get; init; } = DateTime.UtcNow;
    
    // Обычное свойство можно менять после создания
    public bool IsActive { get; set; } = true;
}

// Создание объекта
var user = new User
{
    Username = "alice",  // Обязательно!
    Email = "alice@example.com"  // Обязательно!
    // Registered установится по умолчанию
};

// user.Username = "bob";  // ОШИБКА: init-свойства неизменяемы после создания
user.IsActive = false;  // OK: обычное свойство с set
```

### Деструкторы и IDisposable

```csharp
// Деструктор (финализатор) - вызывается GC, не детерминировано
public class Resource
{
    ~Resource()  // Не рекомендуется полагаться только на это!
    {
        Cleanup();
    }
    
    private void Cleanup() { /* освобождение ресурсов */ }
}

// Правильный паттерн: IDisposable
public class DatabaseConnection : IDisposable
{
    private bool _disposed = false;
    
    public void Open() { /* открытие соединения */ }
    
    // Реализация IDisposable
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);  // Не вызывать финализатор
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        
        if (disposing)
        {
            // Освобождение управляемых ресурсов
        }
        // Освобождение неуправляемых ресурсов
        
        _disposed = true;
    }
}

// Использование с using (автоматический вызов Dispose)
using (var db = new DatabaseConnection())
{
    db.Open();
    // Работа с БД
}  // Dispose() вызывается автоматически здесь

// Или (C# 8.0+): using declaration
using var db2 = new DatabaseConnection();
// Dispose() вызывается при выходе из области видимости
```

</article>