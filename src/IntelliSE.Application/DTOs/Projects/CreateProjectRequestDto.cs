
using System.ComponentModel.DataAnnotations;

namespace IntelliSE.Application.DTOs.Projects;

public class CreateProjectRequestDto
{
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;

    [Required]
    public string Description { get; set; } = string.Empty;
}
