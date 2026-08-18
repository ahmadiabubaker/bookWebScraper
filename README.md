# Books to Scrape

A web scraper that collects the full book catalogue from [books.toscrape.com](https://books.toscrape.com/) and saves it as a CSV file along with every book's cover image.

## What this code does

The site lists roughly 1000 books spread across 50 categories. The scraper walks the whole site and, for each book, opens its product page and pulls out the details.

`main.py` runs the whole job:

1. Reads the category list from the site's home page.
2. Visits every category, following the "next" link so that categories spanning several pages are covered in full.
3. Opens each book's product page and extracts ten fields: product page URL, UPC, title, price including tax, price excluding tax, quantity available, description, category, review rating, and image URL.
4. Writes every book as one row in `data/book_data.csv`.
5. Downloads each cover image into `images/<category>/`, so covers are grouped by the category the book belongs to.

All requests share a single `requests.Session`, which reuses the connection and keeps the run reasonably quick.

### Files

| File | Purpose |
| --- | --- |
| `main.py` | Entry point. Runs the scrape, writes the CSV, downloads the images. |
| `book_scraper.py` | The scraping logic: one book, one category, and the whole site. |
| `prototype_single_book.py` | A standalone script that scrapes only the first book on the home page. Written while working out the selectors, and kept as a small reference. Not used in production and not run when you run `main.py`. |
| `requirements.txt` | Pinned dependencies. |

### Output

* `data/book_data.csv`, one row per book plus a header row.
* `images/` holding one subfolder per category, each filled with cover images.

Neither is committed. `data/` and `images/` each contain their own `.gitignore` holding these two lines:

```
*
!.gitignore
```

That ignores everything in the folder except the ignore file itself. Since git tracks files rather than folders, keeping that one file committed is what makes the empty folder appear when the repository is cloned, while the scraped data stays out.

## How to run it

You need Python 3.8 or newer. Run these from the project root.

### 1. Create a virtual environment

This keeps the project's packages separate from your system Python.

```bash
python -m venv env
```

That creates an `env/` folder. You only do this once.

### 2. Activate it

On Windows, using Git Bash:

```bash
source env/Scripts/activate
```

On Windows, using PowerShell:

```powershell
env\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source env/bin/activate
```

Your prompt should now start with `(env)`. That is how you know the environment is active. You need to activate it in every new terminal session.

### 3. Install the requirements

With the environment active:

```bash
pip install -r requirements.txt
```

This installs `requests` and `beautifulsoup4` and the packages they depend on. Because the environment is active, they land inside `env/` rather than in your system Python.

### 4. Run the scraper

```bash
python main.py
```

The script prints nothing while it works. It makes over a thousand requests, so expect it to run for several minutes. When it finishes you will have `data/book_data.csv` and a populated `images/` folder.

To leave the virtual environment when you are done:

```bash
deactivate
```

## Notes

Re-running the script overwrites `data/book_data.csv` from scratch. Images are overwritten in place, so an interrupted run can safely be started again.

books.toscrape.com is a sandbox built specifically for practising web scraping, so it is fine to scrape repeatedly.
