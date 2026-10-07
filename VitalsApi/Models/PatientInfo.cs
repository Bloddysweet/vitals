namespace VitalsApi.Models;

public class PatientInfo
{
    public string Prno { get; set; } = string.Empty;
    public string IpatientId { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Sex { get; set; } = string.Empty;
    public int? Age { get; set; }
    public string? Bed { get; set; }
    public string? Department { get; set; }
    public string? DoctorName { get; set; }
    public DateTime? AdmittedOn { get; set; }
    public string? CaseType { get; set; }
}