namespace VitalsApi.Models;

public class ConfirmHourlyEntryRequest
{
    public string PatientIdentifier { get; set; } = string.Empty;
    public DateTime EntryDate { get; set; }
    public string Hour { get; set; } = string.Empty;

    public decimal? Temperature { get; set; }
    public int? RespiratoryRate { get; set; }
    public int? HeartRate { get; set; }
    public int? PulseRate { get; set; }

    public string? Iabp { get; set; }
    public int? SpO2 { get; set; }
    public int? NibpSystolic { get; set; }
    public int? NibpDiastolic { get; set; }
    public int? Map { get; set; }
    public string? Cvp { get; set; }

    public int? BloodGlucose { get; set; }
    public string? Insulin { get; set; }

    public string? AdrenalineStarted { get; set; }
    public string? AdrenalineInfused { get; set; }
    public string? NoradrenalineStarted { get; set; }
    public string? NoradrenalineInfused { get; set; }
    public string? DopamineStarted { get; set; }
    public string? DopamineInfused { get; set; }
    public string? DobutamineStarted { get; set; }
    public string? DobutamineInfused { get; set; }

    public int? ParenteralNutrition { get; set; }
    public int? RtFeeds { get; set; }
    public int? Iv1 { get; set; }
    public int? Iv2 { get; set; }

    public int? Drains { get; set; }
    public string? Stool { get; set; }
    public int? Urine { get; set; }

    public string? VentMode { get; set; }
    public string? Fio2 { get; set; }
    public string? RateSet { get; set; }
    public string? RateSpont { get; set; }
    public string? TidalSet { get; set; }
    public string? TidalSpont { get; set; }
    public string? MinVolSet { get; set; }
    public string? MinVolSpont { get; set; }
    public string? Pc { get; set; }
    public string? Peep { get; set; }
    public string? Ps { get; set; }
    public string? Pip { get; set; }
    public string? VentSpo2 { get; set; }
    public string? Etco2 { get; set; }
    public string? Abg { get; set; }

    public int? GcsEye { get; set; }
    public int? GcsMotor { get; set; }
    public int? GcsVerbal { get; set; }
    public bool MotorUpperR { get; set; }
    public bool MotorUpperL { get; set; }
    public bool MotorLowerR { get; set; }
    public bool MotorLowerL { get; set; }
    public string? PupilR { get; set; }
    public string? PupilL { get; set; }

    public string? ExtractionConfidence { get; set; }
}