const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const loginEmail = document.getElementById("email").value.trim();
    const loginPassword = document.getElementById("password").value;

    const users = JSON.parse(localStorage.getItem("users")) || [];

    const user = users.find(function (user) {
        return user.email === loginEmail &&
               user.password === loginPassword;
    });

    if (user) {
        localStorage.setItem("loggedInUser", JSON.stringify(user));

        alert("Login successful!");

        window.location.href = "dashboard.html";
    } else {
        alert("Invalid email or password.");
    }
});

