using Microsoft.EntityFrameworkCore;
using VitalsApi.Models;

namespace VitalsApi.Data;

public class VitalsDbContext : DbContext
{
    public VitalsDbContext(DbContextOptions<VitalsDbContext> options) : base(options)
    {
    }

    public DbSet<HourlyVitalEntry> HourlyVitalEntries => Set<HourlyVitalEntry>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<HourlyVitalEntry>(entity =>
        {
            entity.HasIndex(e => new { e.PatientIdentifier, e.EntryDate, e.Hour })
                  .IsUnique()
                  .HasDatabaseName("IX_HVE_Patient_Date_Hour");

            entity.Property(e => e.EntryId).ValueGeneratedOnAdd();
            entity.Property(e => e.Temperature).HasPrecision(5, 1);

            entity.Property(e => e.ConfirmedAt)
                  .HasDefaultValueSql("SYSTIMESTAMP")
                  .ValueGeneratedOnAdd();
        });
    }
}