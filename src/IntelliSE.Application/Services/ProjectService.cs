
using IntelliSE.Application.DTOs.Projects;
using IntelliSE.Application.Interfaces;
using IntelliSE.Domain.Entities;

namespace IntelliSE.Application.Services;

public class ProjectService : IProjectService
{
    private readonly IProjectRepository _projectRepository;

    public ProjectService(IProjectRepository projectRepository)
    {
        _projectRepository = projectRepository;
    }

    // Create Project
    public async Task<ProjectResponseDto> CreateAsync(
        int userId,
        CreateProjectRequestDto request,
        CancellationToken cancellationToken = default)
    {
        var project = new Project
        {
            Name = request.Name.Trim(),
            Description = request.Description.Trim(),
            UserId = userId,
            CreatedAtUtc = DateTime.UtcNow
        };

        await _projectRepository.AddAsync(
            project,
            cancellationToken);

        await _projectRepository.SaveChangesAsync(
            cancellationToken);

        return MapToDto(project);
    }

    // Get All Projects
    public async Task<List<ProjectResponseDto>> GetAllAsync(
        int userId,
        CancellationToken cancellationToken = default)
    {
        var projects = await _projectRepository.GetAllByUserIdAsync(
            userId,
            cancellationToken);

        return projects.Select(MapToDto).ToList();
    }

    // Get Project By ID
    public async Task<ProjectResponseDto?> GetByIdAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default)
    {
        var project = await _projectRepository.GetByIdAndUserIdAsync(
            projectId,
            userId,
            cancellationToken);

        if (project is null)
        {
            return null;
        }

        return MapToDto(project);
    }

    // Update Project
    public async Task<ProjectResponseDto?> UpdateAsync(
        int projectId,
        int userId,
        UpdateProjectRequestDto request,
        CancellationToken cancellationToken = default)
    {
        var project = await _projectRepository.GetByIdAndUserIdAsync(
            projectId,
            userId,
            cancellationToken);

        if (project is null)
        {
            return null;
        }

        project.Name = request.Name.Trim();
        project.Description = request.Description.Trim();
        project.UpdatedAtUtc = DateTime.UtcNow;

        await _projectRepository.SaveChangesAsync(
            cancellationToken);

        return MapToDto(project);
    }

    // Delete Project
    public async Task<bool> DeleteAsync(
        int projectId,
        int userId,
        CancellationToken cancellationToken = default)
    {
        var project = await _projectRepository.GetByIdAndUserIdAsync(
            projectId,
            userId,
            cancellationToken);

        if (project is null)
        {
            return false;
        }

        _projectRepository.Remove(project);

        await _projectRepository.SaveChangesAsync(
            cancellationToken);

        return true;
    }

    // Mapping
    private static ProjectResponseDto MapToDto(Project project)
    {
        return new ProjectResponseDto
        {
            Id = project.Id,
            Name = project.Name,
            Description = project.Description,
            CreatedAtUtc = project.CreatedAtUtc,
            UpdatedAtUtc = project.UpdatedAtUtc
        };
    }
}
