

<article>

## Асинхронное программирование (async/await)

### Основы async/await

```csharp
// Синхронный код (блокирующий)
public string DownloadContent(string url)
{
    using (var client = new WebClient())
    {
        return client.DownloadString(url);  // Поток блокируется до завершения!
    }
}

// Асинхронный код (неблокирующий)
public async Task<string> DownloadContentAsync(string url)
{
    using (var client = new HttpClient())
    {
        // await "освобождает" поток пока выполняется операция
        return await client.GetStringAsync(url);
    }
    // После завершения операция продолжается с этого места
}

// Вызов асинхронного метода
public async Task UseDownloadAsync()
{
    // ✅ Правильно: await в асинхронном методе
    string content = await DownloadContentAsync("https://api.example.com/data");
    Console.WriteLine(content);
    
    // ❌ Неправильно: блокировка .Result или .Wait() - риск deadlock!
    // string bad = DownloadContentAsync("...").Result;
}
```

### Возвращаемые типы асинхронных методов

```csharp
// Task - для методов без возвращаемого значения (замена void)
public async Task SaveAsync(string data)
{
    await File.WriteAllTextAsync("file.txt", data);
}

// Task<T> - для методов с возвращаемым значением
public async Task<int> CountLinesAsync(string path)
{
    var content = await File.ReadAllTextAsync(path);
    return content.Split('\n').Length;
}

// ValueTask<T> - оптимизация для часто синхронно завершаемых операций
public ValueTask<int> GetCachedValueAsync(int key)
{
    if (_cache.TryGetValue(key, out var value))
    {
        return new ValueTask<int>(value);  // Возвращаем сразу, без аллокации Task
    }
    return new ValueTask<int>(LoadValueAsync(key));  // Или асинхронная загрузка
}

// async void - ТОЛЬКО для обработчиков событий!
public async void Button_Click(object sender, EventArgs e)
{
    // Нельзя await в обычном void-методе, но в event handler можно
    await ProcessDataAsync();
}
```

### Параллельное выполнение задач

```csharp
// Последовательное выполнение (медленнее)
public async Task<int> SumDownloadsSequentialAsync(string[] urls)
{
    int total = 0;
    foreach (var url in urls)
    {
        var content = await DownloadContentAsync(url);  // Ждём каждый по очереди
        total += content.Length;
    }
    return total;
}

// Параллельное выполнение (быстрее)
public async Task<int> SumDownloadsParallelAsync(string[] urls)
{
    // Создаём все задачи сразу
    var tasks = urls.Select(url => DownloadContentAsync(url));
    
    // Ждём завершения всех
    var results = await Task.WhenAll(tasks);
    
    return results.Sum(content => content.Length);
}

// Ограничение параллелизма с SemaphoreSlim
public async Task ProcessWithLimitAsync(IEnumerable<string> urls, int maxConcurrency)
{
    using var semaphore = new SemaphoreSlim(maxConcurrency);
    var tasks = urls.Select(async url =>
    {
        await semaphore.WaitAsync();  // Ждём "разрешение"
        try
        {
            return await DownloadContentAsync(url);
        }
        finally
        {
            semaphore.Release();  // Освобождаем "разрешение"
        }
    });
    
    var results = await Task.WhenAll(tasks);
}
```

### Обработка ошибок и отмена

```csharp
// Обработка исключений в async
public async Task<string> SafeDownloadAsync(string url)
{
    try
    {
        return await DownloadContentAsync(url);
    }
    catch (HttpRequestException ex)
    {
        _logger.LogWarning(ex, "Ошибка загрузки {Url}", url);
        return null;  // Или fallback-значение
    }
}

// CancellationToken для отмены операции
public async Task<string> DownloadWithTimeoutAsync(string url, TimeSpan timeout)
{
    using var cts = new CancellationTokenSource(timeout);
    
    try
    {
        // Передаём токен в асинхронный метод
        using var client = new HttpClient();
        return await client.GetStringAsync(url, cts.Token);
    }
    catch (OperationCanceledException)
    {
        _logger.LogInformation("Загрузка {Url} отменена по таймауту", url);
        throw;  // Или вернуть значение по умолчанию
    }
}

// Отмена по внешнему сигналу
public async Task ProcessQueueAsync(CancellationToken cancellationToken)
{
    while (!cancellationToken.IsCancellationRequested)
    {
        var item = await _queue.DequeueAsync(cancellationToken);
        await ProcessItemAsync(item, cancellationToken);
    }
}

// Вызов с отменой
var cts = new CancellationTokenSource();
// ... где-то в другом месте: cts.Cancel();
await ProcessQueueAsync(cts.Token);
```

### ConfigureAwait и контекст синхронизации

```csharp
// По умолчанию, await пытается продолжить выполнение в исходном контексте
// (важно для UI-приложений: продолжение в потоке интерфейса)

public async Task UpdateUiAsync()
{
    var data = await LoadDataAsync();  // Возврат в UI-поток
    myLabel.Text = data;  // Безопасно: мы в потоке, создавшем элемент
}

// ConfigureAwait(false) - не возвращаться в исходный контекст
// ✅ Использовать в библиотеках и сервисном коде для производительности
public async Task ProcessAsync()
{
    var data = await LoadDataAsync().ConfigureAwait(false);
    // Продолжение может выполниться в любом потоке из пула
    var result = Transform(data);  // Не зависит от контекста
    await SaveAsync(result).ConfigureAwait(false);
}

// ❌ Не использовать ConfigureAwait(false) в:
// - UI-коде (WPF, WinForms, MAUI)
// - ASP.NET Core (там контекст по умолчанию не требуется, но лучше явно)
// - Когда после await обращаетесь к потоко-зависимым ресурсам
```

</article>