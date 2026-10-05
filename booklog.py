#!/usr/bin/env python3
"""booklog - 终端读书记录：加书、记进度、完结打分、看统计。纯标准库。"""
import argparse
import datetime
import json
import os
import sys

DEFAULT_DATA = os.path.join(os.path.expanduser("~"), ".config", "booklog.json")
BAR_W = 20


def err(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def load(path):
    if not os.path.exists(path):
        return {"books": []}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        err(f"数据文件损坏或不可读：{e}")


def save(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def find(books, title):
    for b in books:
        if b["title"] == title:
            return b
    return None


def bar(pct):
    filled = int(pct / 100 * BAR_W + 0.5)
    return "█" * filled + "░" * (BAR_W - filled)


def cmd_add(a):
    data = load(a.data)
    if find(data["books"], a.title):
        err(f"这本书已经在记录里：{a.title}")
    if a.pages is not None and a.pages <= 0:
        err("--pages 必须是正整数")
    data["books"].append({
        "title": a.title,
        "author": a.author or "",
        "pages": a.pages or 0,
        "current": 0,
        "status": "reading",
        "rating": 0,
        "added": datetime.date.today().isoformat(),
        "finished": "",
    })
    save(a.data, data)
    print(f"已加入书架：{a.title}")


def cmd_progress(a):
    data = load(a.data)
    b = find(data["books"], a.title)
    if not b:
        err(f"没有这本书：{a.title}")
    if b["status"] == "finished":
        err(f"这本书已经读完了：{a.title}")
    if a.page < 0:
        err("页码不能为负数")
    if b["pages"] and a.page > b["pages"]:
        err(f"页码超出总页数（{b['pages']}）")
    b["current"] = a.page
    save(a.data, data)
    pct = (a.page / b["pages"] * 100) if b["pages"] else 0
    print(f"{a.title}：读到第 {a.page} 页（{pct:.0f}%）")


def cmd_finish(a):
    data = load(a.data)
    b = find(data["books"], a.title)
    if not b:
        err(f"没有这本书：{a.title}")
    if b["status"] == "finished":
        err(f"这本书已经读完了：{a.title}")
    if not (1 <= a.rating <= 5):
        err("--rating 必须是 1-5 的整数")
    b["status"] = "finished"
    b["rating"] = a.rating
    if b["pages"]:
        b["current"] = b["pages"]
    b["finished"] = datetime.date.today().isoformat()
    save(a.data, data)
    print(f"读完啦：{a.title}，评分 {'★' * a.rating}{'☆' * (5 - a.rating)}")


def cmd_list(a):
    data = load(a.data)
    reading = [b for b in data["books"] if b["status"] == "reading"]
    finished = [b for b in data["books"] if b["status"] == "finished"]
    if not data["books"]:
        print("书架是空的。用 booklog add 加一本书吧。")
        return
    if reading:
        print("===== 在读 =====")
        for b in reading:
            pct = (b["current"] / b["pages"] * 100) if b["pages"] else 0
            au = f"（{b['author']}）" if b["author"] else ""
            pg = f"{b['current']}/{b['pages']} 页" if b["pages"] else f"第 {b['current']} 页"
            print(f"  {b['title']}{au}")
            print(f"    {bar(pct)} {pct:.0f}%  {pg}")
    if finished:
        print("===== 已读完 =====")
        for b in finished:
            stars = "★" * b["rating"] + "☆" * (5 - b["rating"]) if b["rating"] else "未评分"
            au = f"（{b['author']}）" if b["author"] else ""
            print(f"  ✓ {b['title']}{au}  {stars}")


def cmd_stats(a):
    data = load(a.data)
    year = str(datetime.date.today().year)
    done = [b for b in data["books"]
            if b["status"] == "finished" and b["finished"].startswith(year)]
    pages = sum(b["pages"] for b in done)
    rated = [b["rating"] for b in done if b["rating"]]
    avg = sum(rated) / len(rated) if rated else 0
    reading = sum(1 for b in data["books"] if b["status"] == "reading")
    print(f"===== {year} 年读书统计 =====")
    print(f"  读完：{len(done)} 本")
    print(f"  总页数：{pages} 页")
    print(f"  平均评分：{avg:.1f} / 5" if rated else "  平均评分：暂无评分")
    print(f"  在读：{reading} 本")


def build_parser():
    p = argparse.ArgumentParser(prog="booklog", description="终端读书记录：加书、记进度、完结打分。")
    p.add_argument("--version", action="version", version="booklog 0.1.0")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(s):
        s.add_argument("--data", default=DEFAULT_DATA, help="数据文件路径")

    s = sub.add_parser("add", help="加一本书")
    s.add_argument("title", help="书名")
    s.add_argument("--author", default="", help="作者")
    s.add_argument("--pages", type=int, default=0, help="总页数")
    common(s)

    s = sub.add_parser("progress", help="记录读到第几页")
    s.add_argument("title", help="书名")
    s.add_argument("page", type=int, help="当前页码")
    common(s)

    s = sub.add_parser("finish", help="标记读完并打分")
    s.add_argument("title", help="书名")
    s.add_argument("--rating", type=int, required=True, help="评分 1-5")
    common(s)

    s = sub.add_parser("list", help="列出书架")
    common(s)

    s = sub.add_parser("stats", help="年度统计")
    common(s)
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    {"add": cmd_add, "progress": cmd_progress, "finish": cmd_finish,
     "list": cmd_list, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
