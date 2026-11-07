// Accessible mobile navigation.
document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector(".menu-toggle");
    const links = document.querySelector(".nav-links");
    if (!button || !links) return;

    button.addEventListener("click", () => {
        const open = links.classList.toggle("is-open");
        button.setAttribute("aria-expanded", String(open));
    });

    links.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            links.classList.remove("is-open");
            button.setAttribute("aria-expanded", "false");
        });
    });
});
