# -*- coding: utf-8 -*-
"""
大冰语料库提取器 v2.0：基于精确定位拆分5合1作品集
"""
import zipfile, os, re, json

EPUB_DIR = r"D:\1电子资源\书籍\大冰"
OUT_DIR = r"C:\Users\kk\da-bing-corpus\books"
os.makedirs(OUT_DIR, exist_ok=True)

def extract_epub_full(epub_path):
    """从epub提取全部文本"""
    chunks = []
    with zipfile.ZipFile(epub_path, 'r') as z:
        names = sorted([n for n in z.namelist() if n.endswith(('.xhtml', '.html', '.htm'))])
        for n in names:
            raw = z.read(n)
            text = None
            for enc in ['utf-8', 'gb18030', 'gbk']:
                try:
                    text = raw.decode(enc); break
                except: continue
            if text is None: continue
            text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL|re.IGNORECASE)
            body = re.search(r'<body[^>]*>(.*?)</body>', text, re.DOTALL|re.IGNORECASE)
            if body: text = body.group(1)
            text = re.sub(r'<br\s*/?>|</(p|div|h[1-6]|tr|li|blockquote)>', '\n', text, flags=re.DOTALL|re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
            text = re.sub(r'&\w+;', '', text)
            text = re.sub(r'[ \t]+', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            if text.strip(): chunks.append(text.strip())
    return '\n\n'.join(chunks)


def split_5book(full_text, out_dir):
    """用版权信息标记精确拆分5合1作品集"""
    # 每本书的版权信息起始标记（去掉了目录中重复的书名）
    # 从分析日志中定位的精确位置：
    # 你坏: pos=63 (第一个"版权信息\n\n你坏")
    # 我不: pos=196848 ("版权信息\n\n\n\n我不")
    # 好吗好的: pos=368045 ("版权信息\n\n好吗好的")
    # 阿弥陀佛么么哒: pos=551392 ("版权信息\n\n阿弥陀佛么么哒")
    # 乖，摸摸头: pos=709295 ("版权信息\n\n乖，摸摸头")

    # 用正则精确定位每本书的版权信息起始
    boundaries = []
    patterns = [
        (r'版权信息\s*\n+\s*你坏', '你坏'),
        (r'版权信息\s*\n+\s*我不', '我不'),
        (r'版权信息\s*\n+\s*好吗好的', '好吗好的'),
        (r'版权信息\s*\n+\s*阿弥陀佛么么哒', '阿弥陀佛么么哒'),
        (r'版权信息\s*\n+\s*乖，摸摸头', '乖，摸摸头'),
    ]

    for pattern, name in patterns:
        # 找第二次出现（第一次在总目录）
        matches = list(re.finditer(pattern, full_text))
        if len(matches) >= 2:
            pos = matches[1].start()
            boundaries.append((pos, name))
        elif len(matches) == 1:
            pos = matches[0].start()
            boundaries.append((pos, name))

    boundaries.sort(key=lambda x: x[0])

    saved = []
    for i, (pos, name) in enumerate(boundaries):
        end = boundaries[i+1][0] if i+1 < len(boundaries) else len(full_text)
        text = full_text[pos:end].strip()

        # 清理：去掉开头的"版权信息\n\n书名\n"
        text = re.sub(r'^版权信息\s*\n+\s*' + re.escape(name) + r'\s*\n*', '', text, count=1)
        # 去掉版权页（到第一个故事标题之前的内容，但保留作者自述）
        # 直接保留全部内容让用户看到完整文本

        fname = name.replace('，', '').replace(' ', '') + '.txt'
        fpath = os.path.join(out_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
        saved.append((name, len(text), fpath))
        print(f"OK {name}: {len(text):,} 字")

    return saved


def extract_single(epub_path, book_name, out_dir):
    text = extract_epub_full(epub_path)
    fname = book_name.replace('，', '').replace(' ', '') + '.txt'
    fpath = os.path.join(out_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"OK {book_name}: {len(text):,} 字")
    return (book_name, len(text), fpath)


print("=" * 60)
print("大冰语料库提取器 v2.0")
print("=" * 60)

results = []

# 单本epub
single = [
    (r"他们最幸福 (大冰 著 [著, 大冰]) (Z-Library).epub", "他们最幸福"),
    (r"小孩（现象级畅销书作家大冰2019年全新作品。于无常处知有情， 于有情处知众生。 ） (大冰) (z-library.sk, 1lib.sk, z-lib.sk).epub", "小孩"),
    (r"保重 (大冰) (z-library.sk, 1lib.sk, z-lib.sk).epub", "保重"),
]
for epub_name, book_name in single:
    epub_path = os.path.join(EPUB_DIR, epub_name)
    if os.path.exists(epub_path):
        results.append(extract_single(epub_path, book_name, OUT_DIR))

# 5合1
five_book = os.path.join(EPUB_DIR, "大冰作品集（5册） (大冰) (Z-Library).epub")
if os.path.exists(five_book):
    print("\n拆分5合1作品集...")
    full = extract_epub_full(five_book)
    results.extend(split_5book(full, OUT_DIR))

# 汇总
print(f"\n{'='*60}")
total = sum(r[1] for r in results)
print(f"语料库提取完成！共 {len(results)} 本书, {total:,} 字\n")
for name, chars, _ in sorted(results, key=lambda x: -x[1]):
    pct = chars / total * 100
    bar = '#' * int(pct / 2)
    print(f"  {name:12s} {chars:>9,} 字 ({pct:5.1f}%) {bar}")

meta = {"books": [{"name": n, "chars": c, "file": os.path.basename(p)} for n, c, p in results], "total_chars": total}
with open(os.path.join(OUT_DIR, '..', 'metadata.json'), 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
