
namespace IntelliSE.Application.DTOs.Auth;

public class LoginResponseDto
{
    public string AccessToken { get; set; } = string.Empty;

    public DateTime ExpiresAt { get; set; }

    public AuthUserDto User { get; set; } = null!;
}
