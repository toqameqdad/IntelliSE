
/* 1. Global Variables */

const navbar = document.querySelector(".navbar");
const navLinks = document.querySelectorAll(".nav-links a");
const primaryButtons = document.querySelectorAll(".primary-button");
const navButton = document.querySelector(".nav-button");


/* 2. Smooth Navigation */

navLinks.forEach(function(link) {

    link.addEventListener("click", function(event) {

        const targetId = link.getAttribute("href");

        if (targetId && targetId.startsWith("#")) {

            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                event.preventDefault();

                targetSection.scrollIntoView({
                    behavior: "smooth"
                });
            }
        }

    });

});


/* 3. Navigation Button */

if (navButton) {

    navButton.addEventListener("click", function(event) {

        const targetId = navButton.getAttribute("href");

        if (targetId && targetId.startsWith("#")) {

            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                event.preventDefault();

                targetSection.scrollIntoView({
                    behavior: "smooth"
                });
            }
        }

    });

}


/* 4. Primary Button */

primaryButtons.forEach(function(button) {

    button.addEventListener("click", function(event) {

        const targetId = button.getAttribute("href");

        if (targetId && targetId !== "#" && targetId.startsWith("#")) {

            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                event.preventDefault();

                targetSection.scrollIntoView({
                    behavior: "smooth"
                });
            }
        }

    });

});


/* 5. Navbar Scroll Effect */

window.addEventListener("scroll", function() {

    if (navbar) {

        if (window.scrollY > 50) {
            navbar.style.transition = "all 0.3s ease";
        }

    }

});


/* 6. Welcome Message*/

console.log("Welcome to IntelliSE!");
console.log("IntelliSE Frontend is running successfully.");

/* 7. Active Navigation Link */

navLinks.forEach(function(link) {

    link.addEventListener("click", function() {

        navLinks.forEach(function(item) {
            item.classList.remove("active");
        });

        link.classList.add("active");

    });

});

/* 8. Active Navigation on Scroll */

const sections = document.querySelectorAll("main section");

window.addEventListener("scroll", function() {

    let currentSection = "";

    sections.forEach(function(section) {

        const sectionTop = section.offsetTop;

        if (window.scrollY >= sectionTop - 150) {
            currentSection = section.getAttribute("id");
        }

    });

    navLinks.forEach(function(link) {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + currentSection) {
            link.classList.add("active");
        }

    });

});
window.dispatchEvent(new Event("scroll"));
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const loginEmail = document.getElementById("loginEmail").value.trim();
        const loginPassword = document.getElementById("loginPassword").value;

        const users = JSON.parse(localStorage.getItem("users")) || [];

        const user = users.find(function (user) {
            return user.email === loginEmail &&
                   user.password === loginPassword;
        });

        if (user) {
            localStorage.setItem("loggedInUser", JSON.stringify(user));

            alert("Login successful!");

            window.location.href = "index.html";
        } else {
            alert("Invalid email or password.");
        }
    });
}

const logoutButton = document.getElementById("logoutButton");

if (logoutButton) {
    logoutButton.addEventListener("click", function () {
        localStorage.removeItem("loggedInUser");

        window.location.href = "login.html";
    });
}


