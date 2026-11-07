#!/usr/bin/env python3
from datetime import date
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parent

def ask(label, default=""):
    value = input(f"{label}" + (f" [{default}]" if default else "") + ": ").strip()
    return value or default

def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def inline_format(text):
    text = text.replace(r"\*\*", "**").replace(r"\*", "*").replace(r"\`", "`")
    text = escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

def markdown_to_html(source, title="", summary="", published=""):
    lines = source.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**BLOG /") or stripped.startswith("**RESEARCH /"):
            continue
        if stripped in (f"# {title}", title, summary, published):
            continue
        if "Back to Blog" in stripped or "Back to Research" in stripped:
            continue
        cleaned.append(line)

    out, paragraph, code, in_code, in_list = [], [], [], False, False

    def flush():
        if paragraph:
            out.append(f"<p>{inline_format(' '.join(paragraph).strip())}</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in cleaned:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            close_list()
            if in_code:
                out.append("<pre><code>" + escape("\n".join(code)) + "</code></pre>")
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
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush()
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline_format(heading.group(2))}</h{level}>")
        elif re.match(r"^[-*]\s+", stripped):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^[-*]\s+", "", stripped)
            out.append(f"<li>{inline_format(item)}</li>")
        else:
            close_list()
            paragraph.append(stripped)

    flush()
    close_list()
    if in_code:
        out.append("<pre><code>" + escape("\n".join(code)) + "</code></pre>")
    return "\n".join(out)

def make_article(title, summary, section, category, published, body):
    label = "RESEARCH JOURNAL" if section == "research" else "BLOG"
    back = "Research" if section == "research" else "Blog"
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{escape(summary, quote=True)}">
<title>{escape(title)} | Bala B</title>
<script>try {{ const t=localStorage.getItem("bala-portfolio-theme"); document.documentElement.dataset.theme=t==="dark"?"dark":"light"; }} catch(e) {{ document.documentElement.dataset.theme="light"; }}</script>
<link rel="stylesheet" href="css/style.css"><link rel="stylesheet" href="css/animations.css"><link rel="stylesheet" href="css/responsive.css">
</head><body>
<header class="site-header"><nav class="navigation" aria-label="Main navigation">
<div class="brand-group"><a class="brand" href="index.html">BALA B</a><button class="theme-toggle" type="button" aria-label="Switch theme" title="Switch theme"><span class="theme-symbol" aria-hidden="true">☾</span></button></div>
<div class="nav-tools"><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation">Menu</button></div>
<div class="nav-links" id="primary-navigation">
<a href="index.html">Home</a><a href="about.html">About</a><a href="expertise.html">Expertise &amp; Lab</a><a href="projects.html">Projects</a>
<a href="research.html">Research</a><a href="blog.html">Blog</a><a href="workspace.html">Developer Workspace</a><a href="contact.html">Contact</a>
</div></nav></header>
<main><section class="page-hero"><p class="eyebrow">{label} / {escape(category)}</p><h1>{escape(title)}</h1><p class="hero-description">{escape(summary)}</p><p class="generated-meta">{escape(published)}</p></section>
<section class="content-section article-content">{body}<p><a class="text-link" href="{section}.html">← Back to {back}</a></p></section></main>
<footer class="site-footer"><p>Designed and developed by Bala B.</p><a href="contact.html">Contact</a></footer>
<script src="js/theme.js"></script><script src="js/navigation.js"></script><script src="js/github.js"></script><script src="js/main.js"></script>
</body></html>'''

def main():
    print("\nBALA B | PORTFOLIO PUBLISHER")
    print("1. Blog post")
    print("2. Research entry")
    choice = ask("Choose 1 or 2")
    if choice not in ("1", "2"):
        print("Invalid choice.")
        return
    section = "blog" if choice == "1" else "research"
    title = ask("Title")
    if not title:
        print("Title is required.")
        return
    published = ask("Date (YYYY-MM-DD)", date.today().isoformat())
    try:
        date.fromisoformat(published)
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return
    category = ask("Category" if section == "blog" else "Topic",
                   "Personal Journey" if section == "blog" else "Machine Learning")
    summary = ask("Short description")
    if not summary:
        print("Description is required.")
        return
    slug = slugify(ask("URL slug", slugify(title)))
    if not slug:
        print("Invalid URL slug.")
        return
    article_path = ROOT / f"{section}-{slug}.html"
    if article_path.exists():
        print("That slug already exists. Choose another one.")
        return
    print("\nWrite ONLY the article body below.")
    print("Do not repeat the title, summary, date or back-to-blog link.")
    print("Formatting: # Heading, ## Subheading, - bullet, **bold**, *italic*.")
    print("You can paste the complete draft too; repeated header lines are filtered.")
    print("Type END on its own line when finished.\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    source = "\n".join(lines).strip()
    if not source:
        print("No content entered. Nothing published.")
        return
    body = markdown_to_html(source, title, summary, published)
    article_path.write_text(make_article(title, summary, section, category, published, body), encoding="utf-8")
    listing_path = ROOT / f"{section}.html"
    page = listing_path.read_text(encoding="utf-8")
    start, end = f"<!-- GENERATED:{section}:START -->", f"<!-- GENERATED:{section}:END -->"
    if start not in page or end not in page:
        article_path.unlink(missing_ok=True)
        print("Could not find the listing insertion area.")
        return
    before, rest = page.split(start, 1)
    existing, after = rest.split(end, 1)
    card = f'''
<article class="generated-entry">
<p class="generated-meta">{escape(published)} · {escape(category)}</p>
<h3><a href="{escape(article_path.name, quote=True)}">{escape(title)}</a></h3>
<p>{escape(summary)}</p>
</article>
'''
    listing_path.write_text(before + start + existing + card + end + after, encoding="utf-8")
    print(f"\nPublished! Created {article_path.name} and updated {listing_path.name}.")
    print("Refresh Live Server to see it.")

if __name__ == "__main__":
    main()
