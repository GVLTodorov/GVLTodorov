using Microsoft.AspNetCore.Mvc;
using weather.Configuration;

namespace weather.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ConfigurationController : ControllerBase
    {

        [HttpGet(Name = "GetWeatherForecast")]
        public WeatherConfiguration Get()
        {
            return new WeatherConfiguration();
        }
    }
}
