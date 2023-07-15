using System.Text.Json.Serialization;

namespace weather.Configuration
{
    public class WeatherConfiguration
    {
        [JsonPropertyName("location")]
        public string Location { get; set; }
    }
}
