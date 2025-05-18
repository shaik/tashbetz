import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, unquote

def crawl(start_url, max_pages=7000, output_file='hebrew_words.txt', save_interval=50):
    visited = set()
    queue = [start_url]
    words = set()
    pages_scanned = 0
    prefix = 'https://he.wikipedia.org/wiki/'

    while queue and pages_scanned < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        # Increment page count and prepare RTL title
        pages_scanned += 1
        if url.startswith(prefix):
            title = unquote(url[len(prefix):])
        else:
            title = unquote(url)
        # Wrap title in RTL embedding markers so it displays right-to-left
        rtl_title = '\u202B' + title + '\u202C'
        print(f"\r{pages_scanned}. Crawling: {rtl_title}", end='', flush=True)

        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"\nError loading {title}: {e}")
            continue

        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = soup.find('div', id='mw-content-text')
        text = content_div.get_text() if content_div else soup.get_text()

        # Extract Hebrew words (with possible apostrophes) and clean apostrophes
        raw_words = re.findall(r"[\u05D0-\u05EA']+", text)
        before_count = len(words)
        for w in raw_words:
            clean = re.sub(r"[^\u05D0-\u05EA]", "", w)
            if len(clean) > 1:
                words.add(clean)
        new_words = len(words) - before_count

        # Log summary and save snapshot every save_interval pages
        if pages_scanned % save_interval == 0:
            avg_new = len(words) / pages_scanned
            print(f"\nScanned {pages_scanned} pages, total words: {len(words)}, avg new/page: {avg_new:.2f}")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    for w in sorted(words):
                        f.write(w + '\n')
                print(f"Snapshot saved to {output_file}")
            except Exception as e:
                print(f"Error saving snapshot: {e}")

        # Enqueue internal Hebrew Wikipedia links
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/wiki/') and ':' not in href:
                full_url = urljoin(prefix, href.split('/wiki/')[-1])
                if full_url not in visited:
                    queue.append(full_url)

    # Final save and summary
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for w in sorted(words):
                f.write(w + '\n')
        print(f"\nScript finished. Total unique words: {len(words)}. Saved to {output_file}")
    except Exception as e:
        print(f"\nError saving final output: {e}")

if __name__ == '__main__':
    start_page = 'https://he.wikipedia.org/wiki/דף_ראשי'
    crawl(start_page)
