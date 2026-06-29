#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量下载2025年补税公告PDF"""

import csv, os, re, time, requests

CSV_PATH = "/Users/datamine/Desktop/个人web/all_tax_announcements_2025.csv"
PDF_DIR = "/Users/datamine/Desktop/个人web/补税公告PDF_2025"
HEADERS = {"User-Agent": "Mozilla/5.0"}
os.makedirs(PDF_DIR, exist_ok=True)

def extract_ann_id(url):
    m = re.search(r'/detail/[A-Z0-9]+/(AN\d+)\.html', url)
    return m.group(1) if m else None

def download(ann_id, code, name, date_str):
    pdf_url = f"http://pdf.dfcfw.com/pdf/H2_{ann_id}_1.pdf"
    safe = re.sub(r'[\\/:*?"<>|]', '', name)
    fname = f"{safe}_{code}_{date_str}.pdf"
    fpath = os.path.join(PDF_DIR, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 1000:
        return True, "已存在"
    try:
        r = requests.get(pdf_url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(fpath, 'wb') as f: f.write(r.content)
            return True, f"{len(r.content)//1024}KB"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"共 {len(rows)} 条公告")
ok = fail = 0
for i, row in enumerate(rows, 1):
    url = row.get('url', '')
    code = row.get('code', '')
    name = row.get('name', '')
    date_s = row.get('date', '').replace('-', '')
    ann_id = extract_ann_id(url)
    if not ann_id:
        print(f"[{i}/{len(rows)}] ⚠️ {code} {name} - 无法提取ID"); fail += 1; continue
    ok_flag, msg = download(ann_id, code, name, date_s)
    status = "✅" if ok_flag else "❌"
    print(f"[{i}/{len(rows)}] {status} {code} {name} ({msg})")
    if ok_flag: ok += 1
    else: fail += 1
    time.sleep(0.5)

print(f"\n完成！成功: {ok}, 失败: {fail}")
