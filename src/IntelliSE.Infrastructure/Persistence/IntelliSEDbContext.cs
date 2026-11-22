
using IntelliSE.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace IntelliSE.Infrastructure.Persistence;

public class IntelliSEDbContext : DbContext
{
    public IntelliSEDbContext(DbContextOptions<IntelliSEDbContext> options):base(options)
    {
    }
    public DbSet<User> Users => Set<User>();
    public DbSet<Project> Projects => Set<Project>();
    public DbSet<Requirement> Requirements => Set<Requirement>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.ApplyConfigurationsFromAssembly(
            typeof(IntelliSEDbContext).Assembly);
    }
}
