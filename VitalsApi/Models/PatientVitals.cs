using System.Text.Json.Serialization;

namespace VitalsApi.Models;

public class PatientVitals
{
    [JsonPropertyName("heart_rate")]
    public VitalReading HeartRate { get; set; } = new();

    [JsonPropertyName("blood_pressure_systolic")]
    public VitalReading BloodPressureSystolic { get; set; } = new();

    [JsonPropertyName("blood_pressure_diastolic")]
    public VitalReading BloodPressureDiastolic { get; set; } = new();

    [JsonPropertyName("spo2")]
    public VitalReading SpO2 { get; set; } = new();

    [JsonPropertyName("respiratory_rate")]
    public VitalReading RespiratoryRate { get; set; } = new();

    [JsonPropertyName("temperature")]
    public VitalReading Temperature { get; set; } = new();

    [JsonPropertyName("etco2")]
    public VitalReading Etco2 { get; set; } = new();

    [JsonPropertyName("mean_arterial_pressure")]
    public VitalReading MeanArterialPressure { get; set; } = new();
}