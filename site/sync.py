#!/usr/bin/env python3
import subprocess
import shutil
import sys
import json
import re
import os
from pathlib import Path
import tempfile
import hashlib

REPO_URL = "https://github.com/svyatoylol/knowledgebse.git"
BRANCH = "main"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 🎯 ЕДИНЫЙ ИСТОЧНИК ПРАВДЫ: папка data в корне проекта
DATA_ROOT = PROJECT_ROOT / "data"  # ← Новая центральная папка

# Пути назначения (куда копируем)
RAG_DATA_DIR = PROJECT_ROOT / "rag" / "knowledge-base" / "data"
ARTICLES_DIR = PROJECT_ROOT / "site" / "docs" / "articles"
ARTICLES_JSON = PROJECT_ROOT / "site" / "public" / "articles.json"

def run_cmd(cmd, cwd=None):
    print(f"🔄 {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)

def file_hash(path: Path) -> str:
    """Вычисляет MD5-хэш файла для сравнения изменений"""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def extract_metadata(file_path: Path):
    try:
        text = file_path.read_text(encoding="utf-8")[:600]
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
        title_match = re.search(r'^#+\s+(.*)', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem.replace('-', ' ').title()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
        desc = paragraphs[0][:120] + '...' if paragraphs else ""
        return title, desc
    except:
        return file_path.stem, ""

def sync_directory(source: Path, dest: Path) -> set:
    """
    Синхронизирует папку: копирует новые/изменённые файлы, удаляет отсутствующие в источнике.
    Возвращает множество имён файлов, которые есть в источнике.
    """
    dest.mkdir(parents=True, exist_ok=True)
    source_files = {f.name for f in source.glob("*.md")}
    
    # 1. Копируем новые и изменённые файлы
    for src_file in source.glob("*.md"):
        dst_file = dest / src_file.name
        needs_copy = True
        
        if dst_file.exists():
            if file_hash(src_file) == file_hash(dst_file):
                needs_copy = False
        
        if needs_copy:
            shutil.copy2(src_file, dst_file)
            action = "✅ Обновлено" if dst_file.exists() else "🆕 Добавлено"
            print(f"   {action}: {src_file.name}")
    
    # 2. Удаляем файлы, которых нет в источнике
    for dst_file in list(dest.glob("*.md")):
        if dst_file.name not in source_files:
            dst_file.unlink()
            print(f"   🗑️  Удалено из {dest.name}: {dst_file.name}")
    
    return source_files

def update_kb():
    print(f"📂 Корень проекта: {PROJECT_ROOT}")
    print(f"💾 Источник статей: {DATA_ROOT}")
    
    # 🎯 Создаём папку data в корне, если нет
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Если data пустая — пробуем скачать из репо (первый запуск)
    if not any(DATA_ROOT.glob("*.md")):
        print("📥 Папка data/ пустая. Скачиваем статьи из репозитория...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_repo = Path(tmp_dir) / "kb-repo"
            run_cmd(["git", "clone", "--depth=1", "--filter=blob:none", "--no-checkout", REPO_URL, str(tmp_repo)])
            run_cmd(["git", "sparse-checkout", "init", "--cone"], cwd=tmp_repo)
            run_cmd(["git", "sparse-checkout", "set", "rag/knowledge-base/data"], cwd=tmp_repo)
            run_cmd(["git", "checkout", BRANCH], cwd=tmp_repo)
            
            source = tmp_repo / "rag" / "knowledge-base" / "data"
            if source.exists():
                for f in source.glob("*.md"):
                    shutil.copy2(f, DATA_ROOT / f.name)
                print(f"✅ Скачано {len(list(DATA_ROOT.glob('*.md')))} статей в data/")
            else:
                print("⚠️ Не удалось скачать статьи. Создайте файлы вручную в data/")

    # 🔄 Синхронизация ИЗ data/ → в rag/data (для RAG)
    print("\n🔄 Синхронизация: data/ → rag/knowledge-base/data/")
    synced_to_rag = sync_directory(DATA_ROOT, RAG_DATA_DIR)
    print(f"✅ В rag/data: {len(synced_to_rag)} статей")

    # 🔄 Синхронизация ИЗ data/ → в site/docs/articles (для VitePress)
    print("\n🔄 Синхронизация: data/ → site/docs/articles/")
    synced_to_site = sync_directory(DATA_ROOT, ARTICLES_DIR)
    print(f"✅ В site/docs/articles: {len(synced_to_site)} статей")

    # 📄 Генерация articles.json (только актуальные статьи из data/)
    articles = []
    for md_file in sorted(DATA_ROOT.glob("*.md")):  # sorted для стабильного порядка
        if md_file.name in synced_to_site:
            title, desc = extract_metadata(md_file)
            articles.append({
                "title": title,
                "path": f"/articles/{md_file.stem}",
                "description": desc,
                "filename": md_file.name  # ← Добавляем имя файла для отладки
            })
    
    ARTICLES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Сгенерирован: {ARTICLES_JSON} ({len(articles)} статей)")

    # 🎯 Итог
    print("\n🎯 Синхронизация завершена:")
    print(f"   • Источник: {DATA_ROOT} ({len(list(DATA_ROOT.glob('*.md')))} файлов)")
    print(f"   • Синхронизировано: {len(synced_to_rag)} статей")
    print(f"   • Удалено устаревших: {len(list(ARTICLES_DIR.glob('*.md'))) - len(synced_to_site)}")

if __name__ == "__main__":
    update_kb()