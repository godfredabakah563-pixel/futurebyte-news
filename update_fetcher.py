#!/usr/bin/env python3
"""update_fetcher.py

Fetch multiple RSS feeds (configured below), extract title, link, summary, published date, and an image URL.
If run on a server with internet, this script will download images into ./public/images/ and write articles.json
which the client page reads.

This script is designed to run in GitHub Actions (or any server), where internet access is available.
"""

import os, re, json, sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
import urllib.request
import xml.etree.ElementTree as ET

# CONFIG: list of feeds to aggregate
FEEDS = [
    {'url': 'https://techcrunch.com/feed/', 'source': 'TechCrunch'},
    {'url': 'https://www.theverge.com/rss/index.xml', 'source': 'The Verge'},
    {'url': 'http://feeds.bbci.co.uk/news/technology/rss.xml', 'source': 'BBC Technology'}
]

MAX_ITEMS = 30
OUT_DIR = 'public'
IMAGES_DIR = os.path.join(OUT_DIR, 'images')

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def fetch_url(url, timeout=20):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print('Failed fetching', url, '->', e, file=sys.stderr)
        return None

def extract_image_from_item(item, nsmap):
    # Common RSS patterns: media:content, enclosure, or an <img> in the description
    img = None
    # media:content
    for media in item.findall('.//{http://search.yahoo.com/mrss/}content'):
        if 'url' in media.attrib:
            return media.attrib.get('url')
    # enclosure
    enc = item.find('enclosure')
    if enc is not None and 'url' in enc.attrib:
        return enc.attrib.get('url')
    # look for img tag in description/html
    desc = item.findtext('description') or item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or ''
    m = re.search(r'<img[^>]+src=[\'\"]([^\'\"]+)', desc)
    if m:
        return urljoin('', m.group(1))
    # some feeds use media:thumbnail
    thumb = item.find('.//{http://search.yahoo.com/mrss/}thumbnail')
    if thumb is not None and 'url' in thumb.attrib:
        return thumb.attrib.get('url')
    return None

def parse_feed(feed_url, source_name):
    raw = fetch_url(feed_url)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except Exception as e:
        print('XML parse failed for', feed_url, e, file=sys.stderr)
        return []
    items = []
    for item in root.findall('.//item')[:MAX_ITEMS]:
        title = item.findtext('title') or 'No title'
        link = item.findtext('link') or ''
        pub = item.findtext('pubDate') or item.findtext('{http://purl.org/dc/elements/1.1/}date') or ''
        summary = item.findtext('description') or ''
        img = extract_image_from_item(item, None)
        items.append({'title': title.strip(), 'link': link.strip(), 'date': pub.strip(), 'summary': re.sub('<[^<]+?>', '', summary)[:500].strip(), 'image': img, 'source': source_name})
    return items

def safe_filename_from_url(url):
    if not url: return None
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name:
        name = parsed.netloc.replace('.', '_')
    name = re.sub(r'[^0-9A-Za-z._-]', '_', name)
    return name

def download_image(url):
    if not url: return None
    try:
        data = fetch_url(url)
        if not data: return None
        name = safe_filename_from_url(url)
        path = os.path.join(IMAGES_DIR, name)
        with open(path, 'wb') as f:
            f.write(data)
        return 'images/' + name
    except Exception as e:
        print('Image download failed', url, e, file=sys.stderr)
        return None

def main():
    print('Starting feed fetch at', datetime.utcnow().isoformat())
    all_items = []
    for f in FEEDS:
        try:
            items = parse_feed(f['url'], f.get('source', f['url']))
            print('Fetched', len(items), 'from', f['url'])
            all_items.extend(items)
        except Exception as e:
            print('Error fetching', f['url'], e, file=sys.stderr)
    def parsed_date(s):
        try:
            return datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %Z')
        except Exception:
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return datetime.min
    all_items.sort(key=lambda x: parsed_date(x.get('date','')), reverse=True)
    all_items = all_items[:MAX_ITEMS]
    for it in all_items:
        img = it.get('image')
        if img:
            local = download_image(img)
            if local:
                it['image_local'] = local
    out_path = os.path.join(OUT_DIR, 'articles.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print('Wrote', out_path, 'with', len(all_items), 'items.')

if __name__=='__main__':
    main()
