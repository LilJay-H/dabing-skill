# -*- coding: utf-8 -*-
"""
大冰语料库分析器：从真实文本提取精确语言特征
输出：精确的金句库、高频词典、句式模板、结构分析
"""
import os, re, json
from collections import Counter, defaultdict

BOOKS_DIR = r"C:\Users\kk\da-bing-corpus\books"
OUT_DIR = r"C:\Users\kk\da-bing-corpus\analysis"
os.makedirs(OUT_DIR, exist_ok=True)

# ===== 加载全部语料 =====
corpus = {}
for fn in os.listdir(BOOKS_DIR):
    if fn.endswith('.txt'):
        name = fn.replace('.txt', '')
        with open(os.path.join(BOOKS_DIR, fn), 'r', encoding='utf-8') as f:
            corpus[name] = f.read()

print(f"加载了 {len(corpus)} 本书, 总计 {sum(len(v) for v in corpus.values()):,} 字")
print()

# ===== 1. 金句提取 =====
def extract_golden_sentences(text, min_len=8, max_len=80):
    """提取可能的金句：短句、有哲理感、常被引用的句子"""
    sentences = re.split(r'[。！？\n]', text)
    candidates = []
    for s in sentences:
        s = s.strip()
        length = len(s)
        if min_len <= length <= max_len:
            score = 0
            # 有对仗/排比特征
            if re.search(r'，.*，.*，', s): score += 2
            if re.search(r'[。；]', s) == None and '——' in s: score += 1
            # 有"愿"、"请"等祝福开头
            if s.startswith(('愿', '请', '祝')): score += 2
            # 有核心意象
            for kw in ['江湖', '流浪', '故事', '缘', '善良', '善意', '天涯', '自由',
                       '星光', '赶路人', '风尘', '平行世界', '自洽', '平视',
                       '朝九晚五', '浪迹', '梦', '酒', '眼泪', '命运']:
                if kw in s: score += 1
            # 有排比/重复结构
            if s.count('，') >= 2 and len(set(s.split('，'))) <= len(s.split('，')) * 0.7: score += 1
            # 包含口语特色
            for kw in ['乖', '摸摸头', '阿弥陀佛', '好吗好的', '算球', '他奶奶的',
                       '你坏', '咱', '打哭你', '保重']:
                if kw in s: score += 1
            if score >= 3:
                candidates.append((s, score))

    candidates.sort(key=lambda x: -x[1])
    return candidates

print("=== 金句提取 ===")
all_golden = {}
for name, text in corpus.items():
    golden = extract_golden_sentences(text)
    all_golden[name] = golden
    print(f"  {name}: {len(golden)} 条候选金句")
    for s, score in golden[:5]:
        print(f"    [{score}] {s}")

with open(os.path.join(OUT_DIR, 'golden_sentences.json'), 'w', encoding='utf-8') as f:
    json.dump({k: [{"text": s, "score": sc} for s, sc in v] for k, v in all_golden.items()},
              f, ensure_ascii=False, indent=2)

# ===== 2. 高频词分析 =====
print("\n=== 高频词分析 ===")
all_text = '\n'.join(corpus.values())

# 2-4字词组频率
words_2 = re.findall(r'[一-鿿]{2}', all_text)
words_3 = re.findall(r'[一-鿿]{3}', all_text)
words_4 = re.findall(r'[一-鿿]{4}', all_text)

counter_2 = Counter(words_2)
counter_3 = Counter(words_3)
counter_4 = Counter(words_4)

print(f"\n  二字高频词 TOP 30:")
for w, c in counter_2.most_common(30):
    print(f"    {w}: {c}")

print(f"\n  三字高频词 TOP 20:")
for w, c in counter_3.most_common(20):
    print(f"    {w}: {c}")

print(f"\n  四字高频词 TOP 20:")
for w, c in counter_4.most_common(20):
    print(f"    {w}: {c}")

# 保存
with open(os.path.join(OUT_DIR, 'word_frequency.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'bigrams': counter_2.most_common(100),
        'trigrams': counter_3.most_common(80),
        'quadgrams': counter_4.most_common(60),
    }, f, ensure_ascii=False, indent=2)

# ===== 3. 句式模式分析 =====
print("\n=== 句式模式分析 ===")
sentence_patterns = defaultdict(list)

for name, text in corpus.items():
    sentences = re.split(r'[。\n]', text)
    for s in sentences:
        s = s.strip()
        if len(s) < 6 or len(s) > 60:
            continue

        # 模式1: "有人……有人……有人……"
        if re.search(r'有人.*有人.*有人', s):
            sentence_patterns['有人排比'].append(s)
        # 模式2: "不是……不是……是……"
        if re.search(r'不是.*不是', s) and '是' in s:
            sentence_patterns['三段否定'].append(s)
        # 模式3: "XX也好，XX也好"
        if re.search(r'[^，]+也好.*[^，]+也好', s):
            sentence_patterns['也好并列'].append(s)
        # 模式4: "愿……"
        if s.startswith('愿'):
            sentence_patterns['愿字祝福'].append(s)
        # 模式5: "请……"
        if s.startswith('请'):
            sentence_patterns['请字祈使'].append(s)
        # 模式6: "你真以为"
        if '你真以为' in s or '你以为' in s:
            sentence_patterns['反问颠覆'].append(s)
        # 模式7: "……罢了"/"……而已"
        if s.endswith(('罢了', '而已')):
            sentence_patterns['降调收束'].append(s)
        # 模式8: 短断言 "XX就是XX" / "XX是XX"
        if re.match(r'^[一-鿿]{2,8}就是[一-鿿]{2,8}$', s.replace('，', '')):
            sentence_patterns['断言定义'].append(s)
        # 模式9: "缘深缘浅"
        if '缘' in s and ('深' in s or '浅' in s or '聚' in s or '散' in s):
            sentence_patterns['缘分句式'].append(s)

for pattern, examples in sentence_patterns.items():
    print(f"\n  [{pattern}] {len(examples)} 例:")
    for ex in examples[:4]:
        print(f"    {ex}")

with open(os.path.join(OUT_DIR, 'sentence_patterns.json'), 'w', encoding='utf-8') as f:
    json.dump({k: v[:20] for k, v in sentence_patterns.items()},
              f, ensure_ascii=False, indent=2)

# ===== 4. 段落结构分析 =====
print("\n=== 段落长度分布 ===")
for name, text in corpus.items():
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    para_lens = [len(p) for p in paragraphs]
    if para_lens:
        avg = sum(para_lens) / len(para_lens)
        med = sorted(para_lens)[len(para_lens)//2]
        short_pct = sum(1 for l in para_lens if l < 50) / len(para_lens) * 100
        print(f"  {name}: {len(paragraphs)}段, 平均{avg:.0f}字, 中位{med}字, 短段(<50字){short_pct:.0f}%")

# ===== 5. 口语/书面语比例 =====
print("\n=== 口语特征检测 ===")
oral_markers = ['咱', '呗', '嘛', '哈', '啦', '哎', '哟', '嗯', '呃',
                '你说', '我跟你说', '不是', '真的', '其实', '就是说',
                '算球', '他奶奶的', '真他妈', '他喵', '打哭你']
literary_markers = ['于', '之', '乎', '者', '也', '矣', '焉', '哉',
                    '何以', '是以', '故而', '纵', '亦', '遂', '乃']

for name, text in corpus.items():
    oral_count = sum(text.count(m) for m in oral_markers)
    lit_count = sum(text.count(m) for m in literary_markers)
    total_chars = len(text)
    oral_pct = oral_count / total_chars * 1000
    lit_pct = lit_count / total_chars * 1000
    print(f"  {name}: 口语标记{oral_count}次({oral_pct:.1f}‰), 书面标记{lit_count}次({lit_pct:.1f}‰)")

# ===== 6. 核心意象词频 =====
print("\n=== 核心意象词频（每千字） ===")
imagery_words = ['江湖', '故事', '流浪', '远方', '酒', '歌', '梦', '路',
                 '丽江', '西藏', '新疆', '大理', '小屋', '星空', '风',
                 '雪', '山', '海', '夜', '光', '命', '缘', '善']

for name, text in corpus.items():
    per_1k = {w: text.count(w) / len(text) * 1000 for w in imagery_words if text.count(w) > 0}
    top_imagery = sorted(per_1k.items(), key=lambda x: -x[1])[:8]
    print(f"  {name}: {', '.join(f'{w}({v:.1f})' for w, v in top_imagery)}")

print("\n分析完成！输出目录:", OUT_DIR)
