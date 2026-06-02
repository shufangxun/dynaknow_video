---
name: dynaknow-git-lfs
description: Use this skill when versioning the DynaKnow video benchmark repository, especially when adding or updating media assets with Git LFS, pushing dataset iterations to GitHub, or checking that large media files are not committed as normal Git blobs.
---

# DynaKnow Git LFS Workflow

Use this workflow for `/root/public/jasonshu/dynaknow_video` unless the user points to another checkout.

## Core Rule

Text, metadata, scripts, docs, schemas, prompts, reports, and release files use normal Git. Everything under `media/**` must use Git LFS.

Do not add media to regular Git. Verify LFS tracking before committing media changes.

## Standard Update

1. Inspect state:

```bash
git status --short --branch
git remote -v
git lfs version
```

2. Ensure LFS is enabled and tracking media:

```bash
git lfs install
git lfs track 'media/**'
git add .gitattributes
```

Expected `.gitattributes` entry:

```gitattributes
media/** filter=lfs diff=lfs merge=lfs -text
```

3. Stage only intended changes. For broad benchmark updates, this is usually:

```bash
git add README.md data docs prompts release reports schemas scripts templates .gitignore .gitattributes
git add media
```

Do not stage Python caches or build trash. Keep these ignored:

```gitignore
__pycache__/
*.pyc
```

4. Verify before commit:

```bash
git lfs ls-files | wc -l
git lfs ls-files | head
git diff --cached --stat
git status --short
```

If newly staged media does not appear in `git lfs ls-files`, stop and fix `.gitattributes` before committing.

5. Commit and push:

```bash
git commit -m "Update benchmark dataset"
git push
```

For media-only updates, use a commit message like:

```bash
git commit -m "Update benchmark media assets"
```

## First-Time Setup

If `git lfs version` fails, install Git LFS first. On Ubuntu/Debian as root:

```bash
apt-get update
apt-get install -y git-lfs
```

If the repo has no commits yet:

```bash
git init
git branch -M main
git remote add origin <github-repo-url>
```

Make an initial text-only commit before large media if that keeps the workflow easier to debug.

## Failure Handling

- `src refspec main does not match any`: create a commit first, then push.
- GitHub rejects files over 100 MB: the file was staged as a normal Git blob; fix LFS tracking before recommitting.
- LFS upload fails for auth or quota: keep the local commit, report the exact error, and retry after credentials/quota are fixed.
- Do not rewrite published history with `git lfs migrate` unless the user explicitly asks. If a large file already entered published Git history, explain the tradeoff first.

## Useful Checks

Largest working tree files:

```bash
find . -type f -size +50M -printf '%s %p\n' | sort -nr | head
```

Media file type counts:

```bash
find media -type f | sed 's/.*\\.//' | sort | uniq -c | sort -nr
```

Recent history:

```bash
git log --oneline -5
```
