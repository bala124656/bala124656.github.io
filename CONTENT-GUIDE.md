# Add Research entries and Blog posts with Python

You do not write the article inside Python code. You write a normal Markdown (`.md`) file, then run the Python publisher. Python turns that file into a web page and adds its card to the correct section.

## 1. One-time setup

Open the portfolio folder in VS Code. Open **Terminal → New Terminal**, then run:

```bash
python -m pip install -r requirements.txt
```

You only need to install these packages once on your computer.

## 2. Create a Blog post

1. Open `content/blog/`.
2. Copy `blog-post-template.md`.
3. Rename the copy to something descriptive, such as `my-first-ml-post.md`.
4. Open it and replace the example text with your article.

Example file:

```md
---
title: "What I Learned Building Linear Regression"
date: "2026-11-07"
category: "Machine Learning"
summary: "My notes on implementing linear regression and understanding its mathematics."
slug: "what-i-learned-linear-regression"
---

## Why I explored this

I wanted to understand how a model learns a relationship between input and output.

## The implementation

I implemented the model and tested it on a small dataset.

## What I learned

Explain what worked, what did not, and what you would improve.
```

The section between the first two `---` lines is metadata. The rest is the article itself.

## 3. Create a Research entry

1. Open `content/research/`.
2. Copy `research-entry-template.md`.
3. Rename the copy, for example `mechanistic-interpretability.md`.
4. Fill in the metadata and write your research notes below it.

Example:

```md
---
title: "An Introduction to Mechanistic Interpretability"
date: "2026-11-07"
topic: "AI Security"
status: "In progress"
summary: "Exploring how internal neural-network features and circuits can be studied."
slug: "mechanistic-interpretability-introduction"
---

## Research question

How can we inspect what a neural network has learned internally?

## Sources

- [Add the paper or article you read](https://example.com)

## Notes

Write the concepts in your own words. Separate what a source demonstrates from your own interpretation.

## Open questions

List what you want to investigate next.
```

## 4. Run the Python publisher

Save the Markdown file. In the VS Code terminal, make sure the terminal is at the portfolio's main folder (the folder containing `publisher`, `content` and `index.html`).

Run:

```bash
python publisher/build.py
```

Python will:
- read every Markdown file in `content/blog/` and `content/research/`;
- read its title, date, summary and slug from the YAML metadata;
- convert the Markdown writing into HTML;
- create article pages such as `blog-what-i-learned-linear-regression.html`;
- add the article cards to `blog.html` or `research.html`.

Refresh the website in Live Server. Your new entry should appear.

## 5. Publish the changes online

The generated HTML files are part of the website. Commit and push the Markdown file **and** the generated output to GitHub. The included GitHub Actions workflow also runs the Python publisher during deployment.

For the first GitHub Pages deployment, choose **Repository Settings → Pages → Build and deployment → Source → GitHub Actions**.

## Metadata rules

- `title`: the title readers see.
- `date`: use `YYYY-MM-DD`.
- `summary`: the short description shown on the listing page.
- `slug`: a unique web-safe ID, lowercase letters/numbers/hyphens only.
- `category` (Blog) or `topic` (Research): the label shown above the entry.
- Do not reuse a slug within the same section.
- Keep the opening and closing `---` lines.
- Do not edit generated article HTML manually. Edit the Markdown source, then run the Python build again.

## Useful Markdown formatting

```md
## Section heading

A paragraph with **bold text**, *italic text*, and a [link](https://example.com).

- A bullet point
- Another bullet point

> A quotation or important note.

```python
print("A code example inside your article")
```
```

**In short:** Markdown is where you write. Python is the publisher that converts your writing into website pages.
