# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository provides a reusable GitHub Actions workflow for automatically building and pushing Docker images to Docker Hub. It supports two different project structures:

1. Projects with a single Dockerfile in the root directory (e.g., li88iioo/Photonix)
2. Projects with multiple Dockerfiles in different subdirectories (e.g., JefferyHcool/BiliNote)

## Code Architecture

The system consists of two main workflow files:

1. `.github/workflows/docker-build-new.yml` - The core reusable workflow that handles the actual Docker build and push operations
2. `.github/workflows/main.yml` - The main workflow that defines which repositories to build

### Key Features

- Supports both single and multiple Dockerfile projects
- Configurable Dockerfile path and build context
- Automatic tag generation with date stamps and latest tags
- Reusable workflow design

## Common Development Tasks

### Adding New Repositories

To add a new repository to the build process, add a new job in `main.yml`. Here are some examples:

```yaml
jobs:
  # Build li88iioo/Photonix project (single Dockerfile in root)
  build-photonix:
    uses: ./.github/workflows/docker-build-new.yml
    with:
      source_repo: 'li88iioo/Photonix'
      docker_image_name: 'photonix'

  # Build JefferyHcool/BiliNote backend (Dockerfile in backend directory)
  build-bili-note-backend:
    uses: ./.github/workflows/docker-build-new.yml
    with:
      source_repo: 'JefferyHcool/BiliNote'
      docker_image_name: 'bili-note-backend'
      dockerfile_path: 'backend/Dockerfile'
      context_path: '.'

  # Build JefferyHcool/BiliNote frontend (Dockerfile in BillNote_frontend directory)
  build-bili-note-frontend:
    uses: ./.github/workflows/docker-build-new.yml
    with:
      source_repo: 'JefferyHcool/BiliNote'
      docker_image_name: 'bili-note-frontend'
      dockerfile_path: 'BillNote_frontend/Dockerfile'
      context_path: '.'
```

### Modifying Build Parameters

The reusable workflow supports several parameters:
- `source_repo`: Required Git repository to check out
- `docker_image_name`: Required Docker Hub image name
- `dockerfile_path`: Optional Dockerfile path (defaults to "Dockerfile")
- `context_path`: Optional build context path (defaults to ".")

### Testing Changes

工作流的测试和构建通过GitHub Actions自动触发。要测试更改：
1. 修改工作流文件（例如：`.github/workflows/docker-build-new.yml` 或 `.github/workflows/main.yml`）。
2. 提交并推送更改到仓库。
3. 或者通过GitHub Actions界面手动触发工作流。

**如何查看构建和测试状态：**
1. 访问GitHub仓库的 "Actions" 标签页。
2. 选择相应的工作流运行，查看其状态和日志。

**Linting / 类型检查：**
目前，此仓库中没有明确的linting或类型检查步骤。工作流主要侧重于Docker镜像的构建和推送。