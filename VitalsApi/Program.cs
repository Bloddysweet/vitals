using Microsoft.EntityFrameworkCore;
using Oracle.EntityFrameworkCore;
using VitalsApi.Data;
using VitalsApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();
builder.Services.AddScoped<IVitalsExtractionService, VitalsExtractionService>();
builder.Services.AddHttpClient<IHospitalPatientService, HospitalPatientService>();
builder.Services.AddDbContext<VitalsDbContext>(options =>
    options.UseOracle(builder.Configuration["Oracle:ConnectionString"], o =>
        o.UseOracleSQLCompatibility(OracleSQLCompatibility.DatabaseVersion19)));

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontendDev", policy =>
    {
        policy.WithOrigins(
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "null")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/openapi/v1.json", "VitalsApi v1");
    });
}

app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseCors("AllowFrontendDev");

app.UseAuthorization();

app.MapControllers();

app.Run();