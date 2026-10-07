using VitalsApi.Models;

namespace VitalsApi.Services;

public interface IVitalsExtractionService
{
    Task<VitalsExtractionResult> ExtractVitalsAsync(Stream imageStream, string contentType, CancellationToken cancellationToken = default);
}