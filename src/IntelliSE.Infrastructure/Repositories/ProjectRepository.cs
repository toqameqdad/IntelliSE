
using IntelliSE.Application.Interfaces;
using IntelliSE.Domain.Entities;
using IntelliSE.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace IntelliSE.Infrastructure.Repositories;

public class ProjectRepository : IProjectRepository
{
    private readonly IntelliSEDbContext _context;

    public ProjectRepository(IntelliSEDbContext context)
    {
        _context = context;
    }

    public async Task<List<Project>> GetAllByUserIdAsync(
        int userId,
        CancellationToken cancellationToken = default)
    {
        return await _context.Projects
            .AsNoTracking()
            .Where(p => p.UserId == userId)
            .OrderByDescending(p => p.CreatedAtUtc)
            .ToListAsync(cancellationToken);
    }

    public async Task<Project?> GetByIdAndUserIdAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default)
    {
        return await _context.Projects
            .FirstOrDefaultAsync(
                p => p.Id == projectId && p.UserId == userId,
                cancellationToken);
    }

    public async Task AddAsync(
        Project project,
        CancellationToken cancellationToken = default)
    {
        await _context.Projects.AddAsync(
            project,
            cancellationToken);
    }

    public void Remove(Project project)
    {
        _context.Projects.Remove(project);
    }

    public async Task SaveChangesAsync(
        CancellationToken cancellationToken = default)
    {
        await _context.SaveChangesAsync(cancellationToken);
    }
}
