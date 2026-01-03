# baka.ms Gallery Scraper

Python script to recursively fetch all HTML files from baka.ms/galleries/ and extract direct media links.

## Features

- **Recursive Crawling**: Finds all HTML files at any depth
- **Direct Link Extraction**: Extracts working direct image links using token reversal pattern
- **Folder Structure Creation**: Creates directories mirroring website structure
- **Comprehensive Coverage**: Processes all 892+ URLs across multiple artists

## URL Pattern

- **Photos**: `data-idimg="abc123"` → `"321cba"` → `https://photos.baka.ms/photoservice/uwu/pull/321cba?abc123`
- **Videos**: Uses same pattern but requires additional investigation (currently skipped)

## File Structure

```text
galleries/
├── alicedelish/
│   ├── patreonfeedpt1/
│   │   ├── links.txt (293 photo links)
│   ├── patreonfeedpt2/
│   │   ├── links.txt (282 photo links)
│   ├── patreonfeedpt3/
│   │   ├── links.txt (299 photo links)
│   └── patreonfeedpt4/
│   │   └── links.txt (50 photo links)
├── belle_delphine/
│   ├── 2020/
│   │   ├── 01-June/
│   │   │   │   ├── links.txt (26 photos)
│   │   │   └── ...
│   ├── 2020/02-July/
│   │   │   │   ├── links.txt (51 photos)
│   │   │   └── ...
│   ├── NF/
│   │   └── tsukides/
│   │       └── fansly/
│   │       │   └── timeline/
│   │       │       └── 2023.7.5_533006707148730368_(Nude.Holo.Home)/
│   │       │       │   │   └── links.txt (1 video link - requires investigation)
│   │       │       └── ...
├── breadcos/
│   ├── patreon/
│   │   ├── links.txt (41 photo links)
│   │   └── onlyfans-rip.html
│   │   │   └── links.txt (1 photo link)
│   └── ...
```

## Current Status

- ✅ **Photo links verified working** (4.3MB test download successful)
- ✅ **Proper artist directory structure** (galleries/artist/album/subfolder/)
- ✅ **All 892 URLs processed** across 39 artists
- ⚠️ **12 artists with dynamic loading** cannot be scraped (156 empty files)
- ⚠️ **Video links need dynamic loading** (require JS execution)

## Current Limitations

- ✅ **Photos**: Working - token reversal pattern verified with curl test
- ⚠️ **Videos**: Requires dynamic content loading - currently skipped
- ✅ **Empty Pages**: Expected behavior - some pages genuinely have no immediately available static content

## Content Loading Systems Discovered

### Static Loading System (Working) ✅
**Example Artists**: alicedelish, belle_delphine, etc.

Artists using this system have `<img>` tags with `data-idimg` attributes directly embedded in the HTML:

```html
<img data-idimg="A2LUBJLxCMkyJxDD9bvWxfQN40QrecjjGk5uCaaInqhpU..." />
```

The script extracts these tokens, reverses them, and constructs direct URLs.

### Dynamic Loading System (Not Working) ❌
**Example Artists**: natsumipon, caticornplay, toxicosplays, neyrodesu, lightcos, etc. (12 artists total)

These artists use a JavaScript-based dynamic loading system:

```html
<div id="photos" data-fid="u9uKN2rfJVmeU2Nv5Wah1wJKvqJRcPpJ" data-reverse=""></div>
```

**Key Differences:**
- No `<img>` tags with `data-idimg` in initial HTML
- Content loaded via JavaScript using `data-fid` identifier
- Still appears to use token reversal (`data-reverse=""` attribute)
- Requires additional API calls or JavaScript execution to extract

### Impact Analysis
- **156 empty links.txt files** across 12 artists
- **Completely unscrapable artists**: NF, bunniberry, caterpillarcos, gardenpixie, gintku, holliefyy, hologana, kawaiitsu, kittiolic, lightcos, moxxi.morgan, natsumipon
- **Partially affected artists**: toxicosplays (45 empty), neyrodesu (25 empty), caticornplay (45 empty)

### Potential Solutions
To support dynamic loading, the script would need to:
1. Extract `data-fid` from the photos div
2. Make additional API calls to fetch image data
3. Or use a headless browser to execute JavaScript
4. Or reverse-engineer the API endpoint that serves the dynamic content

## Usage

```bash
python3 main.py
```

## Notes

- Script processes 892 URLs across 39 artists
- Creates proper directory structure: `galleries/artist/album/subfolder/`
- Extracts **~100,000 direct photo links** from artists using static loading
- **156 empty links.txt files** from artists using dynamic loading system
- Script handles both content types gracefully, creating empty files where no static content is available

## License

This project is licensed under the MIT License. See the LICENSE file for details.
