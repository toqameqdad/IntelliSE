
using IntelliSE.Domain.Entities;

namespace IntelliSE.Application.Interfaces;

public interface IProjectRepository
{
    Task<List<Project>> GetAllByUserIdAsync(
        int userId,
        CancellationToken cancellationToken = default);

    Task<Project?> GetByIdAndUserIdAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default);

    Task AddAsync(
        Project project,
        CancellationToken cancellationToken = default);

    void Remove(Project project);

    Task SaveChangesAsync(
        CancellationToken cancellationToken = default);
}
