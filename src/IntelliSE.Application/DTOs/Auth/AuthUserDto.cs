
namespace IntelliSE.Application.DTOs.Auth;

public class AuthUserDto
{
    public int Id { get; set; }

    public string FirstName { get; set; } = string.Empty;

    public string LastName { get; set; } = string.Empty;

    public string FullName => $"{FirstName} {LastName}";

    public string Email { get; set; } = string.Empty;

    public string Role { get; set; } = string.Empty;
}
