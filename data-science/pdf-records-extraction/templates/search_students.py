#!/usr/bin/env python3
"""查询学生信息：姓名、身份证号、页码
用法:
  python search_students.py <姓名或身份证号>
  python search_students.py 4403*727    # 身份证号支持 * 通配符
"""
import csv, re, sys

def search(query, rows):
    results = []
    for r in rows:
        name = r.get("姓名", "")
        idnum = r.get("身份证号", "")
        if "*" in query:
            pattern = "^" + re.escape(query).replace(r"\*", ".*") + "$"
            if re.match(pattern, idnum):
                results.append(r)
                continue
        if query.lower() in name.lower():
            results.append(r)
            continue
        if query in idnum:
            results.append(r)
            continue
    return results

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    query = sys.argv[1].strip()
    with open("students.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    results = search(query, rows)
    if not results:
        print(f"未找到匹配: {query}")
        return
    max_name = max(len(r["姓名"]) for r in results)
    print(f"{'姓名':<{max_name+2}} 证件号{'':<14}页码")
    print("-" * (max_name + 40))
    for r in results:
        print(f"{r['姓名']:<{max_name+2}} {r['身份证号']:<22} {r.get('页码', '')}")

if __name__ == "__main__":
    main()
