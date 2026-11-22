
using IntelliSE.Application.DTOs.Projects;

namespace IntelliSE.Application.Interfaces;

public interface IProjectService
{
    Task<ProjectResponseDto> CreateAsync(
        int userId,
        CreateProjectRequestDto request,
        CancellationToken cancellationToken = default);

    Task<List<ProjectResponseDto>> GetAllAsync(
        int userId,
        CancellationToken cancellationToken = default);

    Task<ProjectResponseDto?> GetByIdAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default);

    Task<ProjectResponseDto?> UpdateAsync(
        int projectId,
        int userId,
        UpdateProjectRequestDto request,
        CancellationToken cancellationToken = default);

    Task<bool> DeleteAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default);
}
