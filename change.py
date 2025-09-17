#!/usr/bin/env python3
import os
import shutil

# --- CONFIG ---
BREACHES_DIR = "breaches"  # 👈 This is where your .md files live
README_PATH = "README.md"

# Files and folders to IGNORE — both exact names and patterns
IGNORE_ITEMS = {
    # Files
    "README.md",
    "CNAME",
    "Gemfile",
    "Gemfile.lock",
    "404.html",
    "_config.yml",
    ".gitignore",
    "LICENSE",
    "CONTRIBUTING.md",
    # Folders (will skip if item is a directory and matches)
    ".github",
    "_layouts",
    "_includes",
    ".git",
    "_site",  # just in case
}

def should_ignore(item_name, is_dir=False):
    """Check if item should be ignored based on name or type."""
    if item_name in IGNORE_ITEMS:
        return True
    if is_dir and item_name in IGNORE_ITEMS:
        return True
    # Also ignore _config.*.yml variants
    if item_name.startswith("_config.") and item_name.endswith(".yml"):
        return True
    return False

def main():
    print("🔍 Scanning for breach markdown files...")

    # Check if breaches folder exists
    if not os.path.exists(BREACHES_DIR):
        print(f"❌ Folder '{BREACHES_DIR}/' not found. Please check path.")
        return

    # DEBUG: List all items in breaches folder
    print(f"\n📂 Files & folders in ./{BREACHES_DIR}/:")
    all_items = os.listdir(BREACHES_DIR)
    for item in all_items:
        full_path = os.path.join(BREACHES_DIR, item)
        if os.path.isdir(full_path):
            print(f"   📁 {item}/")
        else:
            print(f"   📄 {item}")
    print()

    # Step 1: Find all .md files (case-insensitive, excluding ignored ones)
    md_files = []
    for item in all_items:
        if item.lower().endswith(".md") and not should_ignore(item):
            md_files.append(item)

    if not md_files:
        print("❌ No markdown files found to convert.")
        print("💡 TIP: Check if files have .MD/.Md extensions or are in sub-subfolders.")
        return

    print(f"📁 Found {len(md_files)} breach files. Converting...")

    # Step 2: Create folders and move files INSIDE ./breaches/
    converted = []
    for md_file in md_files:
        # Remove extension properly (case-insensitive)
        name = os.path.splitext(md_file)[0]  # Better than slicing

        folder_path = os.path.join(BREACHES_DIR, name)
        index_path = os.path.join(folder_path, "index.md")

        # Safety check: don't overwrite existing folders unless empty
        if os.path.exists(folder_path) and os.listdir(folder_path):
            print(f"⚠️  Skipping {md_file} — folder '{name}/' already exists and is not empty.")
            continue

        # Create folder
        os.makedirs(folder_path, exist_ok=True)

        # Move file → folder/index.md
        src = os.path.join(BREACHES_DIR, md_file)
        shutil.move(src, index_path)

        converted.append(name)
        print(f"   ✅ {md_file} → {BREACHES_DIR}/{name}/index.md")

    print(f"🎉 Converted {len(converted)} files.")

    # Step 3: Update README.md — now links point to ./breaches/Name/
    if os.path.exists(README_PATH):
        print("📝 Updating README.md with new folder links...")
        with open(README_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_list = False
        new_lines = []
        skip_list = False

        for line in lines:
            if line.startswith("## 📂 List of Breaches"):
                in_list = True
                new_lines.append(line)
                # Generate new sorted list — now with ./breaches/ prefix
                new_links = [f"- [{name}](./{BREACHES_DIR}/{name}/)" for name in sorted(converted)]
                new_lines.extend([link + "\n" for link in new_links])
                skip_list = True
            elif in_list and (line.startswith("## ") or (line.strip() == "" and len(new_lines) > 1)):
                in_list = False
                skip_list = False
                new_lines.append(line)
            elif skip_list and line.strip().startswith("- ["):
                continue  # Skip old list items
            else:
                if not skip_list:
                    new_lines.append(line)

        # Write back
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print("✅ README.md updated successfully.")
    else:
        print(f"⚠️  {README_PATH} not found — skipping update.")

    print("\n✅ All done! Review changes and commit:")
    print("   git sdtatus")
    print("   git addd .")
    print('   git codmmit -m "chore: convert breaches to folder/index.md structure inside /breaches"')
    print("   git pudsh")

if __name__ == "__main__":
    main()