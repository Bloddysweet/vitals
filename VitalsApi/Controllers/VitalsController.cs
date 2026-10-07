using Microsoft.AspNetCore.Mvc;
using VitalsApi.Models;
using VitalsApi.Services;

namespace VitalsApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class VitalsController : ControllerBase
{
    private const long MaxFileSizeBytes = 10 * 1024 * 1024; // 10 MB

    private static readonly string[] AllowedContentTypes =
    {
        "image/png", "image/jpeg", "image/bmp", "image/webp"
    };

    private readonly IVitalsExtractionService _extractionService;
    private readonly ILogger<VitalsController> _logger;

    public VitalsController(IVitalsExtractionService extractionService, ILogger<VitalsController> logger)
    {
        _extractionService = extractionService;
        _logger = logger;
    }

    [HttpPost("extract")]
    [ProducesResponseType(typeof(VitalsExtractionResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<VitalsExtractionResult>> ExtractVitals(
        IFormFile image, CancellationToken cancellationToken)
    {
        if (image is null || image.Length == 0)
        {
            return BadRequest("No image file was uploaded.");
        }

        if (!AllowedContentTypes.Contains(image.ContentType))
        {
            return BadRequest($"Unsupported content type: {image.ContentType}");
        }

        if (image.Length > MaxFileSizeBytes)
        {
            return BadRequest($"Image too large ({image.Length / 1024 / 1024} MB). Maximum allowed is 10 MB.");
        }

        await using var stream = image.OpenReadStream();
        var result = await _extractionService.ExtractVitalsAsync(stream, image.ContentType, cancellationToken);

        if (!result.Success)
        {
            _logger.LogWarning("Vitals extraction failed: {Error}", result.ErrorMessage);
        }

        return Ok(result);
    }
}