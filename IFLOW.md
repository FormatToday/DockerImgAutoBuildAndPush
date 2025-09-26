# 项目概述

DockerImgAutoBuildAndPush 是一个用于自动化构建和推送 Docker 镜像的 GitHub Actions 工作流系统。它支持多种项目结构，包括单个 Dockerfile 项目和多个 Dockerfile 项目。

## 核心功能

- 自动检出 Git 仓库
- 构建 Docker 镜像
- 推送镜像到 Docker Hub
- 支持单个和多个 Dockerfile 的构建
- 可重用的工作流设计
- 支持不同项目结构的灵活配置

## 项目结构

```
DockerImgAutoBuildAndPush/
├── .github/
│   └── workflows/
│       ├── docker-build.yml  # 核心可重用工作流
│       └── main.yml          # 主工作流配置
├── README.md                 # 项目说明文档
├── CLAUDE.md                 # Claude AI 使用指南
└── IFLOW.md                  # iFlow CLI 上下文文件
```

## 核心工作流文件

### docker-build.yml

这是核心的可重用工作流，负责实际的 Docker 构建和推送操作。它支持以下特性：

- 灵活的 Dockerfile 路径配置
- 自定义构建上下文
- 使用 docker-compose 构建
- 自动标签生成（包括日期戳和 latest 标签）
- 多架构镜像支持（通过 QEMU 和 Buildx）

### main.yml

这是主工作流文件，定义了需要构建的仓库列表。每个仓库作为一个独立的 job 运行。

## 使用方法

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

### 构建参数说明

| 参数名 | 是否必需 | 默认值 | 说明 |
|--------|---------|--------|------|
| source_repo | 是 | 无 | 需要检出的 Git 仓库地址 |
| docker_image_name | 是 | 无 | 推送到 Docker Hub 的镜像名称 |
| dockerfile_path | 否 | "Dockerfile" | Dockerfile 路径 |
| context_path | 否 | "." | 构建上下文路径 |

## 开发与维护

### 测试更改

工作流的测试和构建通过 GitHub Actions 自动触发。要测试更改：
1. 修改工作流文件（例如：`.github/workflows/docker-build.yml` 或 `.github/workflows/main.yml`）。
2. 提交并推送更改到仓库。
3. 或者通过 GitHub Actions 界面手动触发工作流。

### 查看构建状态

1. 访问 GitHub 仓库的 "Actions" 标签页。
2. 选择相应的工作流运行，查看其状态和日志。