using Microsoft.AspNetCore.Mvc;
using VitalsApi.Models;
using VitalsApi.Services;

namespace VitalsApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PatientsController : ControllerBase
{
    private readonly IHospitalPatientService _hospitalPatientService;
    private readonly ILogger<PatientsController> _logger;

    public PatientsController(IHospitalPatientService hospitalPatientService, ILogger<PatientsController> logger)
    {
        _hospitalPatientService = hospitalPatientService;
        _logger = logger;
    }

    [HttpGet("lookup/{id}")]
    [ProducesResponseType(typeof(PatientInfo), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status502BadGateway)]
    public async Task<ActionResult<PatientInfo>> Lookup(string id, CancellationToken cancellationToken)
    {
        PatientInfo? patient;
        try
        {
            patient = await _hospitalPatientService.LookupAsync(id, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Hospital patient API unreachable");
            return StatusCode(StatusCodes.Status502BadGateway, "Could not reach the hospital patient system.");
        }

        return patient is null ? NotFound() : Ok(patient);
    }
}