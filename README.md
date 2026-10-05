# booklog

终端读书记录：加书、记进度、完结打分、看年度统计。纯 Python 标准库，数据是本地 JSON。

## 安装

零依赖，Python 3.10+：

```bash
cd booklog
python3 -m booklog --help
```

## 用法

```bash
# 加书
booklog add "三体" --author "刘慈欣" --pages 300

# 记进度
booklog progress "三体" 150

# 读完并打分（1-5）
booklog finish "三体" --rating 5

# 看书架
booklog list

# 年度统计
booklog stats
```

输出示例：

```
===== 在读 =====
  三体（刘慈欣）
    ██████████░░░░░░░░░░ 50%  150/300 页
===== 已读完 =====
  ✓ 流浪地球（刘慈欣）  ★★★★☆
```

数据默认存在 `~/.config/booklog.json`，用 `--data 路径` 覆盖（也方便测试）。

## 设计取舍

- 进度按页码记，不记章节——页码最通用。
- `stats` 只统计当年读完的书；想看历年，把 JSON 拿去自己算。
- 数据文件原子写入（写临时文件再 `os.replace`），不怕 Ctrl-C 写坏一半。

## 已知局限

- 单机 JSON，无同步、无多设备。
- 评分只有 1–5 整数，没有半星。
- 没有提醒"该读书了"的功能——那是 habit 的活。

## License

MIT，见 [LICENSE](LICENSE)。
