
using IntelliSE.Application.Interfaces;
using IntelliSE.Domain.Entities;
using IntelliSE.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace IntelliSE.Infrastructure.Repositories;

public class UserRepository : IUserRepository
{
    private readonly IntelliSEDbContext _context;

    public UserRepository(IntelliSEDbContext context)
    {
        _context = context;
    }

    public async Task<User?> GetByEmailAsync(string email,CancellationToken cancellationToken = default)
    {
        return await _context.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(u => u.Email == email,cancellationToken);
    }

    public async Task AddAsync(User user,CancellationToken cancellationToken = default)
    {
        await _context.Users.AddAsync(user, cancellationToken);
    }

    public async Task SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        await _context.SaveChangesAsync(cancellationToken);
    }
}
