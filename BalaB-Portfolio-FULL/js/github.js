// Public GitHub integrations for Bala B.
document.addEventListener("DOMContentLoaded", () => {
    const username = "bala124656";
    const headers = { "Accept": "application/vnd.github+json" };

    async function githubJSON(url) {
        const response = await fetch(url, { headers });
        if (!response.ok) throw new Error(`GitHub API request failed (${response.status})`);
        return response.json();
    }

    // Refresh the circular avatar beside the homepage name.
    const avatar = document.getElementById("github-avatar");
    if (avatar) {
        githubJSON(`https://api.github.com/users/${username}`)
            .then(profile => { if (profile.avatar_url) avatar.src = profile.avatar_url; })
            .catch(error => console.warn("GitHub avatar refresh failed:", error));
    }

    function prettyName(path) {
        return path.split("/").pop().replace(/\.[^.]+$/, "")
            .replace(/[_-]+/g, " ")
            .replace(/\b\w/g, letter => letter.toUpperCase());
    }

    function addFileCard(container, file, repo) {
        const card = document.createElement("article");
        card.className = "repo-card";
        const heading = document.createElement("h3");
        const link = document.createElement("a");
        const encodedPath = file.path.split("/").map(encodeURIComponent).join("/");
        link.href = `https://github.com/${username}/${repo}/blob/main/${encodedPath}`;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = prettyName(file.path);
        heading.append(link);

        const description = document.createElement("p");
        description.textContent = file.path.includes("/")
            ? file.path.substring(0, file.path.lastIndexOf("/"))
            : "Repository root";

        const meta = document.createElement("div");
        meta.className = "repo-meta";
        meta.textContent = `${file.path.endsWith(".py") ? "Python" : "Notebook / Markdown"} · ${Math.max(1, Math.round((file.size || 0) / 1024))} KB`;
        card.append(heading, description, meta);
        container.append(card);
    }

    async function loadRepoFiles(repo, containerId, statusId, filter) {
        const container = document.getElementById(containerId);
        const status = document.getElementById(statusId);
        if (!container || !status) return;
        try {
            const tree = await githubJSON(`https://api.github.com/repos/${username}/${repo}/git/trees/main?recursive=1`);
            const files = (tree.tree || []).filter(item => item.type === "blob" && filter(item.path));
            container.replaceChildren();
            if (!files.length) {
                status.textContent = "No matching source files found.";
                return;
            }
            files.forEach(file => addFileCard(container, file, repo));
            status.textContent = `${files.length} files loaded directly from ${repo}.`;
            if (tree.truncated) status.textContent += " GitHub returned a partial listing.";
        } catch (error) {
            status.textContent = `Couldn't load ${repo} right now. Use the repository link below to view it.`;
            console.error(`Failed to load ${repo}:`, error);
        }
    }

    loadRepoFiles("ML-concepts", "ml-concepts-list", "ml-repo-status",
        path => /\.(py|ipynb|md)$/i.test(path) && !path.toLowerCase().includes("readme"));
    loadRepoFiles("Python-Lab", "python-lab-list", "python-repo-status",
        path => /\.py$/i.test(path));

    // Searchable public repository browser on Developer Workspace.
    const repoGrid = document.getElementById("github-repositories");
    if (!repoGrid) return;
    const status = document.getElementById("repo-status");
    const search = document.getElementById("repo-search");
    const sort = document.getElementById("repo-sort");
    let repos = [];

    function renderRepos() {
        const query = (search?.value || "").trim().toLowerCase();
        const mode = sort?.value || "updated";
        const list = repos.filter(repo =>
            [repo.name, repo.description || "", repo.language || ""].join(" ").toLowerCase().includes(query));
        list.sort((a, b) => {
            if (mode === "stars") return b.stargazers_count - a.stargazers_count;
            if (mode === "name") return a.name.localeCompare(b.name);
            return new Date(b.updated_at) - new Date(a.updated_at);
        });
        repoGrid.replaceChildren();
        if (!list.length) {
            const empty = document.createElement("p");
            empty.className = "muted";
            empty.textContent = "No repositories match this search.";
            repoGrid.append(empty);
            return;
        }
        list.forEach(repo => {
            const card = document.createElement("article");
            card.className = "repo-card";
            const heading = document.createElement("h3");
            const link = document.createElement("a");
            link.href = repo.html_url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = repo.name;
            heading.append(link);
            const description = document.createElement("p");
            description.textContent = repo.description || "No description provided.";
            const meta = document.createElement("div");
            meta.className = "repo-meta";
            const date = new Date(repo.updated_at);
            meta.textContent = [repo.language || "Language not specified", `★ ${repo.stargazers_count}`,
                `Forks ${repo.forks_count}`, Number.isNaN(date.getTime()) ? "Date unavailable" :
                `Updated ${date.toLocaleDateString()}`].join(" · ");
            card.append(heading, description, meta);
            repoGrid.append(card);
        });
    }

    githubJSON(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated&type=owner`)
        .then(data => {
            if (!Array.isArray(data)) throw new Error("Unexpected GitHub API response");
            repos = data;
            if (status) status.textContent = `${repos.length} public repositories found for @${username}.`;
            renderRepos();
            search?.addEventListener("input", renderRepos);
            sort?.addEventListener("change", renderRepos);
        })
        .catch(error => {
            if (status) status.textContent = "GitHub repositories could not be loaded right now. Refresh to try again.";
            console.error(error);
        });
});
