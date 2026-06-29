#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载已抓取的补税公告PDF文件
从 all_tax_announcements.csv 读取公告URL，提取ID后下载PDF
"""

import csv
import os
import re
import time
import requests

CSV_PATH = "/Users/datamine/Desktop/个人web/all_tax_announcements.csv"
PDF_DIR = "/Users/datamine/Desktop/个人web/补税公告PDF"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_ann_id(url):
    """从东方财富公告URL中提取公告ID"""
    # 格式: https://data.eastmoney.com/notices/detail/002400/AN202603021820194164.html
    m = re.search(r'/detail/[A-Z0-9]+/(AN\d+)\.html', url)
    if m:
        return m.group(1)
    return None

def download_pdf(ann_id, code, name, date_str):
    """尝试下载PDF"""
    # 东方财富PDF URL格式
    pdf_url = f"http://pdf.dfcfw.com/pdf/H2_{ann_id}_1.pdf"
    
    # 安全文件名
    safe_name = re.sub(r'[\\/:*?"<>|]', '', name)
    filename = f"{safe_name}_{code}_{date_str}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  ⏭ 已存在: {filename}")
        return True
    
    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            print(f"  ✅ {filename} ({len(resp.content)//1024}KB)")
            return True
        else:
            print(f"  ⚠️ 下载失败({resp.status_code}): {filename}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {filename} - {e}")
        return False

def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"共 {len(rows)} 条公告记录")
    success = 0
    fail = 0
    
    for i, row in enumerate(rows, 1):
        url = row.get('url', '')
        code = row.get('code', '')
        name = row.get('name', '')
        date_str = row.get('date', '').replace('-', '')
        
        ann_id = extract_ann_id(url)
        if not ann_id:
            print(f"[{i}/{len(rows)}] ⚠️ 无法提取ID: {code} {name}")
            fail += 1
            continue
        
        print(f"[{i}/{len(rows)}] {code} {name} ({date_str})...", end=" ")
        if download_pdf(ann_id, code, name, date_str):
            success += 1
        else:
            fail += 1
        
        time.sleep(0.5)  # 限速
    
    print(f"\n完成！成功: {success}, 失败: {fail}")

if __name__ == "__main__":
    main()
