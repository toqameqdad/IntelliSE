using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Domain.Entities
{
    public class Project
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int UserId { get; set; }
        public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
        public DateTime? UpdatedAtUtc { get; set; }
        public User User { get; set; } = null!;
        public ICollection<Requirement> Requirements { get; set; } = new List<Requirement>();
    }
}
