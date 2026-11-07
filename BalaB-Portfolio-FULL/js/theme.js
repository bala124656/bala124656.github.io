// Shared light/dark theme. The choice persists across pages.
(() => {
    const key = "bala-portfolio-theme";
    let theme = "light";
    try {
        theme = localStorage.getItem(key) === "dark" ? "dark" : "light";
    } catch (_) {
        theme = "light";
    }
    document.documentElement.dataset.theme = theme;

    document.addEventListener("DOMContentLoaded", () => {
        const button = document.querySelector(".theme-toggle");
        const symbol = button?.querySelector(".theme-symbol");
        if (!button || !symbol) return;

        const update = () => {
            const dark = document.documentElement.dataset.theme === "dark";
            symbol.textContent = dark ? "☀" : "☾";
            button.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
            button.title = dark ? "Switch to light theme" : "Switch to dark theme";
        };

        update();
        button.addEventListener("click", () => {
            const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = next;
            try { localStorage.setItem(key, next); } catch (_) {}
            update();
        });
    });
})();
