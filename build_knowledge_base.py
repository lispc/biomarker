#!/usr/bin/env python3
"""
构建生物标志物知识库
读取 marker.csv，为每个生物标志物生成说明文档
"""

import argparse
import csv
import os
import sys
from query import query_biomarker


def is_file_exists_and_not_empty(filepath: str) -> bool:
    """检查文件是否存在且不为空"""
    return os.path.exists(filepath) and os.path.getsize(filepath) > 0


def build_filename(index: int, name_en: str, name_cn: str, category: str, output_dir: str) -> str:
    """构建文件名路径，用于检查文件是否存在"""
    # 与 query.py 中的 buildFilename 逻辑保持一致
    # 只替换 / 和 \，保留 | 作为分隔符
    safe_name_en = name_en.replace("/", "-").replace("\\", "-")
    safe_name_cn = name_cn.replace("/", "-").replace("\\", "-")
    safe_category = category.replace("/", "-").replace("\\", "-").strip()
    filename = f"{index:03d}|{safe_name_en}|{safe_name_cn}.md"
    return os.path.join(output_dir, safe_category, filename)


def main():
    parser = argparse.ArgumentParser(
        description="构建生物标志物知识库，为每个标志物生成说明文档"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制处理的条目数量（默认处理所有未完成的条目）",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="marker.csv",
        help="CSV 文件路径（默认: marker.csv）",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="docs/assets",
        help="输出目录（默认: docs/assets）",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="起始行号（从1开始，默认: 1）",
    )
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 读取 CSV
    markers = []
    with open(args.csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if idx < args.start:
                continue
            markers.append({
                "index": idx,
                "category": row.get("category", ""),
                "name_en": row.get("Biomarkers_en", ""),
                "name_cn": row.get("Biomarkers_cn", ""),
            })
    
    print(f"总共读取到 {len(markers)} 个生物标志物（从第 {args.start} 行开始）")
    
    # 统计需要处理的和已跳过的
    to_process = []
    skipped = []
    
    for marker in markers:
        filepath = build_filename(
            marker["index"], marker["name_en"], marker["name_cn"], marker["category"], args.output_dir
        )
        if is_file_exists_and_not_empty(filepath):
            skipped.append(marker)
        else:
            to_process.append(marker)
    
    print(f"已存在且非空，将跳过: {len(skipped)} 个")
    print(f"需要处理: {len(to_process)} 个")
    
    # 应用 limit
    if args.limit is not None:
        to_process = to_process[:args.limit]
        print(f"根据 --limit={args.limit}，实际将处理: {len(to_process)} 个")
    
    # 处理每个标志物
    success_count = 0
    fail_count = 0
    
    for i, marker in enumerate(to_process, start=1):
        print(f"\n[{i}/{len(to_process)}] 处理: {marker['name_en']} ({marker['name_cn']}) - 行号 {marker['index']}")
        
        try:
            filepath = query_biomarker(
                index=marker["index"],
                name_en=marker["name_en"],
                name_cn=marker["name_cn"],
                category=marker["category"],
                output_dir=args.output_dir,
            )
            print(f"    ✓ 已保存到: {filepath}")
            success_count += 1
        except Exception as e:
            print(f"    ✗ 处理失败: {e}")
            fail_count += 1
            # 继续处理下一个
    
    print(f"\n{'='*50}")
    print(f"处理完成!")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"跳过（已存在）: {len(skipped)} 个")


if __name__ == "__main__":
    main()
