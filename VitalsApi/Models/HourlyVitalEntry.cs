using System.ComponentModel.DataAnnotations;

namespace VitalsApi.Models;

public class HourlyVitalEntry
{
    [Key]
    public int EntryId { get; set; }

    [Required, MaxLength(50)]
    public string PatientIdentifier { get; set; } = string.Empty; // hospital's ipatientid

    public DateTime EntryDate { get; set; }

    [Required, MaxLength(4)]
    public string Hour { get; set; } = string.Empty;

    public decimal? Temperature { get; set; }
    public int? RespiratoryRate { get; set; }
    public int? HeartRate { get; set; }
    public int? PulseRate { get; set; }

    [MaxLength(50)] public string? Iabp { get; set; }
    public int? SpO2 { get; set; }
    public int? NibpSystolic { get; set; }
    public int? NibpDiastolic { get; set; }
    public int? Map { get; set; }
    [MaxLength(50)] public string? Cvp { get; set; }

    public int? BloodGlucose { get; set; }
    [MaxLength(100)] public string? Insulin { get; set; }

    [MaxLength(50)] public string? AdrenalineStarted { get; set; }
    [MaxLength(50)] public string? AdrenalineInfused { get; set; }
    [MaxLength(50)] public string? NoradrenalineStarted { get; set; }
    [MaxLength(50)] public string? NoradrenalineInfused { get; set; }
    [MaxLength(50)] public string? DopamineStarted { get; set; }
    [MaxLength(50)] public string? DopamineInfused { get; set; }
    [MaxLength(50)] public string? DobutamineStarted { get; set; }
    [MaxLength(50)] public string? DobutamineInfused { get; set; }

    public int? ParenteralNutrition { get; set; }
    public int? RtFeeds { get; set; }
    public int? Iv1 { get; set; }
    public int? Iv2 { get; set; }

    public int? Drains { get; set; }
    [MaxLength(50)] public string? Stool { get; set; }
    public int? Urine { get; set; }

    [MaxLength(50)] public string? VentMode { get; set; }
    [MaxLength(50)] public string? Fio2 { get; set; }
    [MaxLength(50)] public string? RateSet { get; set; }
    [MaxLength(50)] public string? RateSpont { get; set; }
    [MaxLength(50)] public string? TidalSet { get; set; }
    [MaxLength(50)] public string? TidalSpont { get; set; }
    [MaxLength(50)] public string? MinVolSet { get; set; }
    [MaxLength(50)] public string? MinVolSpont { get; set; }
    [MaxLength(50)] public string? Pc { get; set; }
    [MaxLength(50)] public string? Peep { get; set; }
    [MaxLength(50)] public string? Ps { get; set; }
    [MaxLength(50)] public string? Pip { get; set; }
    [MaxLength(50)] public string? VentSpo2 { get; set; }
    [MaxLength(50)] public string? Etco2 { get; set; }
    [MaxLength(500)] public string? Abg { get; set; }

    public int? GcsEye { get; set; }
    public int? GcsMotor { get; set; }
    public int? GcsVerbal { get; set; }
    public bool MotorUpperR { get; set; }
    public bool MotorUpperL { get; set; }
    public bool MotorLowerR { get; set; }
    public bool MotorLowerL { get; set; }
    [MaxLength(20)] public string? PupilR { get; set; }
    [MaxLength(20)] public string? PupilL { get; set; }

    [MaxLength(20)] public string? ExtractionConfidence { get; set; }

    public DateTime ConfirmedAt { get; set; }
}