# DockerImgAutoBuildAndPush

[![构建状态](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/main.yml/badge.svg)](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/main.yml)

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
- **第三方镜像批量迁移**：通过配置文件批量将 GHCR/Quay 等 registry 的镜像迁移到 Docker Hub

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
    uses: ./.github/workflows/docker-build-new.yml
    with:
      source_repo: 'li88iioo/Photonix'
      docker_image_name: 'photonix'

  # 构建JefferyHcool/BiliNote后端（Dockerfile在backend目录）
  build-bili-note-backend:
    uses: ./.github/workflows/docker-build-new.yml
    with:
      source_repo: 'JefferyHcool/BiliNote'
      docker_image_name: 'bili-note-backend'
      dockerfile_path: 'backend/Dockerfile'
      context_path: '.'

  # 构建JefferyHcool/BiliNote前端（Dockerfile在BillNote_frontend目录）
  build-bili-note-frontend:
    uses: ./.github/workflows/docker-build-new.yml
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

## 镜像迁移流程

用于将第三方 registry（如 GHCR、Quay.io）的已有镜像批量迁移到 Docker Hub，无需源码构建。

### 工作原理

1. **`migrate-list.json`**：迁移清单，定义所有需要迁移的源镜像与目标镜像名
2. **`dockerfiles/migrate-template.Dockerfile`**：模板 Dockerfile，通过 `ARG SRC_IMG` 动态接收源镜像地址，以 `FROM ${SRC_IMG}` 的方式直接重新打标签
3. **`.github/workflows/migrate.yml`**：工作流读取 JSON 清单，通过 matrix 策略为每个镜像并行执行迁移任务

### migrate-list.json 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `source_img` | 源镜像地址（不含 tag） | `ghcr.io/metacubex/metacubexd-server` |
| `hub_name` | 推送到 Docker Hub 的仓库名 | `metacubexd-server` |
| `tag` | 源镜像的 tag | `latest` |

示例：

```json
[
  {
    "source_img": "ghcr.io/metacubex/metacubexd-server",
    "hub_name": "metacubexd-server",
    "tag": "latest"
  }
]
```

### 添加迁移镜像

直接编辑 `migrate-list.json`，在数组中追加一条记录即可，无需修改工作流文件。

### 触发方式

- **手动触发**：GitHub Actions 页面选择「迁移第三方镜像到DockerHub」工作流 → Run workflow
- **定时触发**：每天 UTC 5:00（北京时间 13:00）自动执行一次