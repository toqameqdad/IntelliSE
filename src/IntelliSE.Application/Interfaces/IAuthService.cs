using IntelliSE.Application.DTOs.Auth;
using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Application.Interfaces
{
    public interface IAuthService
    {
        Task<AuthUserDto> RegisterAsync(RegisterRequestDto request, CancellationToken cancellationToken = default);

        Task<LoginResponseDto> LoginAsync(LoginRequestDto request,CancellationToken cancellationToken = default);
    }
}
