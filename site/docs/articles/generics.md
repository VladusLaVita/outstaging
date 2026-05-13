

<article>

## Generics — обобщённое программирование

### Основы дженериков

```csharp
// Без generics: нужно приводить типы, нет проверки на этапе компиляции
ArrayList oldList = new ArrayList();
oldList.Add(1);
oldList.Add("текст");  // Компилируется, но ошибка в рантайме!
int num = (int)oldList[1];  // InvalidCastException!

// С generics: типобезопасность и производительность
List<int> numbers = new List<int>();
numbers.Add(1);
// numbers.Add("текст");  // ОШИБКА компиляции: нельзя добавить string в List<int>
int safeNum = numbers[0];  // Без приведения, тип известен

// Обобщённый класс
public class Box<T>
{
    public T Content { get; set; }
    
    public void Display()
    {
        Console.WriteLine($"Содержимое: {Content?.ToString() ?? "null"}");
    }
}

// Использование с разными типами
var intBox = new Box<int> { Content = 42 };
var stringBox = new Box<string> { Content = "Hello" };
var userBox = new Box<User> { Content = new User("Alice") };

intBox.Display();      // "Содержимое: 42"
stringBox.Display();   // "Содержимое: Hello"
```

### Обобщённые методы и ограничения

```csharp
// Обобщённый метод
public T GetDefault<T>()
{
    return default(T);  // null для ссылочных типов, 0/нулевое значение для значимых
}

int zero = GetDefault<int>();        // 0
string empty = GetDefault<string>(); // null

// Ограничения (constraints) на тип параметра
public class Repository<T> where T : class, IEntity, new()
{
    // T должен быть:
    // class - ссылочным типом
    // IEntity - реализовывать интерфейс IEntity
    // new() - иметь публичный параметрический конструктор
    
    public T Create()
    {
        return new T();  // Возможно благодаря new()
    }
    
    public void Save(T entity)
    {
        // Доступ к членам интерфейса
        entity.Id = Guid.NewGuid();  // IEntity требует свойство Id
    }
}

// Типы ограничений:
// where T : struct          // Только значимые типы
// where T : class           // Только ссылочные типы
// where T : new()           // Параметрический конструктор без аргументов
// where T : BaseClass       // Наследование от конкретного класса
// where T : IInterface      // Реализация интерфейса
// where T : U               // T должен быть или наследовать тип другого параметра
```

### Ковариантность и контравариантность

```csharp
// Ковариантность (out): можно использовать более производный тип
// IEnumerable<out T> - можно читать T, но нельзя записывать
IEnumerable<string> strings = new List<string> { "a", "b" };
IEnumerable<object> objects = strings;  // OK: string -> object (ковариантность)

// Контравариантность (in): можно использовать более базовый тип
// Action<in T> - можно передавать T как параметр
Action<object> actObject = (obj) => Console.WriteLine(obj);
Action<string> actString = actObject;  // OK: object -> string (контравариантность)
actString("Тест");  // Вызовет actObject с аргументом "Тест"

// Инвариантность (без in/out): тип должен совпадать точно
List<string> stringList = new List<string>();
// List<object> objList = stringList;  // ОШИБКА: List<T> инвариантен
// Это правильно: в List<object> можно добавить int, что сломает List<string>

// Практический пример с Func и Action
Func<string, int> parse = int.Parse;
Func<object, int> parseObj = parse;  // Контравариантность по параметру

Func<int, string> toString = i => i.ToString();
Func<int, object> toObj = toString;  // Ковариантность по возвращаемому типу
```

### Практические паттерны с Generics

```csharp
// Паттерн: Generic Factory
public interface IFactory<T>
{
    T Create();
}

public class UserFactory : IFactory<User>
{
    public User Create() => new User();
}

// Паттерн: Generic Repository
public interface IRepository<T> where T : class, IEntity
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
}

// Паттерн: Generic Validator
public interface IValidator<T>
{
    ValidationResult Validate(T entity);
}

public class UserValidator : IValidator<User>
{
    public ValidationResult Validate(User user)
    {
        var result = new ValidationResult();
        if (string.IsNullOrWhiteSpace(user.Name))
            result.Errors.Add("Имя обязательно");
        if (user.Age < 0 || user.Age > 150)
            result.Errors.Add("Некорректный возраст");
        return result;
    }
}

// Использование
public class UserService
{
    private readonly IRepository<User> _repo;
    private readonly IValidator<User> _validator;
    
    public async Task<bool> RegisterUserAsync(User user)
    {
        var validation = _validator.Validate(user);
        if (!validation.IsValid)
            throw new ValidationException(validation.Errors);
            
        await _repo.AddAsync(user);
        return true;
    }
}
```

</article>
