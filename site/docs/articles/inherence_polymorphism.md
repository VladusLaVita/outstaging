<article>

## Наследование и полиморфизм в C#

### Основы наследования

```csharp
// Базовый класс
public class Animal
{
    public string Name { get; set; }
    
    public Animal(string name)
    {
        Name = name;
    }
    
    // Виртуальный метод - можно переопределить в наследнике
    public virtual void MakeSound()
    {
        Console.WriteLine("Животное издаёт звук");
    }
    
    // Обычный метод - нельзя переопределить (только скрыть)
    public void Sleep()
    {
        Console.WriteLine($"{Name} спит");
    }
}

// Производный класс
public class Dog : Animal  // : означает наследование
{
    public string Breed { get; set; }
    
    // Конструктор с вызовом базового конструктора
    public Dog(string name, string breed) : base(name)
    {
        Breed = breed;
    }
    
    // Переопределение виртуального метода
    public override void MakeSound()
    {
        Console.WriteLine($"{Name} лает: Гав-гав!");
    }
    
    // Новый метод, специфичный для собаки
    public void Fetch()
    {
        Console.WriteLine($"{Name} приносит мяч");
    }
}

// Использование
Animal myPet = new Dog("Рекс", "Овчарка");
myPet.MakeSound();  // "Рекс лает: Гав-гав!" (полиморфизм!)
myPet.Sleep();      // "Рекс спит" (унаследованный метод)
// myPet.Fetch();   // ОШИБКА: метод не виден через ссылку типа Animal
```

### Полиморфизм в действии

```csharp
public class Cat : Animal
{
    public Cat(string name) : base(name) { }
    
    public override void MakeSound()
    {
        Console.WriteLine($"{Name} мяукает: Мяу!");
    }
}

// Коллекция базового типа с разными наследниками
List<Animal> zoo = new List<Animal>
{
    new Dog("Шарик", "Дворняга"),
    new Cat("Мурка"),
    new Dog("Бобик", "Лабрадор")
};

// Единый интерфейс для разных типов
foreach (Animal animal in zoo)
{
    animal.MakeSound();  // Вызывается РЕАЛИЗАЦИЯ конкретного типа
    // Полиморфизм: один вызов, разное поведение
}

/* Вывод:
Шарик лает: Гав-гав!
Мурка мяукает: Мяу!
Бобик лает: Гав-гав!
*/
```

### Абстрактные и запечатанные классы

```csharp
// abstract - класс нельзя создать напрямую, только наследовать
public abstract class Shape
{
    public string Color { get; set; }
    
    // Абстрактный метод - НЕТ реализации, ОБЯЗАТЕЛЬНО переопределить
    public abstract double CalculateArea();
    
    // Виртуальный метод с реализацией по умолчанию
    public virtual void Draw()
    {
        Console.WriteLine($"Рисую {Color} фигуру");
    }
}

// Конкретный наследник
public class Circle : Shape
{
    public double Radius { get; set; }
    
    public Circle(double radius, string color)
    {
        Radius = radius;
        Color = color;
    }
    
    // ОБЯЗАТЕЛЬНАЯ реализация абстрактного метода
    public override double CalculateArea()
    {
        return Math.PI * Radius * Radius;
    }
    
    // Опциональное переопределение виртуального метода
    public override void Draw()
    {
        Console.WriteLine($"Рисую {Color} круг радиусом {Radius}");
    }
}

// sealed - класс нельзя наследовать дальше
public sealed class FinalClass : Shape
{
    public override double CalculateArea() => 0;  // "заглушка"
}
// public class Derived : FinalClass { }  // ОШИБКА: нельзя наследовать sealed
```

### Операторы is и as с наследованием

```csharp
Animal animal = new Dog("Тузик", "Пудель");

// Проверка типа
if (animal is Dog dog)  // Pattern matching (C# 7.0+)
{
    Console.WriteLine($"Это собака породы {dog.Breed}");
    dog.Fetch();  // Доступ к методам производного класса
}

// Безопасное приведение
Cat? cat = animal as Cat;
if (cat == null)
{
    Console.WriteLine("Это не кошка");
}

// Switch expression с типами (C# 8.0+)
string description = animal switch
{
    Dog d => $"Собака: {d.Breed}",
    Cat c => $"Кошка",
    Animal a => $"Просто животное: {a.Name}",
    _ => "Неизвестно"
};
```

</article>