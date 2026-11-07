document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks = document.getElementById("nav-links");
  const hamburgerIcon = menuToggle?.querySelector(".hamburger-icon");
  const closeIcon = menuToggle?.querySelector(".close-icon");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      // Přepne zobrazení menu
      navLinks.classList.toggle("hidden");
      navLinks.classList.toggle("flex");

      // Přepne ikonky hamburger / křížek
      if (hamburgerIcon && closeIcon) {
        hamburgerIcon.classList.toggle("hidden");
        closeIcon.classList.toggle("hidden");
      }
    });
  }
});
