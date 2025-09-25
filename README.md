# DockerImgAutoBuildAndPush

## 简介

DockerImgAutoBuildAndPush 是一个自动化构建和推送 Docker 镜像的 GitHub Actions 工作流。它支持两种不同的项目结构：

1. 单个Dockerfile位于项目根目录的项目（如li88iioo/Photonix）
2. 多个Dockerfile位于不同子目录的项目（如JefferyHcool/BiliNote）

## 功能特性

- 自动检出 Git 仓库
- 构建 Docker 镜像
- 推送镜像到 Docker Hub
- 支持单个和多个 Dockerfile 的构建
- 可重用的工作流设计
- 支持不同项目结构的灵活配置

## 使用方法

### 项目配置

系统通过在 `main.yml` 中为每个项目创建独立的 job 来支持不同结构的项目：

1. **单个Dockerfile项目**（如li88iioo/Photonix）- 使用默认配置
2. **多个Dockerfile项目**（如JefferyHcool/BiliNote）- 为每个Dockerfile创建独立的job

### 完整配置示例

在主工作流中为不同项目创建独立的构建任务：

```yaml
jobs:
  # 构建li88iioo/Photonix项目（单个Dockerfile在根目录）
  build-photonix:
    uses: ./.github/workflows/docker-build.yml
    with:
      source_repo: 'li88iioo/Photonix'
      docker_image_name: 'photonix'

  # 构建JefferyHcool/BiliNote后端（Dockerfile在backend目录）
  build-bili-note-backend:
    uses: ./.github/workflows/docker-build.yml
    with:
      source_repo: 'JefferyHcool/BiliNote'
      docker_image_name: 'bili-note-backend'
      dockerfile_path: 'backend/Dockerfile'
      context_path: '.'

  # 构建JefferyHcool/BiliNote前端（Dockerfile在BillNote_frontend目录）
  build-bili-note-frontend:
    uses: ./.github/workflows/docker-build.yml
    with:
      source_repo: 'JefferyHcool/BiliNote'
      docker_image_name: 'bili-note-frontend'
      dockerfile_path: 'BillNote_frontend/Dockerfile'
      context_path: '.'
```

### 可重用工作流参数说明

| 参数名 | 是否必需 | 默认值 | 说明 |
|--------|---------|--------|------|
| source_repo | 是 | 无 | 需要检出的 Git 仓库地址 |
| docker_image_name | 是 | 无 | 推送到 Docker Hub 的镜像名称 |
| dockerfile_path | 否 | "Dockerfile" | Dockerfile 路径 |
| context_path | 否 | "." | 构建上下文路径 |

### 添加新项目

要添加新项目，只需在 `main.yml` 中添加一个新的 job：

```yaml
  # 构建新项目
  build-new-project:
    uses: ./.github/workflows/docker-build.yml
    with:
      source_repo: 'username/repository'
      docker_image_name: 'image-name'
      # 如果Dockerfile不在根目录，指定路径
      dockerfile_path: 'path/to/Dockerfile'
      context_path: 'path/to/context'
```