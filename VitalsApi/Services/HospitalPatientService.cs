using System.Globalization;
using System.Text.Json;
using VitalsApi.Models;

namespace VitalsApi.Services;

public class HospitalPatientService : IHospitalPatientService
{
    private const string BaseUrl = "http://115.241.194.2/nmis_api/api/Patient/ipdetails";
    private readonly HttpClient _httpClient;
    private readonly ILogger<HospitalPatientService> _logger;

    public HospitalPatientService(HttpClient httpClient, ILogger<HospitalPatientService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<PatientInfo?> LookupAsync(string input, CancellationToken cancellationToken = default)
    {
        var url = $"{BaseUrl}?input={Uri.EscapeDataString(input)}";
        var response = await _httpClient.GetAsync(url, cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            _logger.LogWarning("Hospital patient API returned {Status}", response.StatusCode);
            return null;
        }

        var json = await response.Content.ReadAsStringAsync(cancellationToken);
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        // Their API returns success:true even for "not found" — data being null is the real signal.
        if (!root.TryGetProperty("data", out var dataEl) || dataEl.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        string? Get(string name) =>
            dataEl.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;

        DateTime? admittedOn = null;
        var admitRaw = Get("admitdate");
        if (!string.IsNullOrWhiteSpace(admitRaw) &&
            DateTime.TryParseExact(admitRaw, "dd-MMM-yyyy HH:mm:ss", CultureInfo.InvariantCulture, DateTimeStyles.None, out var parsed))
        {
            admittedOn = parsed;
        }

        int? age = int.TryParse(Get("agenew"), out var a) ? a : null;

        return new PatientInfo
        {
            Prno = Get("prno") ?? string.Empty,
            IpatientId = Get("ipatientid") ?? string.Empty,
            FullName = Get("firstname")?.Trim() ?? string.Empty,
            Sex = Get("sex") ?? string.Empty,
            Age = age,
            Bed = Get("bedid"),
            Department = Get("deptname"),
            DoctorName = Get("doctorname"),
            AdmittedOn = admittedOn,
            CaseType = Get("casetype")
        };
    }
}