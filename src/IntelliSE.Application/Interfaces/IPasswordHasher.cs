using IntelliSE.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Application.Interfaces
{
    public interface IPasswordHasher
    {
        string HashPassword(User user, string password);

        bool VerifyPassword(User user, string password);
    }
}
