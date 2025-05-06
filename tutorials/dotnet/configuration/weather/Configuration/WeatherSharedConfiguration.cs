using System.Text.Json.Serialization;

namespace weather.Configuration
{
    public class WeatherSharedConfiguration
    {
        [JsonPropertyName("shared")]
        public string Shared { get; set; }
    }
}
