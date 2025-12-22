import os
import shutil

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/26.2 Safari/605.1.15"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BASE_URL = "https://baka.ms/galleries/"
EXCLUDE = {"..", ".DS_Store", "favicon.ico", "v-proxy.js"}


def fetch_links(url):
    """Fetch valid href links from a page."""
    with requests.Session() as session:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Try table rows first (default format)
    links = []
    for a in soup.select("tr a[href]"):
        if a.text.strip() not in EXCLUDE:
            href = str(a["href"])
            current_url = url if url.endswith("/") else url + "/"
            joined = urljoin(current_url, href)
            links.append(joined)

    # If no table links found, try all <a> tags (for pages like belle_delphine)
    if not links:
        for a in soup.find_all("a", href=True):
            if a.text.strip() and not any(exclude in a.text for exclude in [".."]):
                href = str(a["href"])
                if href.startswith("/"):
                    links.append("https://baka.ms" + href)
                else:
                    links.append(urljoin(url, href))

    return links


def fetch_all_html_recursive(start_url, visited=None):
    """Recursively fetch all HTML files from all subdirectories."""
    if visited is None:
        visited = set()

    results = []
    urls_to_visit = [start_url.rstrip("/") + "/"]

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"Scanning: {current_url}")

        try:
            links = fetch_links(current_url)
            print(f"Found {len(links)} links")

            for link in links:
                print(f"  Link: {link}")
                # Check if it's an HTML file
                if link.endswith(".html"):
                    rel_path = relative_path(link)
                    if rel_path:
                        results.append(rel_path)
                # Check if it's a directory (doesn't end with .html and not a file)
                elif not any(
                    link.endswith(ext)
                    for ext in [".ico", ".js", ".css", ".png", ".jpg", ".gif", ".txt"]
                ):
                    # It's likely a directory, add to visit queue
                    urls_to_visit.append(link)

        except Exception:
            continue

    return results


def relative_path(url):
    """Convert full URL to relative path after /galleries/"""
    path = urlparse(url).path
    if not path.startswith("/galleries/"):
        return None
    return path[len("/galleries/") :]  # keeps artist/filename.html


def extract_direct_links(html_url, output_dir):
    """Extract direct image and video links from HTML page and save to text file"""
    try:
        response = requests.get(html_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        direct_links = []

        # Find all images with data-idimg attributes (photos)
        images = soup.find_all("img", {"data-idimg": True})
        for img in images:
            data_id = img.get("data-idimg")
            if data_id:
                # Apply the token reversal pattern
                reversed_token = data_id[::-1]
                # Construct direct URL for photos
                direct_url = f"https://photos.baka.ms/photoservice/uwu/pull/{reversed_token}?{data_id}"
                direct_links.append(direct_url)

        # Save direct links to text file
        output_file = f"{output_dir}/links.txt"

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            for link in direct_links:
                f.write(f"{link}\n")

        print(f"  Extracted {len(direct_links)} direct links to {output_file}")
        print(f"  Photos found: {len(images)} (video links skipped)")
        return len(direct_links)

    except Exception as e:
        print(f"  Error extracting links from {html_url}: {e}")
        return 0


def create_folder_structure():
    """Create folder structure where each HTML file becomes a directory named after a file"""
    print("\nCreating folder structure where each HTML file becomes a directory...")

    # Remove existing galleries directory if it exists
    if os.path.exists("galleries"):
        shutil.rmtree("galleries")
        print("Removed existing galleries directory")

    # Read URLs from files.txt and create directories
    total_images = 0
    processed_count = 0

    with open("files.txt", "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            processed_count += 1

            # Extract path from URL (remove https://baka.ms/galleries/)
            path = url.replace("https://baka.ms/galleries/", "")

            # Create directory named after full path (removing .html extension)
            dir_path = f"galleries/{path}"
            dir_folder = dir_path.replace(".html", "")

            os.makedirs(dir_folder, exist_ok=True)
            print(f"Created directory: {dir_folder}")

            # Extract direct links for all HTML files
            if url.endswith(".html"):
                image_count = extract_direct_links(url, dir_folder)
                total_images += image_count

    print("\nFolder structure creation complete!")
    print(f"Processed {processed_count} directories")
    print(f"Extracted {total_images} total direct image links")
    print("Direct links saved to links.txt files in each folder")


def main():
    print("Fetching all HTML files recursively from all galleries...")

    results = fetch_all_html_recursive(BASE_URL)

    # Remove duplicates and sort
    results = sorted(set(results))

    # Write full URLs to file
    with open("files.txt", "w", encoding="utf-8") as f:
        for rel_path in results:
            full_url = f"https://baka.ms/galleries/{rel_path}"
            f.write(f"{full_url}\n")

    print(f"\nSaved {len(results)} URLs to files.txt")

    # Create folder structure
    create_folder_structure()


if __name__ == "__main__":
    main()
