<article>

## Классы и объекты. Основы ООП

### Объявление класса и создание объектов

```csharp
// Простой класс
public class Person
{
    // Поля (обычно private)
    private string _name;
    private int _age;
    
    // Конструктор
    public Person(string name, int age)
    {
        _name = name;
        _age = age;
    }
    
    // Методы
    public void Introduce()
    {
        Console.WriteLine($"Привет, я {_name}, мне {_age} лет.");
    }
    
    public bool IsAdult() => _age >= 18;
}

// Использование
Person person = new Person("Alice", 25);
person.Introduce();  // "Привет, я Alice, мне 25 лет."
Console.WriteLine(person.IsAdult());  // True
```

### Инкапсуляция и модификаторы доступа

```csharp
public class BankAccount
{
    // Приватное поле - скрыто от внешнего кода
    private decimal _balance;
    
    // Публичный метод для контролируемого доступа
    public void Deposit(decimal amount)
    {
        if (amount <= 0) throw new ArgumentException("Сумма должна быть положительной");
        _balance += amount;
    }
    
    public bool Withdraw(decimal amount)
    {
        if (amount > _balance) return false;
        _balance -= amount;
        return true;
    }
    
    // Публичное свойство только для чтения
    public decimal Balance => _balance;
    
    // Модификаторы доступа:
    // public    - доступен отовсюду
    // private   - доступен только внутри класса (по умолчанию для полей)
    // protected - доступен в классе и наследниках
    // internal  - доступен в пределах сборки (.dll/.exe)
    // protected internal - комбинация
}
```

### Статические члены класса

```csharp
public class MathHelper
{
    // Статическое поле - одно на все экземпляры
    public static readonly double Pi = 3.14159265359;
    
    // Статический метод - вызывается без создания объекта
    public static double CircleArea(double radius)
    {
        return Pi * radius * radius;
    }
    
    // Статический конструктор - выполняется один раз при первом обращении
    static MathHelper()
    {
        Console.WriteLine("MathHelper инициализирован");
    }
}

// Вызов
double area = MathHelper.CircleArea(5);  // Не создаём new MathHelper!
Console.WriteLine(MathHelper.Pi);
```

### Структуры (struct) против классов (class)

```csharp
// struct - значимый тип (копируется при передаче)
public struct Point
{
    public int X { get; set; }
    public int Y { get; set; }
    
    public Point(int x, int y) : this()  // Требуется для struct
    {
        X = x;
        Y = y;
    }
}

// class - ссылочный тип (передаётся ссылка)
public class Person
{
    public string Name { get; set; }
}

// Разница в поведении
Point p1 = new Point(1, 2);
Point p2 = p1;  // Копирование значений
p2.X = 10;
Console.WriteLine(p1.X);  // 1 (p1 не изменился!)

Person person1 = new Person { Name = "Alice" };
Person person2 = person1;  // Копирование ссылки
person2.Name = "Bob";
Console.WriteLine(person1.Name);  // "Bob" (изменился тот же объект!)

// Когда использовать struct:
// ✓ Небольшие данные (< 16 байт)
// ✓ Неизменяемые значения (immutable)
// ✓ Не требуют наследования
// ✓ Примеры: Point, Rectangle, Color, Complex
```

</article>
