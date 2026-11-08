
#!/usr/bin/env python3

import os
import re
import json
import base64
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path
from html import escape

# ==========================================
# CONFIGURATION
# ==========================================

ROOT = Path(__file__).resolve().parent

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv(
    "GITHUB_REPO",
    "bala124656/bala124656.github.io"
)
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

API_BASE = "https://api.github.com"


# ==========================================
# INPUT HELPERS
# ==========================================

def ask(label, default=""):
    value = input(
        f"{label}" + (f" [{default}]" if default else "") + ": "
    ).strip()
    return value or default


def slugify(value):
    return re.sub(
        r"[^a-z0-9]+", "-", value.lower()
    ).strip("-")


# ==========================================
# MARKDOWN CONVERTER
# ==========================================

def inline_format(text):
    text = escape(text, quote=False)

    text = re.sub(
        r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text
    )
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text
    )
    text = re.sub(
        r"`(.+?)`", r"<code>\1</code>", text
    )
    text = re.sub(
        r"\[(.+?)\]\((https?://[^\s)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        text
    )

    return text


def markdown_to_html(source):
    output = []
    paragraph = []
    code = []
    in_code = False
    in_list = False
    in_quote = False

    def flush():
        if paragraph:
            output.append(
                f"<p>{inline_format(' '.join(paragraph))}</p>"
            )
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    def close_quote():
        nonlocal in_quote
        if in_quote:
            output.append("</blockquote>")
            in_quote = False

    for line in source.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            flush()
            close_list()
            close_quote()

            if in_code:
                output.append(
                    "<pre><code>"
                    + escape("\n".join(code))
                    + "</code></pre>"
                )
                code.clear()
                in_code = False
            else:
                in_code = True

            continue

        if in_code:
            code.append(line)
            continue

        if not stripped:
            flush()
            close_list()
            close_quote()
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)

        if heading:
            flush()
            close_list()
            close_quote()
            level = len(heading.group(1))
            output.append(
                f"<h{level}>{inline_format(heading.group(2))}</h{level}>"
            )

        elif re.match(r"^[-*]\s+", stripped):
            flush()
            close_quote()

            if not in_list:
                output.append("<ul>")
                in_list = True

            item = re.sub(r"^[-*]\s+", "", stripped)
            output.append(f"<li>{inline_format(item)}</li>")

        elif stripped.startswith(">"):
            flush()
            close_list()

            if not in_quote:
                output.append("<blockquote>")
                in_quote = True

            output.append(
                f"<p>{inline_format(stripped[1:].strip())}</p>"
            )

        else:
            close_list()
            close_quote()
            paragraph.append(stripped)

    flush()
    close_list()
    close_quote()

    if in_code:
        output.append(
            "<pre><code>" + escape("\n".join(code)) + "</code></pre>"
        )

    return "\n".join(output)


# ==========================================
# ARTICLE GENERATOR
# ==========================================

def make_article(title, summary, section, category, published, body):

    label = "RESEARCH JOURNAL" if section == "research" else "BLOG"
    back = "Research" if section == "research" else "Blog"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{escape(summary, quote=True)}">
<title>{escape(title)} | Bala B</title>

<script>
try {{
    const t = localStorage.getItem("bala-portfolio-theme");
    document.documentElement.dataset.theme =
        t === "dark" ? "dark" : "light";
}} catch(e) {{
    document.documentElement.dataset.theme = "light";
}}
</script>

<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="css/animations.css">
<link rel="stylesheet" href="css/responsive.css">
</head>

<body>

<header class="site-header">
<nav class="navigation" aria-label="Main navigation">

<div class="brand-group">
<a class="brand" href="index.html">BALA B</a>
<button class="theme-toggle" type="button"
aria-label="Switch theme" title="Switch theme">
<span class="theme-symbol" aria-hidden="true">☾</span>
</button>
</div>

<div class="nav-tools">
<button class="menu-toggle" type="button"
aria-expanded="false" aria-controls="primary-navigation">
Menu
</button>
</div>

<div class="nav-links" id="primary-navigation">
<a href="index.html">Home</a>
<a href="about.html">About</a>
<a href="expertise.html">Expertise &amp; Lab</a>
<a href="projects.html">Projects</a>
<a href="research.html">Research</a>
<a href="blog.html">Blog</a>
<a href="workspace.html">Developer Workspace</a>
<a href="contact.html">Contact</a>
</div>

</nav>
</header>

<main>

<section class="page-hero">
<p class="eyebrow">{label} / {escape(category)}</p>
<h1>{escape(title)}</h1>
<p class="hero-description">{escape(summary)}</p>
<p class="generated-meta">{escape(published)}</p>
</section>

<section class="content-section article-content">
{body}
<p>
<a class="text-link" href="{section}.html">
← Back to {back}
</a>
</p>
</section>

</main>

<footer class="site-footer">
<p>Designed and developed by Bala B.</p>
<a href="contact.html">Contact</a>
</footer>

<script src="js/theme.js"></script>
<script src="js/navigation.js"></script>
<script src="js/github.js"></script>
<script src="js/main.js"></script>

</body>
</html>
"""


# ==========================================
# GITHUB API
# ==========================================

def github_request(method, path, data=None):

    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Bala-Portfolio-Publisher"
    }

    payload = None

    if data is not None:
        payload = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API error {error.code}: {message}"
        )


def github_get_file(path):

    try:
        result = github_request("GET", path)
        content = base64.b64decode(
            result["content"]
        ).decode("utf-8")

        return content, result["sha"]

    except RuntimeError as error:
        if "404" in str(error):
            return None, None
        raise


def github_upload_file(path, content, message):

    existing_content, sha = github_get_file(path)

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": message,
        "content": encoded,
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha

    github_request("PUT", path, payload)


# ==========================================
# LISTING PAGE UPDATE
# ==========================================

def update_listing(section, slug, title, summary, category, published):

    listing_path = f"{section}.html"
    page, _ = github_get_file(listing_path)

    if page is None:
        raise RuntimeError(
            f"Could not find {listing_path} in GitHub."
        )

    start = f"<!-- GENERATED:{section}:START -->"
    end = f"<!-- GENERATED:{section}:END -->"

    if start not in page or end not in page:
        raise RuntimeError(
            f"Missing generated-entry markers in {listing_path}."
        )

    card = f"""
<article class="generated-entry">
<p class="generated-meta">{escape(published)} · {escape(category)}</p>
<h3><a href="{section}-{escape(slug, quote=True)}.html">{escape(title)}</a></h3>
<p>{escape(summary)}</p>
</article>
"""

    before, rest = page.split(start, 1)
    existing, after = rest.split(end, 1)

    # Replace an existing entry with the same slug.
    pattern = (
        r'<article\b[^>]*>.*?'
        + re.escape(f'{section}-{slug}.html')
        + r'.*?</article>'
    )

    if re.search(pattern, existing, flags=re.DOTALL):
        existing = re.sub(
            pattern,
            lambda _: card.strip(),
            existing,
            count=1,
            flags=re.DOTALL
        )
    else:
        existing = existing.rstrip() + "\n" + card

    updated_page = before + start + existing + end + after

    return updated_page


# ==========================================
# MAIN PUBLISHER
# ==========================================

def main():

    print("\n===================================")
    print("       BALA B | PUBLISHER")
    print("===================================\n")

    if not GITHUB_TOKEN:
        print("GitHub token not configured.")
        print("Follow the setup instructions before publishing.")
        return

    print("1. Blog post")
    print("2. Research entry")

    choice = ask("\nChoose 1 or 2")

    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    section = "blog" if choice == "1" else "research"

    title = ask("Title")

    if not title:
        print("Title is required.")
        return

    published = ask(
        "Date (YYYY-MM-DD)",
        date.today().isoformat()
    )

    try:
        date.fromisoformat(published)
    except ValueError:
        print("Invalid date.")
        return

    category = ask(
        "Category" if section == "blog" else "Topic",
        "Personal Journey" if section == "blog" else "Machine Learning"
    )

    summary = ask("Short description")

    if not summary:
        print("Description is required.")
        return

    slug = slugify(ask("URL slug", slugify(title)))

    if not slug:
        print("Invalid URL slug.")
        return

    article_path = f"{section}-{slug}.html"

    print("\nWrite your article below.")
    print("Markdown supported:")
    print("# Heading | ## Subheading | - List")
    print("**Bold** | *Italic* | `Code`")
    print("[Link text](https://example.com)")
    print("> Quote")
    print("Use ``` on separate lines for code blocks.")
    print("\nType END on its own line when finished.\n")

    lines = []

    while True:
        try:
            line = input()
        except EOFError:
            return

        if line.strip() == "END":
            break

        lines.append(line)

    source = "\n".join(lines).strip()

    if not source:
        print("No content entered.")
        return

    body = markdown_to_html(source)

    article = make_article(
        title,
        summary,
        section,
        category,
        published,
        body
    )

    try:
        updated_listing = update_listing(
            section,
            slug,
            title,
            summary,
            category,
            published
        )

    except Exception as error:
        print(f"\nCould not prepare listing: {error}")
        return

    print("\n===================================")
    print("              PREVIEW")
    print("===================================")
    print(f"Type: {section.upper()}")
    print(f"Title: {title}")
    print(f"Date: {published}")
    print(f"Category: {category}")
    print(f"Slug: {slug}")
    print(f"Summary: {summary}")
    print(f"Article file: {article_path}")
    print(f"Repository: {GITHUB_REPO}")
    print("===================================")

    confirm = ask(
        "\nPublish directly to GitHub? (yes/no)"
    ).lower()

    if confirm not in ("yes", "y"):
        print("Publishing cancelled.")
        return

    try:
        # Upload article first.
        github_upload_file(
            article_path,
            article,
            f"Publish/update {section}: {title}"
        )

        # Then update the listing page.
        github_upload_file(
            f"{section}.html",
            updated_listing,
            f"Update {section} listing: {title}"
        )

        print("\nSUCCESS! Your files are now on GitHub.")
        print("GitHub Actions will deploy your website.")
        print(f"Article: https://{GITHUB_REPO.split('/')[0]}.github.io/{article_path}")

    except Exception as error:
        print(f"\nPublishing failed: {error}")
        print("Check your token, repository and branch.")
        print("If the article uploaded but the listing failed,")
        print("the article may exist on GitHub without appearing in the list.")


if __name__ == "__main__":
    main()
