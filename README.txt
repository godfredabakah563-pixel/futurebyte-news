Futurebyte News — Auto-updating site bundle

You requested an auto-updating website (B), real images (a), real articles pulled from live tech RSS feeds (ii).
This ZIP contains the site and automation needed to run everything on GitHub Pages using GitHub Actions.

Files included:
- index.html         (client site that reads public/articles.json)
- styles.css
- update_fetcher.py  (aggregates RSS feeds, downloads images to public/images/, writes public/articles.json)
- .github/workflows/update-and-deploy.yml  (workflow to run fetcher and deploy to Pages)
- README.txt         (this file)

Important notes:
- This bundle does NOT include downloaded external images (can't fetch and embed them here). Instead, the update_fetcher.py included WILL download images when it runs on a server (e.g., GitHub Actions).
- Steps to deploy (short):
  1. Create a new public GitHub repository (e.g., futurebyte-news).
  2. Upload ALL files from this ZIP to the repository root (preserve the .github folder).
  3. In the repository, go to Actions -> Workflows and run 'Update articles and deploy to Pages' manually once to test.
  4. After successful run, the site will be published via GitHub Pages. The workflow runs every 30 minutes by schedule to refresh articles/images.
  5. Embed the published Pages URL into Google Sites (Insert -> Embed -> By URL) if desired.
- If you'd prefer I produce a ZIP that actually includes image files embedded, I can do that — but I would need either:
  - You to provide the exact image files, OR
  - Permission to fetch and bundle images from specific URLs (I cannot fetch them into the ZIP in this environment). Instead, running the included workflow on GitHub will download and include images automatically.

Feeds configured (you can edit in update_fetcher.py):
- https://techcrunch.com/feed/
- https://www.theverge.com/rss/index.xml
- http://feeds.bbci.co.uk/news/technology/rss.xml

If you want me to:
- Customize the layout or change number of articles, tell me now.
- Or, I can create the ZIP now (without external images) and provide it for download — ready?
