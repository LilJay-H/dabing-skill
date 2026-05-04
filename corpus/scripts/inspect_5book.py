# -*- coding: utf-8 -*-
"""检查5合1作品集的文本结构，找到正确的书籍边界"""
import zipfile, os, re

EPUB_DIR = r"D:\1电子资源\书籍\大冰"
five_book = os.path.join(EPUB_DIR, "大冰作品集（5册） (大冰) (Z-Library).epub")
LOG = r"C:\Users\kk\da-bing-corpus\inspect_log.txt"

lines = []

def log(msg):
    lines.append(msg)

with zipfile.ZipFile(five_book, 'r') as z:
    names = z.namelist()
    content_files = sorted([n for n in names if n.endswith(('.xhtml', '.html', '.htm'))])
    log(f"Total content files: {len(content_files)}")

    # 逐文件提取并记录内容开头
    all_text_parts = []
    for i, n in enumerate(content_files):
        raw = z.read(n)
        text = None
        for enc in ['utf-8', 'gb18030', 'gbk']:
            try:
                text = raw.decode(enc)
                break
            except:
                continue
        if text is None:
            continue

        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL|re.IGNORECASE)
        body = re.search(r'<body[^>]*>(.*?)</body>', text, re.DOTALL|re.IGNORECASE)
        if body:
            text = body.group(1)
        text = re.sub(r'<br\s*/?>|</(p|div|h[1-6]|tr|li|blockquote)>', '\n', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&\w+;', '', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()

        if text:
            all_text_parts.append((n, text))

    full = '\n'.join(t for _, t in all_text_parts)

    # 找到所有可能的大标题（章节标题）
    # 通常是短行（<20字），且是书名或章节名
    log("\n=== 文本前3000字（含版权页和目录） ===")
    log(full[:3000])

    log("\n\n=== 搜索书名边界标记 ===")
    # 搜索5本书的书名
    book_titles = ['你坏', '我不', '好吗好的', '阿弥陀佛么么哒', '乖，摸摸头', '乖，摸摸头']
    for title in book_titles:
        positions = [m.start() for m in re.finditer(re.escape(title), full)]
        log(f"\n'{title}' 出现在 {len(positions)} 个位置:")
        for pos in positions[:10]:
            context = full[max(0,pos-100):pos+100].replace('\n', ' ')
            log(f"  pos={pos}: ...{context}...")

    # 也搜索"你坏"/"我不"等作为大标题出现的位置（独立成行）
    log("\n\n=== 搜索独立成行的大标题 ===")
    for title in ['你坏', '我不', '好吗好的', '阿弥陀佛么么哒', '乖，摸摸头']:
        pattern = r'(?:^|\n)\s*' + re.escape(title) + r'\s*(?:\n|$)'
        positions = [m.start() for m in re.finditer(pattern, full)]
        log(f"\n'{title}' 独立成行出现在 {len(positions)} 个位置:")
        for pos in positions[:5]:
            context = full[max(0,pos-50):pos+50].replace('\n', '\\n')
            log(f"  pos={pos}: [{context}]")

    # 查找文件名模式 - 5本书可能以不同的文件夹/路径组织
    log("\n\n=== 文件路径结构 ===")
    dirs = set()
    for n in content_files:
        parts = n.split('/')
        if len(parts) > 1:
            dirs.add(parts[0])
    log(f"顶层目录: {sorted(dirs)}")

    # 检查前5个和后5个文件的内容
    log("\n\n=== 前5个内容文件 ===")
    for n, text in all_text_parts[:5]:
        log(f"\n--- {n} ({len(text)} chars) ---")
        log(text[:200])

    log("\n\n=== 最后5个内容文件 ===")
    for n, text in all_text_parts[-5:]:
        log(f"\n--- {n} ({len(text)} chars) ---")
        log(text[:200])

with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Done. Check inspect_log.txt")
