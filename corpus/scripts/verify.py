# -*- coding: utf-8 -*-
"""验证提取的文本质量"""
import os, re, json

OUT_DIR = r"C:\Users\kk\da-bing-corpus\books"
VERIFY_LOG = r"C:\Users\kk\da-bing-corpus\verify_log.txt"

lines = []
def log(s): lines.append(s); print(s)

# 按出版年份排序的书名
book_order = ['他们最幸福', '乖摸摸头', '阿弥陀佛么么哒', '好吗好的', '我不', '你坏', '小孩', '保重']

with open(os.path.join(OUT_DIR, '..', 'metadata.json'), 'r', encoding='utf-8') as f:
    meta = json.load(f)

for book_info in meta['books']:
    name = book_info['name']
    fpath = os.path.join(OUT_DIR, book_info['file'])
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    log(f"\n{'='*60}")
    log(f"[{name}] {len(text):,} 字")

    # 检查质量指标
    lines_count = text.count('\n')
    avg_line_len = len(text) / max(lines_count, 1)

    # 高频字词
    words = re.findall(r'[一-鿿]+', text)
    word_len = len(words)

    # 统计前20个高频词（2-4字）
    from collections import Counter
    bigrams = re.findall(r'[一-鿿]{2,4}', text)
    top_words = Counter(bigrams).most_common(15)

    log(f"  总行数: {lines_count}, 平均行宽: {avg_line_len:.0f} 字符")
    log(f"  词/字组数: {word_len:,}")
    log(f"  高频词: {', '.join(f'{w}({c})' for w, c in top_words[:10])}")

    # 检查开头300字
    log(f"\n  --- 开头300字 ---")
    log(f"  {text[:300].replace(chr(10), ' ')}")

    # 检查结尾200字
    log(f"\n  --- 结尾200字 ---")
    log(f"  {text[-200:].replace(chr(10), ' ')}")

    # 检查是否有残留HTML标签
    tags = re.findall(r'<[^>]+>', text)
    if tags:
        log(f"  [!] 残留HTML标签: {len(tags)} 个: {tags[:5]}")
    else:
        log(f"  [OK] 无残留HTML")

    # 检查是否有异常字符
    non_cjk = re.findall(r'[^一-鿿　-〿＀-￯ -~\n\r\t]', text)
    if len(non_cjk) > len(text) * 0.1:
        log(f"  [!] 非中英文字符占比: {len(non_cjk)/len(text)*100:.1f}%")

with open(VERIFY_LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
