
<article>

## Работа с файлами и сериализация данных (JSON)

### Чтение и запись файлов

```csharp
using System.IO;

// Простые методы (удобно для небольших файлов)
string content = File.ReadAllText("config.txt");  // Чтение всего файла
File.WriteAllText("output.txt", "Данные");         // Перезапись
File.AppendAllText("log.txt", "Новая запись\n");   // Добавление в конец

// Асинхронные версии (рекомендуется для отзывчивости)
string content = await File.ReadAllTextAsync("large.txt");
await File.WriteAllTextAsync("result.txt", content);

// Потоки для работы с большими файлами
using (var reader = new StreamReader("bigfile.csv"))
{
    string line;
    while ((line = await reader.ReadLineAsync()) != null)
    {
        ProcessLine(line);
    }
}

// Бинарные файлы
byte[] data = await File.ReadAllBytesAsync("image.png");
await File.WriteAllBytesAsync("copy.png", data);

// Работа с путями
string fullPath = Path.GetFullPath("data.txt");
string dir = Path.GetDirectoryName(fullPath);
string ext = Path.GetExtension(fullPath);  // ".txt"
string withoutExt = Path.GetFileNameWithoutExtension(fullPath);

// Безопасное создание пути
string configPath = Path.Combine(Environment.GetFolderPath(
    Environment.SpecialFolder.ApplicationData), "MyApp", "config.json");
```

### Сериализация JSON с System.Text.Json

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;

// Простой класс
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    
    // Игнорировать при сериализации
    [JsonIgnore]
    public string InternalCode { get; set; }
    
    // Кастомное имя в JSON
    [JsonPropertyName("cost")]
    public decimal PriceInJson { get => Price; set => Price = value; }
}

// Сериализация
var product = new Product { Id = 1, Name = "Ноутбук", Price = 99999.99m };

// Базовая сериализация
string json = JsonSerializer.Serialize(product);
// {"Id":1,"Name":"Ноутбук","Price":99999.99,"cost":99999.99}

// С опциями
var options = new JsonSerializerOptions
{
    WriteIndented = true,  // Красивое форматирование
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,  // camelCase
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull  // Не писать null
};

string prettyJson = JsonSerializer.Serialize(product, options);
/*
{
  "id": 1,
  "name": "Ноутбук",
  "price": 99999.99,
  "cost": 99999.99
}
*/

// Десериализация
Product loaded = JsonSerializer.Deserialize<Product>(json);

// Асинхронная работа с потоками
using FileStream createStream = File.Create("product.json");
await JsonSerializer.SerializeAsync(createStream, product, options);

using FileStream openStream = File.OpenRead("product.json");
Product fromFile = await JsonSerializer.DeserializeAsync<Product>(openStream);
```

### Продвинутые сценарии JSON

```csharp
// Полиморфная десериализация
[JsonDerivedType(typeof(Dog), typeDiscriminator: "dog")]
[JsonDerivedType(typeof(Cat), typeDiscriminator: "cat")]
public abstract class Animal
{
    public string Name { get; set; }
}
public class Dog : Animal { public string Breed { get; set; } }
public class Cat : Animal { public bool IsIndoor { get; set; } }

// JSON: {"$type":"dog","Name":"Рекс","Breed":"Овчарка"}
Animal pet = JsonSerializer.Deserialize<Animal>(json);  // Автоматически создаст Dog

// Кастомный конвертер
public class DateOnlyConverter : JsonConverter<DateOnly>
{
    public override DateOnly Read(ref Utf8JsonReader reader, Type type, JsonSerializerOptions options)
        => DateOnly.Parse(reader.GetString());
    
    public override void Write(Utf8JsonWriter writer, DateOnly value, JsonSerializerOptions options)
        => writer.WriteStringValue(value.ToString("yyyy-MM-dd"));
}

// Регистрация конвертера
var options = new JsonSerializerOptions();
options.Converters.Add(new DateOnlyConverter());

// Работа с JsonDocument для динамического парсинга
using JsonDocument doc = JsonDocument.Parse(json);
JsonElement root = doc.RootElement;

string name = root.GetProperty("name").GetString();
if (root.TryGetProperty("optional", out JsonElement optional))
{
    // Поле существует
}

// Enum в JSON
public enum Status { Active, Inactive }
public class Item { public Status Status { get; set; } }

// По умолчанию: число (0, 1)
// С опцией: строка ("Active", "Inactive")
var enumOptions = new JsonSerializerOptions
{
    Converters = { new JsonStringEnumConverter() }
};
```

### XML и другие форматы

```csharp
// XML сериализация (System.Xml.Serialization)
using System.Xml.Serialization;

[XmlRoot("Product")]
public class ProductXml
{
    [XmlElement("Id")]
    public int Id { get; set; }
    
    [XmlAttribute("name")]
    public string Name { get; set; }
}

var serializer = new XmlSerializer(typeof(ProductXml));
using var writer = new StreamWriter("product.xml");
serializer.Serialize(writer, product);

// CSV (простой пример)
public static class CsvHelper
{
    public static string ToCsv<T>(IEnumerable<T> items)
    {
        var props = typeof(T).GetProperties();
        var header = string.Join(",", props.Select(p => p.Name));
        var rows = items.Select(item => 
            string.Join(",", props.Select(p => p.GetValue(item)?.ToString() ?? "")));
        return header + "\n" + string.Join("\n", rows);
    }
}

// YAML (требуется библиотека YamlDotNet)
// var yaml = new Serializer().Serialize(product);
```

</article>
