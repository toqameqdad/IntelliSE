using IntelliSE.Application.DTOs.Auth;
using IntelliSE.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Application.Interfaces
{
    public interface IJwtTokenGenerator
    {
        GeneratedTokenDto GenerateToken(User user);
    }
}
