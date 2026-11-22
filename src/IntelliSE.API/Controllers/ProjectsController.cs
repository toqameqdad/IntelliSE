
using IntelliSE.Application.DTOs.Projects;
using IntelliSE.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace IntelliSE.API.Controllers;

[ApiController]
[Route("api/projects")]
[Authorize]
public class ProjectsController : ControllerBase
{
    private readonly IProjectService _projectService;

    public ProjectsController(IProjectService projectService)
    {
        _projectService = projectService;
    }

    // Create Project
    [HttpPost]
    public async Task<ActionResult<ProjectResponseDto>> Create(
        [FromBody] CreateProjectRequestDto request,
        CancellationToken cancellationToken)
    {
        if (!TryGetCurrentUserId(out var userId))
            return Unauthorized();

        var result = await _projectService.CreateAsync(
            userId,
            request,
            cancellationToken);

        return CreatedAtAction(
            nameof(GetById),
            new { id = result.Id },
            result);
    }

    // Get All Projects
    [HttpGet]
    public async Task<ActionResult<List<ProjectResponseDto>>> GetAll(
        CancellationToken cancellationToken)
    {
        if (!TryGetCurrentUserId(out var userId))
            return Unauthorized();

        var result = await _projectService.GetAllAsync(
            userId,
            cancellationToken);

        return Ok(result);
    }

    // Get Project By ID
    [HttpGet("{id:int}")]
    public async Task<ActionResult<ProjectResponseDto>> GetById(
        int id,
        CancellationToken cancellationToken)
    {
        if (!TryGetCurrentUserId(out var userId))
            return Unauthorized();

        var result = await _projectService.GetByIdAsync(
            id,
            userId,
            cancellationToken);

        if (result is null)
            return NotFound(new { message = "Project not found." });

        return Ok(result);
    }

    // Update Project
    [HttpPut("{id:int}")]
    public async Task<ActionResult<ProjectResponseDto>> Update(
        int id,
        [FromBody] UpdateProjectRequestDto request,
        CancellationToken cancellationToken)
    {
        if (!TryGetCurrentUserId(out var userId))
            return Unauthorized();

        var result = await _projectService.UpdateAsync(
            id,
            userId,
            request,
            cancellationToken);

        if (result is null)
            return NotFound(new { message = "Project not found." });

        return Ok(result);
    }

    // Delete Project
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(
        int id,
        CancellationToken cancellationToken)
    {
        if (!TryGetCurrentUserId(out var userId))
            return Unauthorized();

        var deleted = await _projectService.DeleteAsync(
            id,
            userId,
            cancellationToken);

        if (!deleted)
            return NotFound(new { message = "Project not found." });

        return NoContent();
    }

    // Get Current User ID From JWT
    private bool TryGetCurrentUserId(out int userId)
    {
        userId = 0;

        var userIdClaim = User.FindFirstValue(
            ClaimTypes.NameIdentifier);

        return int.TryParse(userIdClaim, out userId);
    }
}
