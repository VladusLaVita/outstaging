#!/usr/bin/env python3
"""
Синхронизатор статей Knowledge Base.
Источник: папка data/ в корне проекта (и в GitHub репозитории).
Назначения:
  - rag/knowledge-base/data/ (для RAG-индексации)
  - site/docs/articles/      (для VitePress)
"""
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

# 🎯 ЕДИНЫЙ ИСТОЧНИК: папка data/ в корне проекта
DATA_ROOT = PROJECT_ROOT / "data"

# Пути назначения
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
    """Синхронизирует папку: копирует новые/изменённые, удаляет отсутствующие в источнике."""
    dest.mkdir(parents=True, exist_ok=True)
    source_files = {f.name for f in source.glob("*.md")}
    
    # 1. Копируем новые и изменённые
    for src_file in source.glob("*.md"):
        dst_file = dest / src_file.name
        if not dst_file.exists() or file_hash(src_file) != file_hash(dst_file):
            shutil.copy2(src_file, dst_file)
            print(f"   {'✅ Обновлено' if dst_file.exists() else '🆕 Добавлено'}: {src_file.name}")
    
    # 2. Удаляем файлы, которых нет в источнике
    for dst_file in list(dest.glob("*.md")):
        if dst_file.name not in source_files:
            dst_file.unlink()
            print(f"   🗑️  Удалено из {dest.name}: {dst_file.name}")
    
    return source_files

def update_kb():
    print(f"📂 Корень проекта: {PROJECT_ROOT}")
    print(f"💾 Источник статей: {DATA_ROOT}")
    
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    
    # 1️⃣ Скачиваем актуальные статьи из GitHub -> в локальную data/
    print("\n📥 Синхронизация с GitHub (папка data/)...")
    github_count = 0
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_repo = Path(tmp_dir) / "kb-repo"
        run_cmd(["git", "clone", "--depth=1", "--filter=blob:none", "--no-checkout", REPO_URL, str(tmp_repo)])
        run_cmd(["git", "sparse-checkout", "init", "--cone"], cwd=tmp_repo)
        run_cmd(["git", "sparse-checkout", "set", "data"], cwd=tmp_repo)  # 👈 КОРНЕВАЯ data/
        run_cmd(["git", "checkout", BRANCH], cwd=tmp_repo)
        
        github_source = tmp_repo / "data"
        if github_source.exists():
            github_files = {f.name for f in github_source.glob("*.md")}
            github_count = len(github_files)
            
            # Копируем/обновляем
            for f in github_source.glob("*.md"):
                dst = DATA_ROOT / f.name
                if not dst.exists() or file_hash(f) != file_hash(dst):
                    shutil.copy2(f, dst)
                    print(f"   📥 Скачано/обновлено: {f.name}")
                    
            # Удаляем локальные файлы, которых нет на GitHub
            for local_md in list(DATA_ROOT.glob("*.md")):
                if local_md.name not in github_files:
                    local_md.unlink()
                    print(f"   🗑️  Удалено локально (нет на GitHub): {local_md.name}")
        else:
            print(f"⚠️ Папка data/ не найдена в репозитории на ветке {BRANCH}")

    print(f"✅ В локальной data/: {len(list(DATA_ROOT.glob('*.md')))} статей")

    # 2️⃣ Синхронизация ИЗ data/ → в rag/knowledge-base/data/
    print("\n🔄 Синхронизация: data/ → rag/knowledge-base/data/")
    synced_to_rag = sync_directory(DATA_ROOT, RAG_DATA_DIR)

    # 3️⃣ Синхронизация ИЗ data/ → в site/docs/articles/
    print("\n🔄 Синхронизация: data/ → site/docs/articles/")
    synced_to_site = sync_directory(DATA_ROOT, ARTICLES_DIR)

    # 4️⃣ Генерация articles.json
    print("\n📄 Генерация articles.json...")
    articles = []
    for md_file in sorted(DATA_ROOT.glob("*.md")):
        if md_file.name in synced_to_site:
            title, desc = extract_metadata(md_file)
            articles.append({
                "title": title,
                "path": f"/articles/{md_file.stem}",
                "description": desc,
                "filename": md_file.name
            })
    
    ARTICLES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    # 🎯 Итог
    print("\n" + "="*50)
    print("🎯 СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
    print("="*50)
    print(f"   • На GitHub: {github_count} статей")
    print(f"   • Локально data/: {len(list(DATA_ROOT.glob('*.md')))} файлов")
    print(f"   • Синхронизировано в rag/: {len(synced_to_rag)}")
    print(f"   • Синхронизировано в site/: {len(synced_to_site)}")
    print(f"   • Сгенерировано статей в JSON: {len(articles)}")
    print("="*50)

if __name__ == "__main__":
    update_kb()