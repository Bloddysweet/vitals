namespace VitalsApi.Services;

public interface IHospitalPatientService
{
    Task<Models.PatientInfo?> LookupAsync(string input, CancellationToken cancellationToken = default);
}