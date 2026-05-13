<article>

## Массивы и основные коллекции

### Массивы

```csharp
// Одномерный массив
int[] numbers = new int[5];  // [0,0,0,0,0]
numbers[0] = 10;
numbers[1] = 20;

// Инициализация при объявлении
string[] names = { "Alice", "Bob", "Charlie" };
int[] primes = new int[] { 2, 3, 5, 7, 11 };

// Доступ к элементам и свойствам
Console.WriteLine(names.Length);        // 3
Console.WriteLine(names[names.Length - 1]);  // "Charlie"

// Многомерные массивы
int[,] matrix = new int[3, 3];  // 3x3
matrix[0, 0] = 1;
matrix[1, 2] = 5;

// Зубчатые массивы (массив массивов)
int[][] jagged = new int[3][];
jagged[0] = new int[] { 1, 2, 3 };
jagged[1] = new int[] { 4, 5 };
jagged[2] = new int[] { 6 };
```

### List<T> - динамический список

```csharp
using System.Collections.Generic;

// Создание и базовые операции
List<string> users = new List<string>();
users.Add("Alice");
users.Add("Bob");
users.AddRange(new[] { "Charlie", "Diana" });

// Доступ и модификация
Console.WriteLine(users[0]);        // Alice
users[1] = "Robert";                // Изменение элемента
users.Remove("Alice");              // Удаление по значению
users.RemoveAt(0);                  // Удаление по индексу

// Поиск
bool hasBob = users.Contains("Bob");                    // true
int index = users.FindIndex(u => u.StartsWith("C"));    // индекс первого, начинающегося с "C"

// Перебор
foreach (var user in users)
{
    Console.WriteLine(user);
}

// Сортировка
users.Sort();  // По алфавиту
users.Reverse();  // В обратном порядке
```

### Dictionary<TKey, TValue> - хеш-таблица

```csharp
Dictionary<string, int> ages = new Dictionary<string, int>();

// Добавление
ages["Alice"] = 25;
ages.Add("Bob", 30);  // Бросит исключение, если ключ уже есть

// Доступ
int aliceAge = ages["Alice"];  // 25

// Безопасный доступ
if (ages.TryGetValue("Charlie", out int charlieAge))
{
    Console.WriteLine(charlieAge);
}
else
{
    Console.WriteLine("Charlie не найден");
}

// Проверка наличия и удаление
if (ages.ContainsKey("Bob"))
{
    ages.Remove("Bob");
}

// Перебор
foreach (var kvp in ages)
{
    Console.WriteLine($"{kvp.Key}: {kvp.Value}");
}

// Инициализация
var scores = new Dictionary<string, int>
{
    ["Alice"] = 95,
    ["Bob"] = 87,
    ["Charlie"] = 92
};
```

### Другие важные коллекции

```csharp
using System.Collections.Generic;
using System.Collections;

// HashSet<T> - уникальные элементы, быстрая проверка вхождения
HashSet<int> uniqueNumbers = new HashSet<int> { 1, 2, 3, 2, 1 };  // {1, 2, 3}
uniqueNumbers.Add(4);  // true
bool wasAdded = uniqueNumbers.Add(3);  // false (уже есть)

// Queue<T> - очередь (FIFO: First In, First Out)
Queue<string> queue = new Queue<string>();
queue.Enqueue("First");
queue.Enqueue("Second");
string next = queue.Dequeue();  // "First"
string peeked = queue.Peek();   // "Second" (не удаляет)

// Stack<T> - стек (LIFO: Last In, First Out)
Stack<int> stack = new Stack<int>();
stack.Push(1);
stack.Push(2);
int top = stack.Pop();  // 2
int nextTop = stack.Peek();  // 1

// LinkedList<T> - двусвязный список
LinkedList<string> linked = new LinkedList<string>();
linked.AddLast("A");
linked.AddFirst("Start");
var node = linked.Find("A");
linked.AddAfter(node, "Between");

// SortedSet<T> - отсортированный набор уникальных элементов
SortedSet<int> sorted = new SortedSet<int> { 5, 2, 8, 1 };  // {1, 2, 5, 8}
```

### Выбор коллекции

```csharp
/*
Когда использовать:

✓ Array: фиксированный размер, максимальная производительность
✓ List<T>: динамический размер, частый доступ по индексу
✓ Dictionary<TKey,TValue>: быстрый поиск по ключу, пары ключ-значение
✓ HashSet<T>: проверка уникальности, операции над множествами
✓ Queue<T>: обработка в порядке поступления (очередь задач)
✓ Stack<T>: отмена действий, обход дерева в глубину
✓ LinkedList<T>: частые вставки/удаления в середине
✓ SortedSet<T>: автоматическая сортировка + уникальность
*/
```

</article>
