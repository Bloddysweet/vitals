using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using VitalsApi.Data;
using VitalsApi.Models;

namespace VitalsApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HourlyVitalsController : ControllerBase
{
    private readonly VitalsDbContext _db;
    private readonly ILogger<HourlyVitalsController> _logger;

    public HourlyVitalsController(VitalsDbContext db, ILogger<HourlyVitalsController> logger)
    {
        _db = db;
        _logger = logger;
    }

    [HttpPost("confirm")]
    [ProducesResponseType(typeof(HourlyVitalEntry), StatusCodes.Status200OK)]
    public async Task<ActionResult<HourlyVitalEntry>> ConfirmEntry(ConfirmHourlyEntryRequest request)
    {
        var entryDateOnly = request.EntryDate.Date;

        // Oracle 11g doesn't support FETCH FIRST (added in 12c), so we avoid
        // FirstOrDefaultAsync — it would add that clause. Our unique index
        // guarantees at most one match, so pulling the list and taking the
        // first item in memory is safe and avoids the unsupported SQL.
        var matches = await _db.HourlyVitalEntries
            .Where(e =>
                e.PatientIdentifier == request.PatientIdentifier &&
                e.EntryDate == entryDateOnly &&
                e.Hour == request.Hour)
            .ToListAsync();
        var existing = matches.FirstOrDefault();

        var entry = existing ?? new HourlyVitalEntry
        {
            PatientIdentifier = request.PatientIdentifier,
            EntryDate = entryDateOnly,
            Hour = request.Hour
        };

        entry.Temperature = request.Temperature;
        entry.RespiratoryRate = request.RespiratoryRate;
        entry.HeartRate = request.HeartRate;
        entry.PulseRate = request.PulseRate;
        entry.Iabp = request.Iabp;
        entry.SpO2 = request.SpO2;
        entry.NibpSystolic = request.NibpSystolic;
        entry.NibpDiastolic = request.NibpDiastolic;
        entry.Map = request.Map;
        entry.Cvp = request.Cvp;
        entry.BloodGlucose = request.BloodGlucose;
        entry.Insulin = request.Insulin;
        entry.AdrenalineStarted = request.AdrenalineStarted;
        entry.AdrenalineInfused = request.AdrenalineInfused;
        entry.NoradrenalineStarted = request.NoradrenalineStarted;
        entry.NoradrenalineInfused = request.NoradrenalineInfused;
        entry.DopamineStarted = request.DopamineStarted;
        entry.DopamineInfused = request.DopamineInfused;
        entry.DobutamineStarted = request.DobutamineStarted;
        entry.DobutamineInfused = request.DobutamineInfused;
        entry.ParenteralNutrition = request.ParenteralNutrition;
        entry.RtFeeds = request.RtFeeds;
        entry.Iv1 = request.Iv1;
        entry.Iv2 = request.Iv2;
        entry.Drains = request.Drains;
        entry.Stool = request.Stool;
        entry.Urine = request.Urine;
        entry.VentMode = request.VentMode;
        entry.Fio2 = request.Fio2;
        entry.RateSet = request.RateSet;
        entry.RateSpont = request.RateSpont;
        entry.TidalSet = request.TidalSet;
        entry.TidalSpont = request.TidalSpont;
        entry.MinVolSet = request.MinVolSet;
        entry.MinVolSpont = request.MinVolSpont;
        entry.Pc = request.Pc;
        entry.Peep = request.Peep;
        entry.Ps = request.Ps;
        entry.Pip = request.Pip;
        entry.VentSpo2 = request.VentSpo2;
        entry.Etco2 = request.Etco2;
        entry.Abg = request.Abg;
        entry.GcsEye = request.GcsEye;
        entry.GcsMotor = request.GcsMotor;
        entry.GcsVerbal = request.GcsVerbal;
        entry.MotorUpperR = request.MotorUpperR;
        entry.MotorUpperL = request.MotorUpperL;
        entry.MotorLowerR = request.MotorLowerR;
        entry.MotorLowerL = request.MotorLowerL;
        entry.PupilR = request.PupilR;
        entry.PupilL = request.PupilL;
        entry.ExtractionConfidence = request.ExtractionConfidence;

        if (existing is null)
        {
            _db.HourlyVitalEntries.Add(entry);
        }

        await _db.SaveChangesAsync();
        _logger.LogInformation("Confirmed hourly entry for Patient {PatientIdentifier}, {Date} {Hour}",
            request.PatientIdentifier, entryDateOnly, request.Hour);

        return Ok(entry);
    }

    [HttpGet("patient/{patientIdentifier}/date/{date}")]
    [ProducesResponseType(typeof(List<HourlyVitalEntry>), StatusCodes.Status200OK)]
    public async Task<ActionResult<List<HourlyVitalEntry>>> GetEntriesForDate(string patientIdentifier, DateTime date)
    {
        var entries = await _db.HourlyVitalEntries
            .Where(e => e.PatientIdentifier == patientIdentifier && e.EntryDate == date.Date)
            .OrderBy(e => e.Hour)
            .ToListAsync();

        return Ok(entries);
    }

    [HttpDelete("{entryId:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteEntry(int entryId)
    {
        // Same reasoning as above — avoid FindAsync's single-row SQL pattern on 11g.
        var matches = await _db.HourlyVitalEntries.Where(e => e.EntryId == entryId).ToListAsync();
        var entry = matches.FirstOrDefault();
        if (entry is null)
        {
            return NotFound();
        }

        _db.HourlyVitalEntries.Remove(entry);
        await _db.SaveChangesAsync();
        _logger.LogInformation("Deleted hourly entry {EntryId}", entryId);
        return NoContent();
    }
}