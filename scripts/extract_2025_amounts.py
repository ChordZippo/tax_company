#!/usr/bin/env python3
"""从2025年补税公告PDF中提取补税金额"""
import os, re, json, csv
from PyPDF2 import PdfReader

PDF_DIR = "/Users/datamine/Desktop/个人web/补税公告PDF_2025"
CSV_PATH = "/Users/datamine/Desktop/个人web/all_tax_announcements_2025.csv"
OUT_JSON = "/Users/datamine/Desktop/个人web/data_2025_amounts.json"

# 金额匹配模式
AMOUNT_PATTERNS = [
    r'(?:补缴|补[税税款]{1,3}|缴纳|补[缴]?)[^。]*?(?:合计|共计|共)?[^。]*?(\d+[.,]\d+)\s*(?:万?元|万元|亿)',
    r'(?:合计|共计|共)[^。]*?(\d+[.,]\d+)\s*(?:万?元|万元)',
    r'(?:税款及滞纳金|税款和滞纳金)[^。]*?(?:合计|共计|共)[^。]*?(\d+[.,]\d+)\s*(?:万?元|万元)',
    r'(?:需补缴|应补缴)[^。]*?(\d+[.,]\d+)\s*(?:万?元|万元|亿)',
]

def extract_amounts(text):
    """从文本中提取补税金额"""
    amounts = []
    for pattern in AMOUNT_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                val = float(m.replace(',', ''))
                # 判断是亿级还是万级
                if '亿元' in text or '亿' in text:
                    val = val * 10000
                amounts.append(val)
            except:
                pass
    return amounts

def parse_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages[:3]:
            text += page.extract_text() or ""
        return text
    except:
        return ""

# 读取CSV获取公司列表
companies = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        companies.append(r)

results = []
for i, c in enumerate(companies):
    safe = re.sub(r'[\\/:*?"<>|]', '', c['name'])
    date_str = c['date'].replace('-', '')
    pdf_name = f"{safe}_{c['code']}_{date_str}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_name)
    
    if not os.path.exists(pdf_path):
        print(f"[{i+1}/{len(companies)}] ❌ {c['name']} - PDF不存在")
        results.append({'name': c['name'], 'code': c['code'], 'amount': 0, 'valid': False})
        continue
    
    text = parse_pdf(pdf_path)
    if not text.strip():
        print(f"[{i+1}/{len(companies)}] ⚠️ {c['name']} - 无法解析")
        results.append({'name': c['name'], 'code': c['code'], 'amount': 0, 'valid': False})
        continue
    
    amounts = extract_amounts(text)
    if amounts:
        max_amt = max(amounts)
        print(f"[{i+1}/{len(companies)}] ✅ {c['name']} - {max_amt:.0f}万元")
        results.append({'name': c['name'], 'code': c['code'], 'amount': round(max_amt), 'valid': True})
    else:
        print(f"[{i+1}/{len(companies)}] ⚠️ {c['name']} - 未找到金额")
        results.append({'name': c['name'], 'code': c['code'], 'amount': 0, 'valid': False})

# 保存结果
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

found = sum(1 for r in results if r['valid'])
total = sum(r['amount'] for r in results)
print(f"\n完成！共提取 {found}/{len(results)} 家公司的补税金额，合计约 {total/10000:.1f} 亿元")
