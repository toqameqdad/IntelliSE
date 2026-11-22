using IntelliSE.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Application.Interfaces
{
    public interface IUserRepository
    {
        Task<User?> GetByEmailAsync(string email,CancellationToken cancellationToken = default);

        Task AddAsync(User user,CancellationToken cancellationToken = default);

        Task SaveChangesAsync(CancellationToken cancellationToken = default);
    }
}
