using IntelliSE.Domain.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace IntelliSE.Domain.Entities
{
    public class Requirement
    {
        public int Id { get; set; }
        public int ProjectId { get; set; }
        public Project Project { get; set; } = null!;
        public RequirementType Type { get; set; }
        public string Description { get; set; } = string.Empty;
        public RequirementPriority Priority { get; set; }
        public string Rationale { get; set; } = string.Empty;
        public bool IsApproved { get; set; } = false;
        public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
        public DateTime? UpdatedAtUtc { get; set; }
      
    }
}
