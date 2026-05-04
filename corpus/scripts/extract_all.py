# -*- coding: utf-8 -*-
"""
大冰语料库提取器：从epub提取全文，按书名分文件存储
"""
import zipfile, os, re, json

EPUB_DIR = r"D:\1电子资源\书籍\大冰"
OUT_DIR = r"C:\Users\kk\da-bing-corpus\books"
LOG_FILE = r"C:\Users\kk\da-bing-corpus\extract_log.txt"
os.makedirs(OUT_DIR, exist_ok=True)

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

def extract_epub(epub_path):
    chunks = []
    with zipfile.ZipFile(epub_path, 'r') as z:
        names = z.namelist()
        content_files = sorted([n for n in names if n.endswith(('.xhtml', '.html', '.htm'))])

        for n in content_files:
            raw = z.read(n)
            text = None
            for enc in ['utf-8', 'gb18030', 'gbk', 'gb2312']:
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
            text = re.sub(r'<br\s*/?>|</(p|div|h[1-6]|tr|li|blockquote)>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            text = text.replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
            text = re.sub(r'&\w+;', '', text)
            text = re.sub(r'[ \t]+', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()
            if text:
                chunks.append(text)

    return '\n\n'.join(chunks)


def split_5book_collection(epub_path, out_dir):
    full_text = extract_epub(epub_path)

    # 找到每本书的起始位置
    book_names = ['你坏', '我不', '好吗好的', '阿弥陀佛么么哒', '乖，摸摸头']
    positions = []

    for book_name in book_names:
        # 搜索多个可能的标题标记
        markers = [book_name]
        if book_name == '乖，摸摸头':
            markers.append('乖，摸摸头')
        for marker in markers:
            # 找到大标题位置（通常出现在目录或章节开头）
            for m in re.finditer(re.escape(marker), full_text):
                idx = m.start()
                # 排除目录中的引用（前面5000字通常是版权页和目录）
                if idx > 3000:
                    positions.append((idx, book_name))
                    break
            if any(p[1] == book_name for p in positions):
                break

    positions.sort(key=lambda x: x[0])
    log(f"  找到 {len(positions)} 本书的边界")

    saved = []
    for i, (pos, book_name) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else len(full_text)
        book_text = full_text[pos:end].strip()
        # 去掉开头的书名
        book_text = re.sub(r'^[\s]*' + re.escape(book_name) + r'[\s]*', '', book_text, count=1)

        fname = book_name.replace('，', '').replace(' ', '') + '.txt'
        fpath = os.path.join(out_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(book_text)
        saved.append((book_name, len(book_text), fpath))
        log(f"  OK {book_name}: {len(book_text):,} 字 -> {fname}")

    return saved


def extract_single(epub_path, book_name, out_dir):
    text = extract_epub(epub_path)
    fname = book_name.replace('，', '').replace(' ', '') + '.txt'
    fpath = os.path.join(out_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)
    log(f"  OK {book_name}: {len(text):,} 字 -> {fname}")
    return (book_name, len(text), fpath)


# ===== 主流程 =====
log("="*60)
log("大冰语料库提取器 v1.0")
log("="*60)

results = []

# 1. 单本epub
single_epubs = [
    (r"他们最幸福 (大冰 著 [著, 大冰]) (Z-Library).epub", "他们最幸福"),
    (r"小孩（现象级畅销书作家大冰2019年全新作品。于无常处知有情， 于有情处知众生。 ） (大冰) (z-library.sk, 1lib.sk, z-lib.sk).epub", "小孩"),
    (r"保重 (大冰) (z-library.sk, 1lib.sk, z-lib.sk).epub", "保重"),
]

for epub_name, book_name in single_epubs:
    epub_path = os.path.join(EPUB_DIR, epub_name)
    log(f"\n提取: {book_name}")
    if os.path.exists(epub_path):
        r = extract_single(epub_path, book_name, OUT_DIR)
        results.append(r)
    else:
        log(f"  FAIL 文件不存在: {epub_path}")

# 2. 5合1作品集
log(f"\n提取: 大冰作品集（5册）- 拆分为5本")
five_book = os.path.join(EPUB_DIR, "大冰作品集（5册） (大冰) (Z-Library).epub")
if os.path.exists(five_book):
    saved = split_5book_collection(five_book, OUT_DIR)
    results.extend(saved)
else:
    log(f"  FAIL 文件不存在: {five_book}")

# 汇总
log(f"\n{'='*60}")
log("语料库提取完成！")
total_chars = sum(r[1] for r in results)
log(f"共 {len(results)} 本书, {total_chars:,} 字")
log(f"\n输出目录: {OUT_DIR}")
log("\n各书字数:")
for name, chars, path in sorted(results, key=lambda x: -x[1]):
    log(f"  {name}: {chars:,} 字")

meta = {"books": [{"name": n, "chars": c, "file": os.path.basename(p)} for n, c, p in results], "total_chars": total_chars}
with open(os.path.join(OUT_DIR, '..', 'metadata.json'), 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
log("\n元数据已保存: metadata.json")

# 写日志
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
