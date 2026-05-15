#!/usr/bin/env python3
"""
JJGPack Advanced SEO Infrastructure Upgrade Script
Addresses all issues from the SEO technical analysis report.
"""
import os
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.jjgpaperbag.com"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. PAGE-SPECIFIC METADATA REGISTRY
# ============================================================
# Manually curated, high-quality metadata for key pages
PAGE_META = {
    # English pages
    "index.html": {
        "title": "Juang Jia Guoo | Professional Paper Bag Manufacturer in Taiwan",
        "description": "70+ years of trusted paper bag manufacturing. PFAS-free, ISO 22000 & FSC certified. Kraft bags, greaseproof bags, custom OEM/ODM packaging for global brands.",
        "h1_check": True,
    },
    "about.html": {
        "title": "About Juang Jia Guoo | 70+ Years Paper Bag Manufacturing Excellence",
        "description": "Discover Juang Jia Guoo's 70-year legacy in paper bag manufacturing. ISO 22000, HACCP, FSC & FSSC 22000 certified factory in Taiwan serving 100+ countries.",
    },
    "products.html": {
        "title": "Paper Bag Products | Kraft, Greaseproof & Custom Bags - JJG Pack",
        "description": "Browse our complete range of eco-friendly paper bags: greaseproof, brown kraft, white kraft, PE lamination, flat handle, fruit protection bags & paper straws.",
    },
    "news.html": {
        "title": "News & Industry Updates | JJG Paper Bag Manufacturer",
        "description": "Latest news on PFAS-free innovation, sustainable packaging trends, water-based flexographic printing, and JJG Paper Bag exhibition appearances worldwide.",
    },
    "catalog.html": {
        "title": "E-Catalog & Product Specifications | JJG Paper Bag",
        "description": "Download JJG Pack product catalogs: Imperial & Metric unit specifications, USA standard catalogue, and detailed paper bag product guides for B2B buyers.",
    },
    "contact.html": {
        "title": "Contact JJG Paper Bag | Get Custom Quotes & OEM Partnerships",
        "description": "Contact Juang Jia Guoo for wholesale paper bag quotes, OEM/ODM partnerships, and custom packaging inquiries. Factory in Taichung, Taiwan. Global shipping.",
    },
    # ZH-TW pages
    "zh-tw/index.html": {
        "title": "壯佳果包裝 | 台灣最大專業紙袋製造商 - 70年經驗",
        "description": "壯佳果股份有限公司，台灣專業紙袋製造商，超過70年生產經驗。提供防油紙袋、牛皮紙袋、手提紙袋、客製化印刷等環保食品包裝解決方案。ISO 22000認證。",
    },
    "zh-tw/about.html": {
        "title": "關於壯佳果 | 70年專業紙袋製造工廠 - JJG Paper Bag",
        "description": "認識壯佳果企業70年製袋歷史，通過ISO 22000、HACCP、FSC、FSSC 22000認證。月產能1.65億件，服務全球100+國家。",
    },
    "zh-tw/products.html": {
        "title": "產品介紹 | 防油紙袋、牛皮紙袋、手提袋 - 壯佳果包裝",
        "description": "瀏覽壯佳果全系列環保紙袋產品：防油紙袋、棕色牛皮紙袋、白牛皮紙袋、PE淋膜紙袋、平把手提袋、水果保護袋及紙吸管。",
    },
    "zh-tw/news.html": {
        "title": "最新消息 | 壯佳果包裝 - JJG Paper Bag",
        "description": "壯佳果最新企業動態、參展資訊、紙袋產業知識百科。了解無PFAS創新、水性柔版印刷技術及永續包裝趨勢。",
    },
    "zh-tw/catalog.html": {
        "title": "型錄EDM | 產品規格下載 - 壯佳果包裝",
        "description": "下載壯佳果產品型錄：英制與公制規格目錄、美規標準型錄及各式紙袋產品EDM電子行銷文宣。",
    },
    "zh-tw/contact.html": {
        "title": "聯絡我們 | 索取報價、OEM/ODM合作 - 壯佳果包裝",
        "description": "聯繫壯佳果企業洽詢紙袋批發報價、OEM/ODM客製合作。工廠位於台中大甲，全球出貨。電話：+886-4-26223215。",
    },
}

# Category page metadata
CATEGORY_META = {
    "products/greaseproof.html": {
        "title": "Greaseproof Paper Bags | PFAS-Free Food Packaging - JJG Pack",
        "description": "Wholesale greaseproof paper bags for bakery, fast food & deli. PFAS-free, PE laminated, food-grade certified. Custom printing available. Taiwan manufacturer.",
        "cat_name": "Greaseproof Paper Bag",
    },
    "products/kraft.html": {
        "title": "Brown Kraft Paper Bags | SOS & Square Bottom Bags - JJG Pack",
        "description": "Premium brown kraft paper bags: SOS bags, square bottom, grocery & to-go bags. 100% virgin kraft paper, eco-friendly. Wholesale from Taiwan manufacturer.",
        "cat_name": "Brown Kraft Bag",
    },
    "products/white-kraft.html": {
        "title": "White Kraft Paper Bags | Retail & Medical Packaging - JJG Pack",
        "description": "White kraft paper bags for retail, pharmacy & bakery. Clean appearance, food-grade certified. Flat handle & shopping bag options. Custom sizes available.",
        "cat_name": "White Kraft Bag",
    },
    "products/pe-lamination.html": {
        "title": "PE Lamination Paper Bags | Waterproof Food Wraps - JJG Pack",
        "description": "PE laminated paper bags: burger pockets, deli wraps & moisture-proof packaging. Greaseproof, waterproof, food-grade. OEM/ODM from Taiwan manufacturer.",
        "cat_name": "PE Lamination Paper Bag",
    },
    "products/flat-handle.html": {
        "title": "Flat Handle Paper Bags | Shopping & Carry Bags - JJG Pack",
        "description": "Flat handle paper shopping bags in kraft & white. High stability, food-grade water-based ink printing. Eco-friendly retail packaging from Taiwan.",
        "cat_name": "Flat Handle Paper Bag",
    },
    "products/aluminum-foil.html": {
        "title": "Aluminum Foil Paper Bags | Heat Retention Packaging - JJG Pack",
        "description": "Aluminum foil lined paper bags for hot food takeaway. Excellent heat retention for roasted chicken, BBQ & fast food. Wholesale from certified Taiwan factory.",
        "cat_name": "Aluminum Foil Paper Bag",
    },
    "products/fruit-protection.html": {
        "title": "Fruit Protection Bags | Agricultural Paper Bags - JJG Pack",
        "description": "Paper fruit protection bags for mango, dragon fruit, grape & guava. Double-layer pest and weather protection. Agricultural packaging from Taiwan manufacturer.",
        "cat_name": "Fruit Protection Bag",
    },
    "products/paper-straw.html": {
        "title": "Biodegradable Paper Straws | Eco-Friendly Alternative - JJG Pack",
        "description": "100% biodegradable paper straws and bamboo straws. Plastic-free, food-safe, Taiwan made. Wholesale eco-friendly drinking solutions for restaurants & cafes.",
        "cat_name": "Paper Straw",
    },
    "products/others.html": {
        "title": "Specialty & Custom Paper Bags | Unique Packaging - JJG Pack",
        "description": "Custom & specialty paper bags: paper placemats, unique designs, bespoke packaging solutions. OEM/ODM services available from JJG Pack Taiwan.",
        "cat_name": "Specialty Bags",
    },
}

# Hreflang mapping: EN path -> ZH-TW path
HREFLANG_MAP = {
    "index.html": "zh-tw/index.html",
    "about.html": "zh-tw/about.html",
    "products.html": "zh-tw/products.html",
    "news.html": "zh-tw/news.html",
    "catalog.html": "zh-tw/catalog.html",
    "contact.html": "zh-tw/contact.html",
}

# Certification alt text fixes
CERT_ALT_FIXES = {
    "footer-iso_v2.png": "ISO 22000, HACCP, FSC, FSSC 22000 International Certifications for Paper Bag Manufacturing",
    "footer-iso": "ISO 22000, HACCP, FSC, FSSC 22000 Certified Paper Bag Factory",
    "2022-FSSC": "FSSC 22000 Food Safety System Certification - JJG Paper Bag",
    "2022-HACCP": "HACCP Hazard Analysis Certification - JJG Paper Bag Manufacturing",
    "2022-ISO": "ISO 22000 Food Safety Management Certification - JJG Pack",
    "FSC": "FSC Forest Stewardship Council Certified Eco-friendly Packaging",
}


def get_rel_path(file_path):
    """Get relative path from root, normalized with forward slashes."""
    return os.path.relpath(file_path, ROOT_DIR).replace("\\", "/")


def get_canonical_url(rel_path):
    """Build canonical URL from relative path."""
    clean = rel_path.replace("index.html", "").rstrip("/")
    if not clean:
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{clean}"


def is_zh(rel_path):
    return "zh-tw/" in rel_path or rel_path.startswith("zh-tw/")


def find_all_html():
    """Find all HTML files, excluding node_modules, dist, .git."""
    html_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".git", ".github", "EDM-Web", "public")]
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))
    return html_files


def generate_product_meta(rel_path, soup):
    """Auto-generate meta for product detail pages from H1/content."""
    h1 = soup.find("h1")
    product_name = h1.get_text(strip=True) if h1 else ""
    if not product_name:
        # Try h3 as fallback
        h3 = soup.find("h3")
        product_name = h3.get_text(strip=True) if h3 else ""
    if not product_name:
        # Extract from filename
        fname = os.path.basename(rel_path).replace(".html", "").replace("-", " ").title()
        product_name = fname

    desc = f"{product_name} - Professional food-grade paper bag by JJG Pack. PFAS-free, eco-friendly, custom sizes available. ISO 22000 certified Taiwan manufacturer."
    if len(desc) > 155:
        desc = desc[:152] + "..."
    title = f"{product_name} | JJG Paper Bag - Juang Jia Guoo"
    return title, desc, product_name


def fix_certification_alts(soup):
    """Fix certification image alt texts that show raw file paths."""
    for img in soup.find_all("img"):
        alt = img.get("alt", "")
        src = img.get("src", "")
        # Fix file-path style alts
        for pattern, replacement in CERT_ALT_FIXES.items():
            if pattern in src or pattern in alt:
                img["alt"] = replacement
                break


def set_meta(soup, name_or_prop, value, is_property=False):
    """Set or create a meta tag."""
    if is_property:
        tag = soup.find("meta", attrs={"property": name_or_prop})
        if tag:
            tag["content"] = value
        else:
            new = soup.new_tag("meta", attrs={"property": name_or_prop, "content": value})
            soup.head.append(new)
    else:
        tag = soup.find("meta", attrs={"name": name_or_prop})
        if tag:
            tag["content"] = value
        else:
            new = soup.new_tag("meta", attrs={"name": name_or_prop, "content": value})
            soup.head.append(new)


def remove_existing_hreflang(soup):
    """Remove any existing hreflang link tags."""
    for link in soup.find_all("link", rel="alternate"):
        if link.get("hreflang"):
            link.decompose()


def add_hreflang(soup, en_url, zh_url):
    """Add hreflang link tags for EN, ZH-TW, and x-default."""
    remove_existing_hreflang(soup)
    for hreflang, href in [("en", en_url), ("zh-TW", zh_url), ("x-default", en_url)]:
        tag = soup.new_tag("link", rel="alternate", hreflang=hreflang, href=href)
        soup.head.append(tag)


def add_robots_meta(soup):
    """Add robots meta tag if missing."""
    existing = soup.find("meta", attrs={"name": "robots"})
    if not existing:
        tag = soup.new_tag("meta", attrs={"name": "robots", "content": "index, follow"})
        soup.head.append(tag)


def process_html(file_path):
    """Process a single HTML file with all SEO upgrades."""
    rel_path = get_rel_path(file_path)
    zh = is_zh(rel_path)

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    if not soup.head:
        return

    # --- Language attribute ---
    if soup.html:
        soup.html["lang"] = "zh-TW" if zh else "en"

    # --- Determine page metadata ---
    page_title = ""
    page_desc = ""
    product_name = ""

    if rel_path in PAGE_META:
        meta = PAGE_META[rel_path]
        page_title = meta["title"]
        page_desc = meta["description"]
    elif rel_path in CATEGORY_META:
        meta = CATEGORY_META[rel_path]
        page_title = meta["title"]
        page_desc = meta["description"]
        # Fix empty H1 on category pages
        h1 = soup.find("h1")
        if h1 and not h1.get_text(strip=True):
            h1.string = meta["cat_name"]
    elif "products/" in rel_path:
        page_title, page_desc, product_name = generate_product_meta(rel_path, soup)
    else:
        # Fallback: use existing title/desc
        page_title = soup.title.string.strip() if soup.title and soup.title.string else "JJG Paper Bag"
        desc_tag = soup.find("meta", attrs={"name": "description"})
        page_desc = desc_tag["content"] if desc_tag and desc_tag.get("content") else ""

    # --- Set Title ---
    if soup.title:
        soup.title.string = page_title
    else:
        title_tag = soup.new_tag("title")
        title_tag.string = page_title
        soup.head.insert(0, title_tag)

    # --- Set Meta Description ---
    if page_desc:
        set_meta(soup, "description", page_desc)

    # --- Robots Meta ---
    add_robots_meta(soup)

    # --- Canonical Tag ---
    canonical_url = f"{BASE_URL}/{rel_path}"
    canonical = soup.find("link", rel="canonical")
    if canonical:
        canonical["href"] = canonical_url
    else:
        tag = soup.new_tag("link", rel="canonical", href=canonical_url)
        soup.head.append(tag)

    # --- Hreflang Tags ---
    en_path = rel_path.replace("zh-tw/", "") if zh else rel_path
    zh_path = f"zh-tw/{en_path}" if not zh else rel_path

    # Only add hreflang if counterpart likely exists
    if en_path in HREFLANG_MAP or rel_path in HREFLANG_MAP.values():
        en_url = f"{BASE_URL}/{en_path}"
        zh_url = f"{BASE_URL}/{zh_path}"
        add_hreflang(soup, en_url, zh_url)
    else:
        # For product/category pages, add hreflang if zh-tw counterpart path exists
        zh_counterpart = os.path.join(ROOT_DIR, zh_path)
        en_counterpart = os.path.join(ROOT_DIR, en_path)
        if os.path.exists(zh_counterpart) and os.path.exists(en_counterpart):
            en_url = f"{BASE_URL}/{en_path}"
            zh_url = f"{BASE_URL}/{zh_path}"
            add_hreflang(soup, en_url, zh_url)

    # --- Open Graph Tags ---
    og_image = f"{BASE_URL}/images/video-bg.jpg"
    # Try to find a better OG image from the page
    first_product_img = soup.find("img", attrs={"alt": True})
    if first_product_img and first_product_img.get("src"):
        src = first_product_img["src"]
        if src.startswith("http"):
            og_image = src
        elif src.startswith("/"):
            og_image = f"{BASE_URL}{src}"

    og_tags = {
        "og:title": page_title,
        "og:description": page_desc,
        "og:type": "website",
        "og:url": canonical_url,
        "og:site_name": "JJG Paper Bag | Juang Jia Guoo Co., Ltd.",
        "og:image": og_image,
        "og:locale": "zh_TW" if zh else "en_US",
    }
    if zh:
        og_tags["og:locale:alternate"] = "en_US"
    else:
        og_tags["og:locale:alternate"] = "zh_TW"

    for prop, content in og_tags.items():
        set_meta(soup, prop, content, is_property=True)

    # --- Twitter Card Tags ---
    twitter_tags = {
        "twitter:card": "summary_large_image",
        "twitter:title": page_title,
        "twitter:description": page_desc,
        "twitter:image": og_image,
    }
    for name, content in twitter_tags.items():
        set_meta(soup, name, content)

    # --- Fix Certification Image Alts ---
    fix_certification_alts(soup)

    # --- Fix generic/empty Alt tags ---
    for img in soup.find_all("img"):
        alt = img.get("alt", "").strip()
        src = img.get("src", "")
        # Fix logos
        if "index-logo" in src and alt in ("JJG", ""):
            img["alt"] = "JJG Paper Bag - Juang Jia Guoo Official Logo"
        # Fix empty alts on decorative SVGs - leave as empty alt
        elif not alt and not src:
            img["alt"] = ""
        # Fix generic placeholder alts
        elif alt == "JJG Paper Bag - Professional Packaging":
            # Try to derive a better alt from context
            parent_h3 = img.find_parent("div")
            if parent_h3:
                h3 = parent_h3.find("h3")
                if h3 and h3.get_text(strip=True):
                    img["alt"] = h3.get_text(strip=True) + " - JJG Paper Bag"

    # --- Write back ---
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    return rel_path


def generate_robots_txt():
    """Generate robots.txt file."""
    content = f"""# robots.txt for JJG Paper Bag - Juang Jia Guoo Co., Ltd.
# https://www.jjgpaperbag.com

User-agent: *
Allow: /
Disallow: /node_modules/
Disallow: /dist/
Disallow: /.git/

# Sitemaps
Sitemap: {BASE_URL}/sitemap.xml

# Crawl-delay (optional, for polite crawling)
Crawl-delay: 1
"""
    path = os.path.join(ROOT_DIR, "robots.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [CREATED] robots.txt")


def generate_sitemap(html_files):
    """Generate comprehensive sitemap.xml."""
    now = datetime.now().strftime("%Y-%m-%d")

    # Priority mapping
    def get_priority(rel):
        if rel in ("index.html", "zh-tw/index.html"):
            return "1.0"
        if rel in ("products.html", "about.html", "contact.html", "zh-tw/products.html"):
            return "0.9"
        if rel.startswith("products/") and rel.count("/") == 1:
            return "0.8"  # Category pages
        if rel.startswith("products/") and rel.count("/") >= 2:
            return "0.7"  # Product detail pages
        return "0.6"

    urls = []
    for fp in html_files:
        rel = get_rel_path(fp)
        url = f"{BASE_URL}/{rel}"
        priority = get_priority(rel)
        freq = "weekly" if priority in ("1.0", "0.9") else "monthly"
        urls.append((url, freq, priority, now))

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    sitemap += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

    for url, freq, priority, lastmod in sorted(urls):
        sitemap += f"  <url>\n"
        sitemap += f"    <loc>{url}</loc>\n"
        sitemap += f"    <lastmod>{lastmod}</lastmod>\n"
        sitemap += f"    <changefreq>{freq}</changefreq>\n"
        sitemap += f"    <priority>{priority}</priority>\n"
        sitemap += f"  </url>\n"

    sitemap += "</urlset>"

    path = os.path.join(ROOT_DIR, "sitemap.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  [CREATED] sitemap.xml ({len(urls)} URLs)")


def generate_llms_txt():
    """Generate updated llms.txt for AI indexing."""
    content = f"""# JJG Pack - Juang Jia Guoo Co., Ltd. | Professional Paper Bag Manufacturer

> Taiwan's leading paper bag manufacturer with 70+ years of experience. ISO 22000, HACCP, FSC & FSSC 22000 certified. PFAS-free, eco-friendly packaging solutions.

## Company Overview
Juang Jia Guoo Co., Ltd. (JJG Pack / 壯佳果股份有限公司) is a premier paper bag manufacturer based in Taichung, Taiwan. Established in the 1960s, we specialize in sustainable, PFAS-free packaging solutions for food service, retail, agriculture and industrial applications. Monthly production capacity: 165 million bags.

## Product Categories
- **Greaseproof Paper Bags**: Bakery bags, sandwich bags, burger wrappers, PFAS-free options
- **Brown Kraft Paper Bags**: SOS bags, square bottom, grocery, to-go bags
- **White Kraft Paper Bags**: Retail, pharmacy, bakery window bags
- **PE Lamination Bags**: Waterproof, moisture-proof burger pockets & deli wraps
- **Flat Handle Shopping Bags**: Custom printed, eco-friendly carry bags
- **Aluminum Foil Bags**: Heat-retaining bags for hot food takeaway
- **Fruit Protection Bags**: Agricultural bags for mango, dragon fruit, grape
- **Paper Straws**: 100% biodegradable, plastic-free drinking straws

## Certifications
- ISO 22000 Food Safety Management
- HACCP Hazard Analysis
- FSC Forest Stewardship Council
- FSSC 22000 Food Safety System

## Key Links
- [Homepage]({BASE_URL}/)
- [All Products]({BASE_URL}/products.html)
- [About Us]({BASE_URL}/about.html)
- [E-Catalogs]({BASE_URL}/catalog.html)
- [Contact / Get Quote]({BASE_URL}/contact.html)
- [News & Updates]({BASE_URL}/news.html)

## Languages
- [English]({BASE_URL}/)
- [繁體中文]({BASE_URL}/zh-tw/index.html)

## Contact
- Address: No.6, You 9th Rd. Dajia Dist., Taichung City 43769 Taiwan
- Phone: +886-4-26223215
- Email: export@jjgpaperbag.com
"""
    path = os.path.join(ROOT_DIR, "llms.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [CREATED] llms.txt")


def main():
    print("=" * 60)
    print("JJGPack Advanced SEO Infrastructure Upgrade")
    print("=" * 60)

    # 1. Find all HTML files
    html_files = find_all_html()
    print(f"\n[1/5] Found {len(html_files)} HTML files to process")

    # 2. Process each file
    print(f"\n[2/5] Processing HTML files...")
    processed = 0
    errors = 0
    for fp in html_files:
        try:
            rel = process_html(fp)
            if rel:
                processed += 1
                print(f"  [OK] {rel}")
        except Exception as e:
            errors += 1
            print(f"  [ERROR] {get_rel_path(fp)}: {e}")

    print(f"\n  Processed: {processed}, Errors: {errors}")

    # 3. Generate robots.txt
    print(f"\n[3/5] Generating robots.txt...")
    generate_robots_txt()

    # 4. Generate sitemap.xml
    print(f"\n[4/5] Generating sitemap.xml...")
    generate_sitemap(html_files)

    # 5. Generate llms.txt
    print(f"\n[5/5] Generating llms.txt...")
    generate_llms_txt()

    print("\n" + "=" * 60)
    print("SEO Upgrade Complete!")
    print("=" * 60)
    print("\nSummary of changes applied to each HTML file:")
    print("  [OK] Unique Title Tags (curated for key pages, auto-generated for products)")
    print("  [OK] Unique Meta Descriptions (<155 chars, keyword-optimized)")
    print("  [OK] Canonical Tags (self-referencing absolute URLs)")
    print("  [OK] Hreflang Tags (en, zh-TW, x-default matrix)")
    print("  [OK] Robots Meta Tags (index, follow)")
    print("  [OK] Open Graph Tags (og:title, og:description, og:image, og:url, og:locale)")
    print("  [OK] Twitter Card Tags (summary_large_image)")
    print("  [OK] Image Alt Text fixes (certifications, logos, generic placeholders)")
    print("  [OK] Category page H1 tag fixes")
    print("\nGenerated files:")
    print("  [OK] robots.txt (crawler directives + sitemap reference)")
    print("  [OK] sitemap.xml (comprehensive URL map with priorities)")
    print("  [OK] llms.txt (AI/LLM indexing file)")


if __name__ == "__main__":
    main()
