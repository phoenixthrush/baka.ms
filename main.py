import os
import shutil
from urllib.parse import urljoin, urlparse

import niquests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ────────────────────── CONFIG ────────────────────── #

load_dotenv()

BASE_URL = "https://baka.ms/galleries/"
BASE_DOMAIN = "https://baka.ms"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/26.2 Safari/605.1.15"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

EXCLUDE = {"..", ".DS_Store", "favicon.ico", "v-proxy.js"}
SKIP_EXTENSIONS = {".ico", ".js", ".css", ".png", ".jpg", ".gif", ".txt"}

BLACKLIST = {
    item.strip() for item in os.getenv("BLACKLIST", "").split(",") if item.strip()
}

# ────────────────────── HELPERS ────────────────────── #


def is_blacklisted(text: str) -> bool:
    return any(bad in text for bad in BLACKLIST)


def is_directory_link(link: str) -> bool:
    return not link.endswith(".html") and not any(
        link.endswith(ext) for ext in SKIP_EXTENSIONS
    )


def relative_gallery_path(url: str) -> str | None:
    path = urlparse(url).path
    if not path.startswith("/galleries/"):
        return None
    return path[len("/galleries/") :]


# ────────────────────── NETWORK ────────────────────── #

session = niquests.Session()
session.headers.update(HEADERS)


def fetch_links(url: str) -> list[str]:
    response = session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    links = []

    anchors = soup.select("tr a[href]") or soup.find_all("a", href=True)

    for a in anchors:
        text = a.text.strip()
        if not text or text in EXCLUDE or is_blacklisted(text):
            continue

        href = a["href"]
        full_url = BASE_DOMAIN + href if href.startswith("/") else urljoin(url, href)
        links.append(full_url)

    return links


# ────────────────────── CRAWLER ────────────────────── #


def fetch_all_html_recursive(start_url: str) -> list[str]:
    visited = set()
    queue = [start_url.rstrip("/") + "/"]
    results = []

    while queue:
        current = queue.pop()
        if current in visited:
            continue

        visited.add(current)
        print(f"Scanning: {current}")

        try:
            for link in fetch_links(current):
                if link.endswith(".html"):
                    rel = relative_gallery_path(link)
                    if rel:
                        results.append(rel)
                elif is_directory_link(link):
                    queue.append(link)

        except Exception as e:
            print(f"Failed to scan {current}: {e}")

    return results


# ────────────────────── EXTRACTION ────────────────────── #


def extract_direct_links(html_url: str, output_dir: str) -> int:
    try:
        response = session.get(html_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        images = soup.select("img[data-idimg]")

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "links.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            for img in images:
                token = img["data-idimg"]
                reversed_token = token[::-1]
                f.write(
                    f"https://photos.baka.ms/photoservice/uwu/pull/"
                    f"{reversed_token}?{token}\n"
                )

        print(f"  {len(images)} images -> {output_file}")
        return len(images)

    except Exception as e:
        print(f"  Error extracting {html_url}: {e}")
        return 0


# ────────────────────── FILESYSTEM ────────────────────── #


def create_folder_structure():
    if os.path.exists("galleries"):
        shutil.rmtree("galleries")

    total_images = 0
    processed = 0

    with open("files.txt", encoding="utf-8") as f:
        for url in map(str.strip, f):
            if not url or is_blacklisted(url):
                continue

            processed += 1
            rel = relative_gallery_path(url)
            if not rel:
                continue

            folder = os.path.join("galleries", rel.replace(".html", ""))
            os.makedirs(folder, exist_ok=True)

            if url.endswith(".html"):
                total_images += extract_direct_links(url, folder)

    print(f"\nProcessed {processed} pages")
    print(f"Extracted {total_images} image links")


# ────────────────────── MAIN ────────────────────── #


def main():
    print("Fetching all gallery HTML files...")
    results = sorted(set(fetch_all_html_recursive(BASE_URL)))

    with open("files.txt", "w", encoding="utf-8") as f:
        for path in results:
            f.write(f"{BASE_URL}{path}\n")

    print(f"Saved {len(results)} URLs")
    create_folder_structure()


if __name__ == "__main__":
    main()
