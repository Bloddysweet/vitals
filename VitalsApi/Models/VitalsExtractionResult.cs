namespace VitalsApi.Models;

public class VitalsExtractionResult
{
    public bool Success { get; set; }
    public bool IsMonitorImage { get; set; } = true;
    public PatientVitals? Vitals { get; set; }
    public string? Notes { get; set; }
    public string? Confidence { get; set; } // "high" | "medium" | "low"
    public string? RawResponse { get; set; }   // populated only if JSON parsing failed
    public string? ErrorMessage { get; set; }
}