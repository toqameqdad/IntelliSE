
using IntelliSE.Domain.Entities;
using IntelliSE.Domain.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace IntelliSE.Infrastructure.Persistence.Configurations;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("Users");

        builder.HasKey(u => u.Id);

        builder.Property(u => u.FirstName)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(u => u.LastName)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(u => u.Email)
            .IsRequired()
            .HasMaxLength(256);

        builder.HasIndex(u => u.Email)
            .IsUnique();

        builder.Property(u => u.PasswordHash)
            .IsRequired()
            .HasMaxLength(500);

        builder.Property(u => u.Role)
            .IsRequired()
            .HasConversion<int>();

        builder.Property(u => u.IsActive)
            .IsRequired()
            .HasDefaultValue(true);

        builder.Property(u => u.CreatedAtUtc)
            .IsRequired();

        builder.Property(u => u.UpdatedAtUtc)
            .IsRequired(false);

        builder.HasData(
            new User
            {
    Id = 10,
    FirstName = "Etaf",
    LastName = "Amjad",
    Email = "etaf@intellise.com",
    PasswordHash = "AQAAAAIAAYagAAAAEOOxzoTpN4QWwSI/7o4Oq2ha1JQw1mynpSpifxU/WBuetrOEkMrP2x2QoCW6bvWpyA==",
    Role = UserRole.Admin,
    IsActive = true,
    CreatedAtUtc = new DateTime(
        2026, 11, 22, 0, 0, 0, DateTimeKind.Utc),
    UpdatedAtUtc = null
});
    }
}
