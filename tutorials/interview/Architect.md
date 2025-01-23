# .NET Interview Preparation

Подготовката за интервю за .NET архитект включва познания за платформата, технологии, добри практики и реален опит в проекти. Това ръководство съдържа основните теми, примери, теоретични пояснения и подходи, които да използвате за вашата подготовка.

---

## Основни области в .NET

### 1. **.NET платформа**
.NET е платформа за разработка, която предоставя възможности за създаване на приложения за различни операционни системи и устройства. 

- **Разлика между .NET Framework, .NET Core и .NET (5/6/7/8):**
  - **.NET Framework**: Подходящ само за Windows приложения. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/framework/)
  - **.NET Core**: Cross-platform, open-source, с висока производителност. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/core/)
  - **.NET 5/6/7/8**: Единен runtime, който обединява функционалностите на Framework и Core. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/)

  ```csharp
  Console.WriteLine($"Platform: {Environment.OSVersion}");
  ```
- **CLR (Common Language Runtime):**
  CLR е среда за изпълнение, която предоставя услуги като управление на паметта, garbage collection, и компилация на междинен код (MSIL) до машинен код. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/standard/clr/)

  ```csharp
  GC.Collect(); // Пример за ръчно управление на garbage collection.
  ```

- **BCL (Base Class Library):**
  Включва базови библиотеки за работа с колекции, файлове, мрежа и др. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/standard/base-types/)

---

### 2. **ASP.NET Core**
ASP.NET Core е framework за създаване на web приложения, API и реалновременни приложения. [Прочетете повече](https://learn.microsoft.com/en-us/aspnet/core/)

#### Request Processing Pipeline (Middleware):
Pipeline-ът на заявките е модулен и позволява добавяне на middleware компоненти за обработка на заявките и отговорите. [Прочетете повече](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/)
```csharp
public class LoggingMiddleware
{
    private readonly RequestDelegate _next;

    public LoggingMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        Console.WriteLine($"Request: {context.Request.Path}");
        await _next(context);
    }
}

// Добавяне в Startup.cs
app.UseMiddleware<LoggingMiddleware>();
```

#### Dependency Injection (DI):
ASP.NET Core предоставя вграден DI контейнер за инжектиране на зависимости. [Прочетете повече](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection/)
```csharp
services.AddSingleton<IMyService, MyService>();
services.AddScoped<IRepository, Repository>();
```

#### Authentication и Authorization:
Поддръжка на JWT, OAuth2 и политики за достъп. [Прочетете повече](https://learn.microsoft.com/en-us/aspnet/core/security/)
```csharp
services.AddAuthentication("Bearer")
    .AddJwtBearer(options =>
    {
        options.Authority = "https://example.com";
        options.Audience = "api1";
    });
```

---

### 3. **EF Core (Entity Framework Core)**
EF Core е ORM, който позволява работа с бази данни чрез C# обекти. [Прочетете повече](https://learn.microsoft.com/en-us/ef/core/)

#### Code-First миграции:
Позволява създаване на база данни въз основа на C# модели. [Прочетете повече](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
}

protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Product>().Property(p => p.Name).IsRequired();
}
```

#### LINQ заявки:
Позволява писане на заявки към базата данни чрез езика на C#. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/)
```csharp
var expensiveProducts = context.Products
    .Where(p => p.Price > 1000)
    .OrderBy(p => p.Name)
    .ToList();
```

#### Транзакции:
[Прочетете повече](https://learn.microsoft.com/en-us/ef/core/saving/transactions/)
```csharp
using var transaction = await context.Database.BeginTransactionAsync();
try
{
    // Вашите операции
    await context.SaveChangesAsync();
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

---

### 4. **Multi-threading и Asynchronous Programming**

#### Асинхронна операция:
Асинхронността подобрява производителността, като освобождава нишките по време на I/O операции. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/csharp/async)
```csharp
public async Task<string> GetDataAsync()
{
    using (var client = new HttpClient())
    {
        return await client.GetStringAsync("https://example.com");
    }
}
```

#### Parallel Programming:
Позволява обработка на задачи паралелно за по-добра производителност. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/)
```csharp
Parallel.For(0, 10, i =>
{
    Console.WriteLine($"Task {i} is running.");
});
```

---

### 5. **Advanced Language Features в C#**

#### Reflection:
Reflection се използва за динамична работа с метаданни. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/reflection)
```csharp
var type = typeof(Product);
foreach (var prop in type.GetProperties())
{
    Console.WriteLine(prop.Name);
}
```

#### Records:
Records предоставят удобен начин за работа с immutable типове. [Прочетете повече](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-9#records)
```csharp
public record Product(string Name, decimal Price);
```

---

### 6. **Архитектурни подходи и шаблони (Design Patterns)**

#### Singleton:
[Прочетете повече](https://refactoring.guru/design-patterns/singleton)
```csharp
public class Singleton
{
    private static Singleton _instance;
    private static readonly object _lock = new object();

    private Singleton() {}

    public static Singleton Instance
    {
        get
        {
            lock (_lock)
            {
                return _instance ??= new Singleton();
            }
        }
    }
}
```

#### Repository Pattern:
[Прочетете повече](https://martinfowler.com/eaaCatalog/repository.html)
```csharp
public interface IRepository<T>
{
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> GetByIdAsync(int id);
    Task AddAsync(T entity);
}
```

---

### 7. **Security в .NET**

#### Data Protection API:
[Прочетете повече](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/)
```csharp
var protector = _dataProtectionProvider.CreateProtector("MyPurpose");
var protectedData = protector.Protect("Sensitive Data");
var unprotectedData = protector.Unprotect(protectedData);
```

#### OWASP Best Practices:
[Прочетете повече](https://owasp.org/www-project-top-ten/)
- Използвайте `SqlParameter` за предотвратяване на SQL Injection:
  ```csharp
  var command = new SqlCommand("SELECT * FROM Users WHERE Username = @username", connection);
  command.Parameters.AddWithValue("@username", username);
  ```

---

### 8. **DevOps и автоматизация**

#### CI/CD с .NET:
[Прочетете повече](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/dotnet-core)
```yaml
- task: UseDotNet@2
  inputs:
    packageType: 'sdk'
    version: '6.x'

- task: DotNetCoreCLI@2
  inputs:
    command: 'publish'
    publishWebProjects: true
```

#### Dockerfile за .NET приложение:
[Прочетете повече](https://learn.microsoft.com/en-us/dotnet/core/docker/)
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /app
COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:6.0
WORKDIR /app
COPY --from=build /app/out .
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

---

### 9. **Cloud Integrations**

#### Azure Integration:
[Прочетете повече](https://learn.microsoft.com/en-us/azure/developer/dotnet/)
```csharp
var client = new BlobServiceClient(connectionString);
var container = client.GetBlobContainerClient("mycontainer");
```

---

## Сценарии за интервю

1. **Кодиране:**
   - Създайте CRUD операции с Web API.
   - Имплементирайте оптимизирана LINQ заявка.

2. **Case Study:**
   - Дизайн на скалируема система за поръчки с microservices.

3. **Behavioral Questions:**
   - Споделете опит с взимане на грешно решение и как сте се справили.

---

## Финални съвети
- **Обяснявайте мисловния си процес:** Аргументирайте решенията си.
- **Фокусирайте се върху опита:** Използвайте примери от реални проекти.
- **Практикувайте:** Създайте тестови приложения, за да се подготвите практически.

---
