import os
import re
import json
from bs4 import BeautifulSoup

def upgrade_seo_ai():
    base_url = "https://www.jjgpaperbag.com"
    root_dir = os.getcwd()
    
    # Common Keywords
    en_keywords = "Taiwan Paper Bag, Manufacturer, square bag, SOS bag, greaseproof bags, flat bag, satchel bags, gusset bags, handle shopping bags, eco-friendly packaging, PFAS-free, Juang Jia Guoo, wholesale paper bags, fast food packaging, bakery bags, kraft paper bags"
    zh_keywords = "台灣紙袋, 製造商, 工廠, 方底袋, SOS袋, 防油紙袋, 平口袋, 側邊袋, 折角袋, 手提購物袋, 環保包裝, 無PFAS, 壯佳果, 紙袋批發, 食品包裝袋, 烘焙紙袋, 牛皮紙袋"

    # Common Organization Schema
    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Juang Jia Guoo Co., Ltd. (JJG Pack)",
        "alternateName": "壯佳果股份有限公司",
        "url": base_url,
        "logo": f"{base_url}/images/index-logo.png",
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+886-4-26223215",
            "contactType": "sales",
            "email": "export@jjgpaperbag.com",
            "areaServed": "Global",
            "availableLanguage": ["English", "Chinese"]
        },
        "sameAs": [
            "https://www.youtube.com/watch?v=1BklHKj_q0c"
        ]
    }

    html_files = []
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in root or 'dist' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files. Starting SEO & AI Index upgrade...")

    for file_path in html_files:
        rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
        is_zh = 'zh-tw/' in rel_path or rel_path.startswith('zh-tw/')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            if not soup.head:
                continue

            # Language-specific settings
            lang = "zh-TW" if is_zh else "en"
            soup.html['lang'] = lang
            
            # 1. Meta Keywords
            keywords = zh_keywords if is_zh else en_keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                meta_keywords['content'] = keywords
            else:
                new_meta = soup.new_tag('meta', attrs={'name': 'keywords', 'content': keywords})
                soup.head.append(new_meta)

            # 2. Open Graph & Twitter
            page_title = soup.title.string if soup.title else "JJG Paper Bag"
            page_desc = soup.find('meta', attrs={'name': 'description'})
            page_desc = page_desc['content'] if page_desc else ""
            
            og_tags = {
                'og:title': page_title,
                'og:description': page_desc,
                'og:type': 'website',
                'og:url': f"{base_url}/{rel_path}",
                'og:site_name': "JJG Paper Bag | Juang Jia Guoo",
                'og:image': f"{base_url}/images/video-bg.jpg",
                'og:locale': 'zh_TW' if is_zh else 'en_US'
            }
            
            for prop, content in og_tags.items():
                existing = soup.find('meta', attrs={'property': prop})
                if existing:
                    existing['content'] = content
                else:
                    new_tag = soup.new_tag('meta', attrs={'property': prop, 'content': content})
                    soup.head.append(new_tag)

            # Twitter Tags
            twitter_tags = {
                'twitter:card': 'summary_large_image',
                'twitter:title': page_title,
                'twitter:description': page_desc,
                'twitter:image': f"{base_url}/images/video-bg.jpg"
            }
            
            for name, content in twitter_tags.items():
                existing = soup.find('meta', attrs={'name': name})
                if existing:
                    existing['content'] = content
                else:
                    new_tag = soup.new_tag('meta', attrs={'name': name, 'content': content})
                    soup.head.append(new_tag)

            # 3. Canonical Tag
            canonical = soup.find('link', rel='canonical')
            if canonical:
                canonical['href'] = f"{base_url}/{rel_path}"
            else:
                new_link = soup.new_tag('link', rel='canonical', href=f"{base_url}/{rel_path}")
                soup.head.append(new_link)

            # 4. JSON-LD Structured Data
            for old_script in soup.find_all('script', type='application/ld+json'):
                old_script.decompose()

            script_org = soup.new_tag('script', type='application/ld+json')
            script_org.string = json.dumps(org_schema, indent=2, ensure_ascii=False)
            soup.head.append(script_org)

            path_parts = rel_path.split('/')
            if len(path_parts) > 1 and rel_path != 'index.html' and rel_path != 'zh-tw/index.html':
                breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/index.html"}]
                for i, part in enumerate(path_parts):
                    if part == 'index.html': continue
                    item_url = f"{base_url}/{'/'.join(path_parts[:i+1])}"
                    breadcrumb_items.append({
                        "@type": "ListItem",
                        "position": len(breadcrumb_items) + 1,
                        "name": part.replace('.html', '').replace('-', ' ').title(),
                        "item": item_url
                    })
                
                breadcrumb_schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": breadcrumb_items}
                script_bread = soup.new_tag('script', type='application/ld+json')
                script_bread.string = json.dumps(breadcrumb_schema, indent=2, ensure_ascii=False)
                soup.head.append(script_bread)

            if 'products/' in rel_path and rel_path.count('/') >= 2:
                h1 = soup.find('h1')
                prod_name = h1.text.strip() if h1 else page_title
                prod_schema = {
                    "@context": "https://schema.org",
                    "@type": "Product",
                    "name": prod_name,
                    "description": page_desc,
                    "brand": {"@type": "Brand", "name": "JJG Pack"},
                    "manufacturer": org_schema,
                    "image": f"{base_url}/images/index-logo.png"
                }
                main_img = soup.find('img', alt=True)
                if main_img:
                    src = main_img['src']
                    if not src.startswith('http'):
                        src = f"{base_url}{src}" if src.startswith('/') else f"{base_url}/{src}"
                    prod_schema["image"] = src

                script_prod = soup.new_tag('script', type='application/ld+json')
                script_prod.string = json.dumps(prod_schema, indent=2, ensure_ascii=False)
                soup.head.append(script_prod)

            # 5. Accessibility (Alt Tags)
            for img in soup.find_all('img'):
                if not img.get('alt'):
                    img['alt'] = "JJG Paper Bag - Professional Packaging"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
        except Exception as e:
            print(f"Error processing {rel_path}: {e}")

    # 6. Generate AI Index Index (llms.txt)
    llms_txt = f"""# JJG Pack - Juang Jia Guoo | Professional Paper Bag Manufacturer

Juang Jia Guoo Co., Ltd. (JJG Pack) is a premier paper bag manufacturer based in Taiwan with over 70 years of experience. We specialize in sustainable, PFAS-free packaging solutions for food, retail, and industrial applications.

## Key Products
- **Greaseproof Bags**: Ideal for bakery, fast food, and deli items.
- **Kraft Paper Bags**: Square bottom, flat bottom, and shopping bags.
- **Handle Shopping Bags**: Flat handle and twisted handle variations.
- **Specialty Packaging**: Laminated bags, paper straws, and custom OEM/ODM solutions.

## Core Capabilities
- **PFAS-Free Production**: Certified eco-friendly and food-safe.
- **Global Export**: Serving over 100 countries worldwide.
- **Customization**: Precision printing and custom sizing for global brands.
- **Certifications**: ISO 22000, HACCP, FSC, and FSSC 22000.

## Useful Links
- [All Products]({base_url}/products.html)
- [About Us]({base_url}/about.html)
- [E-Catalog]({base_url}/catalog.html)
- [Contact for Quotation]({base_url}/contact.html)

## Bilingual Support
- [Traditional Chinese Version]({base_url}/zh-tw/index.html)
"""
    with open(os.path.join(root_dir, 'llms.txt'), 'w', encoding='utf-8') as f:
        f.write(llms_txt)
    print("llms.txt (AI Sitemap) generated.")

    # 7. Generate ai.txt
    ai_txt = """# AI Data Index - ai.txt
# Permissions for AI Agents and LLMs

User-agent: *
Permissions: 
  Search: allow
  Index: allow
  Training: allow
  Summary: allow

# Discovery
llms-txt: https://www.jjgpaperbag.com/llms.txt
sitemap: https://www.jjgpaperbag.com/sitemap.xml
"""
    with open(os.path.join(root_dir, 'ai.txt'), 'w', encoding='utf-8') as f:
        f.write(ai_txt)
    print("ai.txt generated.")

    # 8. Update Sitemap.xml
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for file_path in html_files:
        rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
        url_path = rel_path.replace('index.html', '') if rel_path.endswith('index.html') else rel_path
        sitemap_content += f'  <url>\n    <loc>{base_url}/{url_path}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if "index.html" in rel_path else "0.8"}</priority>\n  </url>\n'
    sitemap_content += '</urlset>'
    with open(os.path.join(root_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("Sitemap.xml updated.")

if __name__ == "__main__":
    upgrade_seo_ai()
