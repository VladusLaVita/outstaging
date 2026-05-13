
<article>

## LINQ — язык интегрированных запросов

### Основы LINQ to Objects

```csharp
using System.Linq;

var numbers = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

// Методы расширения (Method Syntax)
var evens = numbers.Where(n => n % 2 == 0);           // Фильтрация
var squares = numbers.Select(n => n * n);             // Проекция
var firstEven = numbers.First(n => n % 2 == 0);       // Первый подходящий
var count = numbers.Count(n => n > 5);                // Подсчёт
var sum = numbers.Sum();                              // Агрегация
var average = numbers.Average();                      // Среднее
var max = numbers.Max();                              // Максимум

// Синтаксис запросов (Query Syntax) - альтернатива
var query = from n in numbers
            where n % 2 == 0
            select n * n;

// Оба синтаксиса эквивалентны и компилируются в одинаковый IL
```

### Работа с коллекциями объектов

```csharp
var users = new List<User>
{
    new User("Alice", 25, "IT"),
    new User("Bob", 30, "HR"),
    new User("Charlie", 25, "IT"),
    new User("Diana", 35, "Finance")
};

// Фильтрация и проекция
var youngItUsers = users
    .Where(u => u.Age < 30 && u.Department == "IT")
    .Select(u => u.Name);

// Сортировка
var sorted = users
    .OrderBy(u => u.Department)      // Первичная сортировка
    .ThenByDescending(u => u.Age);   // Вторичная

// Группировка
var byDept = users.GroupBy(u => u.Department);
foreach (var group in byDept)
{
    Console.WriteLine($"{group.Key}: {group.Count()} сотрудников");
    foreach (var user in group)
        Console.WriteLine($"  - {user.Name}");
}

// Объединение (Join)
var departments = new List<Department>
{
    new Department("IT", "Информационные технологии"),
    new Department("HR", "Кадры")
};

var userDepts = users
    .Join(departments,
          u => u.Department,      // Ключ из users
          d => d.Code,            // Ключ из departments
          (u, d) => new           // Результат объединения
          {
              UserName = u.Name,
              DeptName = d.FullName
          });

// Групповое объединение (GroupJoin)
var deptWithUsers = departments
    .GroupJoin(users,
               d => d.Code,
               u => u.Department,
               (dept, userGroup) => new
               {
                   Department = dept.FullName,
                   Users = userGroup.Select(u => u.Name)
               });
```

### Отложенное выполнение и материализация

```csharp
// LINQ использует отложенное выполнение (deferred execution)
var data = new[] { 1, 2, 3, 4, 5 };

// Запрос НЕ выполняется при объявлении
var query = data.Where(x => x > 2).Select(x => x * 10);

// Выполнение происходит при переборе:
foreach (var item in query)  // Здесь выполняется Where и Select
{
    Console.WriteLine(item);  // 30, 40, 50
}

// Методы, которые материализуют результат (выполняют запрос сразу):
List<int> list = query.ToList();      // В список
int[] array = query.ToArray();        // В массив
Dictionary<int, int> dict = query.ToDictionary(x => x, x => x * 2);
var lookup = data.ToLookup(x => x % 2);  // Группировка в ILookup

// Важно: если источник изменится после объявления запроса,
// результат при выполнении будет другим!
var numbers = new List<int> { 1, 2, 3 };
var q = numbers.Where(n => n > 1);
numbers.Add(4);  // Изменили источник
var result = q.ToList();  // [2, 3, 4] - включает добавленное!
```

### LINQ to SQL / Entity Framework

```csharp
// LINQ транслируется в выражения (Expression<T>), которые провайдер
// преобразует в целевой язык (SQL, XML и т.д.)

// Пример с EF Core (псевдокод)
using (var context = new AppDbContext())
{
    // Запрос НЕ выполняется сразу
    var activeUsers = context.Users
        .Where(u => u.IsActive)
        .OrderBy(u => u.Name)
        .Select(u => new { u.Id, u.Name });
    
    // Выполнение при материализации - генерируется SQL:
    // SELECT Id, Name FROM Users WHERE IsActive = 1 ORDER BY Name
    var result = activeUsers.ToList();
    
    // ⚠️ Проблема: Client vs Server evaluation
    var badQuery = context.Users
        .Where(u => u.Name.ToUpper() == "ALICE")  //ToUpper() может не транслироваться в SQL
        .ToList();  // Возможно, загрузит ВСЕ пользователи и отфильтрует в памяти!
    
    // ✅ Решение: использовать только методы, поддерживаемые провайдером
    var goodQuery = context.Users
        .Where(u => EF.Functions.Like(u.Name, "Alice"))  // Специфичный для БД метод
        .ToList();
        
    // ⚠️ N+1 проблема: запрос в цикле
    var users = context.Users.ToList();
    foreach (var user in users)
    {
        var orders = context.Orders.Where(o => o.UserId == user.Id).ToList();  // Запрос БД на каждой итерации!
    }
    
    // ✅ Решение: Eager Loading
    var usersWithOrders = context.Users
        .Include(u => u.Orders)  // Загружаем связанные данные одним запросом
        .ToList();
}
```

### Полезные LINQ-методы

```csharp
var items = new[] { "apple", "banana", "cherry", "date" };

// Проверка условий
bool anyLong = items.Any(s => s.Length > 5);      // true (banana, cherry)
bool allShort = items.All(s => s.Length <= 6);    // false
bool hasApple = items.Contains("apple");          // true

// Получение элементов
var first = items.First();                        // "apple"
var firstOr = items.FirstOrDefault(s => s.StartsWith("z")) ?? "default";
var last = items.Last();                          // "date"
var single = items.Single(s => s.Length == 5);    // "apple" (должен быть ровно один)

// Разбиение и объединение
var page = items.Skip(1).Take(2);                 // ["banana", "cherry"]
var distinct = new[] { 1, 2, 2, 3 }.Distinct();   // [1, 2, 3]
var union = new[] { 1, 2 }.Union(new[] { 2, 3 }); // [1, 2, 3]
var intersect = new[] { 1, 2 }.Intersect(new[] { 2, 3 }); // [2]

// Агрегация с начальным значением
var concatenated = items.Aggregate("", (acc, s) => acc + s + ", ");
// "apple, banana, cherry, date, "

// Zip: попарное объединение
var numbers = new[] { 1, 2, 3 };
var letters = new[] { "a", "b", "c" };
var zipped = numbers.Zip(letters, (n, l) => $"{n}{l}");  // ["1a", "2b", "3c"]
```

</article>
