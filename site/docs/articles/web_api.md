
<article>

## ASP.NET Core: создание веб-приложений и Web API

### Минимальный Web API

```csharp
// Program.cs (.NET 6+)
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<AppDbContext>(/* ... */);

var app = builder.Build();

app.MapGet("/", () => "Hello World!");

app.MapGet("/users", async (AppDbContext db) => 
    await db.Users.ToListAsync());

app.MapGet("/users/{id:int}", async (int id, AppDbContext db) => 
    await db.Users.FindAsync(id) is User user 
        ? Results.Ok(user) 
        : Results.NotFound());

app.MapPost("/users", async (UserDto dto, AppDbContext db) =>
{
    var user = new User { Name = dto.Name, Email = dto.Email };
    db.Users.Add(user);
    await db.SaveChangesAsync();
    return Results.Created($"/users/{user.Id}", user);
});

app.MapPut("/users/{id:int}", async (int id, UserDto dto, AppDbContext db) =>
{
    var user = await db.Users.FindAsync(id);
    if (user == null) return Results.NotFound();
    
    user.Name = dto.Name;
    user.Email = dto.Email;
    await db.SaveChangesAsync();
    return Results.NoContent();
});

app.MapDelete("/users/{id:int}", async (int id, AppDbContext db) =>
{
    var user = await db.Users.FindAsync(id);
    if (user == null) return Results.NotFound();
    
    db.Users.Remove(user);
    await db.SaveChangesAsync();
    return Results.NoContent();
});

app.Run();

// DTO для валидации входных данных
public record UserDto(string Name, string Email);
```

### Контроллеры (традиционный подход)

```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly AppDbContext _db;
    
    public UsersController(AppDbContext db) => _db = db;
    
    // GET: api/users
    [HttpGet]
    public async Task<ActionResult<IEnumerable<User>>> GetUsers()
    {
        return await _db.Users.ToListAsync();
    }
    
    // GET: api/users/5
    [HttpGet("{id}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user == null) return NotFound();
        return user;
    }
    
    // POST: api/users
    [HttpPost]
    public async Task<ActionResult<User>> CreateUser(CreateUserDto dto)
    {
        var user = new User { Name = dto.Name, Email = dto.Email };
        _db.Users.Add(user);
        await _db.SaveChangesAsync();
        
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
    
    // PUT: api/users/5
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateUser(int id, UpdateUserDto dto)
    {
        if (id != dto.Id) return BadRequest();
        
        var user = await _db.Users.FindAsync(id);
        if (user == null) return NotFound();
        
        user.Name = dto.Name;
        user.Email = dto.Email;
        
        try
        {
            await _db.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
            if (!UserExists(id)) return NotFound();
            throw;
        }
        
        return NoContent();
    }
    
    // DELETE: api/users/5
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user == null) return NotFound();
        
        _db.Users.Remove(user);
        await _db.SaveChangesAsync();
        
        return NoContent();
    }
    
    private bool UserExists(int id) => _db.Users.Any(e => e.Id == id);
}

// DTO с валидацией
public class CreateUserDto
{
    [Required, StringLength(100)]
    public string Name { get; set; }
    
    [Required, EmailAddress]
    public string Email { get; set; }
}
```

### Middleware и конвейер запросов

```csharp
// Встроенные middleware
app.UseHttpsRedirection();  // Перенаправление HTTP -> HTTPS
app.UseStaticFiles();       // Раздача статических файлов (wwwroot)
app.UseRouting();          // Сопоставление маршрутов
app.UseAuthentication();   // Аутентификация
app.UseAuthorization();    // Авторизация

// Кастомный middleware (через Use/Run/Map)
app.Use(async (context, next) =>
{
    // До обработки запроса
    Console.WriteLine($"Запрос: {context.Request.Method} {context.Request.Path}");
    
    await next();  // Передача следующему middleware
    
    // После обработки (можно модифицировать ответ)
    Console.WriteLine($"Ответ: {context.Response.StatusCode}");
});

// Middleware как класс
public class RequestTimingMiddleware
{
    private readonly RequestDelegate _next;
    
    public RequestTimingMiddleware(RequestDelegate next) => _next = next;
    
    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        await _next(context);
        stopwatch.Stop();
        Console.WriteLine($"Запрос обработан за {stopwatch.ElapsedMilliseconds} мс");
    }
}

// Регистрация
app.UseMiddleware<RequestTimingMiddleware>();
// Или расширение:
// app.UseRequestTiming();
```

### Конфигурация и опции

```csharp
// appsettings.json
{
  "AppSettings": {
    "MaxUploadSize": 10485760,
    "AllowedHosts": ["example.com"]
  }
}

// Сильно типизированные опции
public class AppSettings
{
    public long MaxUploadSize { get; set; }
    public string[] AllowedHosts { get; set; }
}

// Регистрация в Program.cs
builder.Services.Configure<AppSettings>(
    builder.Configuration.GetSection("AppSettings"));

// Внедрение через IOptions<T>
public class UploadService
{
    private readonly long _maxSize;
    
    public UploadService(IOptions<AppSettings> options)
    {
        _maxSize = options.Value.MaxUploadSize;
    }
}

// Конфигурация по средам
// appsettings.Development.json переопределяет базовые настройки
builder.Configuration
    .AddJsonFile("appsettings.json")
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables();
```

</article>
