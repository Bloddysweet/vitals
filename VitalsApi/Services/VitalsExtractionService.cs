using System.ClientModel;
using System.Text.Json;
using OpenAI;
using OpenAI.Chat;
using VitalsApi.Models;

namespace VitalsApi.Services;

public class VitalsExtractionService : IVitalsExtractionService
{
    private const string OpenRouterBaseUrl = "https://openrouter.ai/api/v1";
    private const string VisionModel = "google/gemma-3-27b-it";

    private const string ExtractionPrompt = """
    You are a medical data extraction assistant. First determine whether this image shows a medical patient monitor display (ICU/bedside vitals monitor). Then extract all visible patient vital signs.

    Return ONLY valid JSON in exactly this structure, no extra text or markdown:

    {
      "is_monitor_image": true,
      "patient_vitals": {
        "heart_rate": {"value": null, "unit": "bpm"},
        "blood_pressure_systolic": {"value": null, "unit": "mmHg"},
        "blood_pressure_diastolic": {"value": null, "unit": "mmHg"},
        "spo2": {"value": null, "unit": "%"},
        "respiratory_rate": {"value": null, "unit": "breaths/min"},
        "temperature": {"value": null, "unit": "\u00b0C"},
        "etco2": {"value": null, "unit": "mmHg"},
        "mean_arterial_pressure": {"value": null, "unit": "mmHg"}
      },
      "notes": "Any additional observations or unclear readings",
      "confidence": "high|medium|low"
    }

    Rules:
    - Set is_monitor_image to false if the image is not a medical patient monitor display (e.g. a random photo, document, or unrelated screen). If false, set every vital's value to null, and explain what the image actually shows in notes.
    - Set value to null if a vital sign is not visible, unreadable, or obscured by blur/glare/lighting - do not guess
    - Only extract what is actually visible
    - Return ONLY valid JSON, no extra text or markdown
    """;

    private readonly ChatClient _chatClient;
    private readonly ILogger<VitalsExtractionService> _logger;

    public VitalsExtractionService(IConfiguration configuration, ILogger<VitalsExtractionService> logger)
    {
        _logger = logger;

        var apiKey = configuration["OpenRouter:ApiKey"];
        if (string.IsNullOrWhiteSpace(apiKey))
        {
            throw new InvalidOperationException(
                "OpenRouter:ApiKey is not configured. Set it via Secret Manager (dotnet user-secrets).");
        }

        _chatClient = new ChatClient(
            model: VisionModel,
            credential: new ApiKeyCredential(apiKey),
            options: new OpenAIClientOptions { Endpoint = new Uri(OpenRouterBaseUrl) });
    }

    public async Task<VitalsExtractionResult> ExtractVitalsAsync(
        Stream imageStream, string contentType, CancellationToken cancellationToken = default)
    {
        using var memoryStream = new MemoryStream();
        await imageStream.CopyToAsync(memoryStream, cancellationToken);
        var imageBytes = BinaryData.FromBytes(memoryStream.ToArray());

        var messages = new List<ChatMessage>
        {
            new UserChatMessage(
                ChatMessageContentPart.CreateTextPart(ExtractionPrompt),
                ChatMessageContentPart.CreateImagePart(imageBytes, contentType))
        };

        var options = new ChatCompletionOptions
        {
            MaxOutputTokenCount = 1024,
            Temperature = 0.1f
        };

        ChatCompletion completion;
        try
        {
            completion = await _chatClient.CompleteChatAsync(messages, options, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "OpenRouter API call failed");
            return new VitalsExtractionResult
            {
                Success = false,
                ErrorMessage = $"Error calling OpenRouter API: {ex.Message}"
            };
        }

        var rawText = completion.Content.Count > 0 ? completion.Content[0].Text : string.Empty;
        var jsonText = StripMarkdownFences(rawText);

        try
        {
            using var doc = JsonDocument.Parse(jsonText);
            var root = doc.RootElement;

            var isMonitorImage = root.TryGetProperty("is_monitor_image", out var monitorElement)
                && monitorElement.GetBoolean();

            var vitals = root.TryGetProperty("patient_vitals", out var vitalsElement)
                ? JsonSerializer.Deserialize<PatientVitals>(vitalsElement.GetRawText())
                : null;

            var notes = root.TryGetProperty("notes", out var notesElement) ? notesElement.GetString() : null;
            var confidence = root.TryGetProperty("confidence", out var confElement) ? confElement.GetString() : null;

            if (vitals is null)
            {
                return new VitalsExtractionResult
                {
                    Success = false,
                    RawResponse = rawText,
                    ErrorMessage = "Response did not contain a patient_vitals object."
                };
            }

            return new VitalsExtractionResult
            {
                Success = true,
                IsMonitorImage = isMonitorImage,
                Vitals = vitals,
                Notes = notes,
                Confidence = confidence
            };
        }
        catch (JsonException ex)
        {
            _logger.LogWarning(ex, "Could not parse model response as JSON");
            return new VitalsExtractionResult
            {
                Success = false,
                RawResponse = rawText,
                ErrorMessage = "Could not parse structured data from the model response."
            };
        }
    }

    private static string StripMarkdownFences(string text)
    {
        text = text.Trim();
        if (!text.Contains("```"))
        {
            return text;
        }

        var parts = text.Split("```");
        var candidate = parts.Length > 1 ? parts[1] : text;
        if (candidate.StartsWith("json", StringComparison.OrdinalIgnoreCase))
        {
            candidate = candidate[4..];
        }
        return candidate.Trim();
    }
}