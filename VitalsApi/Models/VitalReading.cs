using System.Text.Json.Serialization;

namespace VitalsApi.Models;

public class VitalReading
{
    [JsonPropertyName("value")]
    public double? Value { get; set; }

    [JsonPropertyName("unit")]
    public string Unit { get; set; } = string.Empty;
}