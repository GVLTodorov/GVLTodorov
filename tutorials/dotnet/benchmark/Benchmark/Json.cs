using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Engines;
using BenchmarkDotNet.Order;
using JsonConvert = Newtonsoft.Json.JsonConvert;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace Benchmark;

public class JsonBenchmark
{
    [SimpleJob(RunStrategy.ColdStart, iterationCount: 5, invocationCount: 50)]
    [Orderer(SummaryOrderPolicy.Method)]
    public class SerializeObject
    {
        private const int N = 100;
        private string _raw { get; set; }
        private object _object { get; set; }

        [GlobalSetup]
        public void Setup()
        {
            _raw = File.ReadAllText("./example.json");
            _object = JsonConvert.DeserializeObject(_raw) ?? throw new ArgumentNullException(nameof(_object));
        }

        [Benchmark]
        public void NewtonSerialize()
        => Enumerable.Repeat(0, N).ToList().ForEach(
                (_) =>
                {
                    JsonConvert.SerializeObject(_object);
                });

        [Benchmark]
        public void NewtonDeserialize()
        => Enumerable.Repeat(0, N).ToList().ForEach(
                (_) =>
                {
                    JsonConvert.DeserializeObject(_raw);
                });


        [Benchmark]
        public void MicrosoftSerialize()
        => Enumerable.Repeat(0, N).ToList().ForEach(
                (_) =>
                {
                    JsonSerializer.Serialize(_object);
                });

        [Benchmark]
        public void MicrosoftDeserialize()
        => Enumerable.Repeat(0, N).ToList().ForEach(
                (_) =>
                {
                    JsonSerializer.Deserialize<object>(_raw);
                });
    }
}