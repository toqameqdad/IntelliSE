using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace IntelliSE.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSystemAdminSeed : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.InsertData(
                table: "Users",
                columns: new[] { "Id", "CreatedAtUtc", "Email", "FirstName", "IsActive", "LastName", "PasswordHash", "Role", "UpdatedAtUtc" },
                values: new object[] { 10, new DateTime(2026, 11, 22, 0, 0, 0, 0, DateTimeKind.Utc), "etaf@intellise.com", "Etaf", true, "Amjad", "AQAAAAIAAYagAAAAEOOxzoTpN4QWwSI/7o4Oq2ha1JQw1mynpSpifxU/WBuetrOEkMrP2x2QoCW6bvWpyA==", 2, null });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "Users",
                keyColumn: "Id",
                keyValue: 10);
        }
    }
}
