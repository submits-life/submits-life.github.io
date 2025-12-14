#!/usr/bin/env python3
"""
最新のaudioファイルから_posts用のMarkdownファイルを生成するスクリプト
"""

import os
import glob
from datetime import datetime
from pathlib import Path

try:
    from mutagen.mp3 import MP3
except ImportError:
    print("mutagenライブラリが必要です。インストールしてください:")
    print("  pip install mutagen")
    exit(1)

# パス設定
SCRIPT_DIR = Path(__file__).parent
AUDIO_DIR = SCRIPT_DIR / "audio"
POSTS_DIR = SCRIPT_DIR / "_posts"

def get_latest_mp3():
    """audioフォルダから最新のmp3ファイルを取得"""
    mp3_files = list(AUDIO_DIR.glob("*.mp3"))
    if not mp3_files:
        print("audioフォルダにmp3ファイルが見つかりません")
        return None

    # 更新日時でソートして最新を取得
    latest = max(mp3_files, key=lambda f: f.stat().st_mtime)
    return latest

def parse_filename(mp3_path):
    """ファイル名から日付と話数を抽出 (例: 2025-12-13-25.mp3)"""
    stem = mp3_path.stem  # 拡張子なしのファイル名
    parts = stem.rsplit("-", 1)

    if len(parts) != 2:
        raise ValueError(f"ファイル名の形式が不正です: {mp3_path.name}")

    date_str = parts[0]  # 2025-12-13
    episode_num = parts[1]  # 25

    return date_str, episode_num

def get_audio_info(mp3_path):
    """mp3ファイルからdurationとファイルサイズを取得"""
    audio = MP3(str(mp3_path))
    duration_secs = audio.info.length

    # 秒をHH:MM:SS形式に変換
    hours = int(duration_secs // 3600)
    minutes = int((duration_secs % 3600) // 60)
    seconds = int(duration_secs % 60)
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    file_size = mp3_path.stat().st_size

    return duration_str, file_size

def check_post_exists(date_str, episode_num):
    """対応する_postファイルが既に存在するかチェック"""
    post_path = POSTS_DIR / f"{date_str}-{episode_num}.md"
    return post_path.exists(), post_path

def create_post(mp3_path, dry_run=False, force_info=False):
    """_posts用のMarkdownファイルを生成"""
    date_str, episode_num = parse_filename(mp3_path)
    duration_str, file_size = get_audio_info(mp3_path)

    exists, post_path = check_post_exists(date_str, episode_num)
    if exists and not force_info:
        print(f"既に存在します: {post_path}")
        return None

    # テンプレート
    content = f"""---
actor_ids:
  - koike
audio_file_path: /audio/{mp3_path.name}
audio_file_size: {file_size}
date: {date_str} 15:00:00 +0900
description: TODO: 説明を追加してください
duration: "{duration_str}"
layout: article
title: {episode_num}. TODO: タイトルを追加してください
---

## Show notes

- TODO: Show notesを追加してください
"""

    print(f"=== 生成情報 ===")
    print(f"MP3ファイル: {mp3_path.name}")
    print(f"日付: {date_str}")
    print(f"話数: {episode_num}")
    print(f"duration: {duration_str}")
    print(f"ファイルサイズ: {file_size:,} bytes")
    print(f"出力先: {post_path}")
    print()

    if dry_run:
        print("=== プレビュー (dry-run) ===")
        print(content)
        return None

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"作成しました: {post_path}")
    return post_path

def main():
    import argparse

    parser = argparse.ArgumentParser(description="最新のmp3から_postファイルを生成")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="ファイルを作成せずにプレビューのみ表示")
    parser.add_argument("--info", "-i", action="store_true",
                        help="情報のみ表示（既存ファイルがあっても表示）")
    parser.add_argument("--file", "-f", type=str,
                        help="特定のmp3ファイルを指定（省略時は最新のファイル）")
    args = parser.parse_args()

    if args.file:
        mp3_path = Path(args.file)
        if not mp3_path.exists():
            mp3_path = AUDIO_DIR / args.file
        if not mp3_path.exists():
            print(f"ファイルが見つかりません: {args.file}")
            return
    else:
        mp3_path = get_latest_mp3()
        if not mp3_path:
            return

    create_post(mp3_path, dry_run=args.dry_run or args.info, force_info=args.info)

if __name__ == "__main__":
    main()
