using weather.Configuration;

namespace weather
{
    public abstract class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();
            var app = builder.Build();

            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }
            
            var env = app.Environment;

            IConfiguration config = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .AddJsonFile($"appsettings.{env.EnvironmentName}.json")
                .AddJsonFile($"sharedsettings.{env.EnvironmentName}.json")
                .AddEnvironmentVariables()
                .Build();
            
            var settings = config.Get<WeatherConfiguration>();
            var sharedSettings = config.Get<WeatherSharedConfiguration>();

            Console.WriteLine($"Environment: {env.EnvironmentName}");
            Console.WriteLine($"Location:{settings.Location}");
            Console.WriteLine($"Shared:{sharedSettings.Shared}");

            app.UseHttpsRedirection();

            app.UseAuthorization();

            app.MapControllers();

            app.Run();
        }
    }
}