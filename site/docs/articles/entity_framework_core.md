





<article>

## Entity Framework Core: основы ORM

### Настройка DbContext и моделей

```csharp
using Microsoft.EntityFrameworkCore;

// Модель сущности
public class User
{
    public int Id { get; set; }  // Первичный ключ по соглашению
    
    [StringLength(100)]
    public string Name { get; set; }
    
    [EmailAddress]
    public string Email { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // Навигационное свойство (связь 1-ко-многим)
    public ICollection<Order> Orders { get; set; }
}

public class Order
{
    public int Id { get; set; }
    public decimal Total { get; set; }
    
    // Внешний ключ
    public int UserId { get; set; }
    
    // Навигационное свойство
    public User User { get; set; }
}

// Контекст базы данных
public class AppDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
    public DbSet<Order> Orders { get; set; }
    
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options) { }
    
    // Дополнительные настройки моделей
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Fluent API (альтернатива атрибутам)
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasIndex(u => u.Email).IsUnique();  // Уникальный индекс
            entity.Property(u => u.Name).IsRequired();  // NOT NULL
            entity.HasMany(u => u.Orders)
                  .WithOne(o => o.User)
                  .HasForeignKey(o => o.UserId)
                  .OnDelete(DeleteBehavior.Cascade);  // Каскадное удаление
        });
    }
}
```

### Подключение к БД и миграции

```csharp
// Регистрация в Program.cs (ASP.NET Core)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")));

// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyApp;Trusted_Connection=True;"
  }
}

// Миграции (через CLI)
// Создать миграцию
dotnet ef migrations add InitialCreate

// Применить миграции к БД
dotnet ef database update

// Скрипт миграции без применения
dotnet ef migrations script

// Удалить последнюю миграцию
dotnet ef migrations remove

// Программное применение миграций (для тестов)
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();  // Применяет все неприменённые миграции
}
```

### CRUD операции с LINQ

```csharp
public class UserService
{
    private readonly AppDbContext _db;
    
    public UserService(AppDbContext db) => _db = db;
    
    // CREATE
    public async Task<User> CreateUserAsync(string name, string email)
    {
        var user = new User { Name = name, Email = email };
        _db.Users.Add(user);
        await _db.SaveChangesAsync();  // Выполняет INSERT
        return user;
    }
    
    // READ
    public async Task<User?> GetUserByIdAsync(int id)
    {
        return await _db.Users.FindAsync(id);  // По первичному ключу
    }
    
    public async Task<List<User>> SearchUsersAsync(string searchTerm)
    {
        return await _db.Users
            .Where(u => u.Name.Contains(searchTerm) || u.Email.Contains(searchTerm))
            .OrderBy(u => u.Name)
            .ToListAsync();  // Выполняет SELECT с WHERE и ORDER BY
    }
    
    // UPDATE
    public async Task<bool> UpdateUserEmailAsync(int userId, string newEmail)
    {
        var user = await _db.Users.FindAsync(userId);
        if (user == null) return false;
        
        user.Email = newEmail;
        // Не нужно вызывать Update() - EF отслеживает изменения
        await _db.SaveChangesAsync();  // Выполняет UPDATE
        return true;
    }
    
    // DELETE
    public async Task<bool> DeleteUserAsync(int userId)
    {
        var user = await _db.Users.FindAsync(userId);
        if (user == null) return false;
        
        _db.Users.Remove(user);
        await _db.SaveChangesAsync();  // Выполняет DELETE
        return true;
    }
}
```

### Загрузка связанных данных

```csharp
// Eager Loading (загрузка сразу с Include)
var userWithOrders = await _db.Users
    .Include(u => u.Orders)  // Загружает заказы
    .FirstOrDefaultAsync(u => u.Id == userId);

// ThenInclude для вложенных связей
var detailedUser = await _db.Users
    .Include(u => u.Orders)
        .ThenInclude(o => o.OrderItems)  // Загружает элементы заказов
    .FirstOrDefaultAsync(u => u.Id == userId);

// Explicit Loading (загрузка по требованию)
var user = await _db.Users.FindAsync(userId);
await _db.Entry(user).Collection(u => u.Orders).LoadAsync();  // Явная загрузка

// Select Loading (загрузка только нужных полей)
var userSummary = await _db.Users
    .Where(u => u.Id == userId)
    .Select(u => new
    {
        u.Name,
        OrderCount = u.Orders.Count(),
        LastOrderDate = u.Orders.Max(o => (DateTime?)o.CreatedAt)
    })
    .FirstOrDefaultAsync();

// ⚠️ Проблема: N+1 запросов
var users = await _db.Users.ToListAsync();  // 1 запрос
foreach (var user in users)
{
    var orders = await _db.Orders.Where(o => o.UserId == user.Id).ToListAsync();  // N запросов!
}

// ✅ Решение: Eager Loading
var usersWithOrders = await _db.Users
    .Include(u => u.Orders)
    .ToListAsync();  // Всего 1-2 запроса в зависимости от провайдера
```

</article>
