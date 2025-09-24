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
- 可复用的工作流设计
- 支持不同项目结构的灵活配置

## 使用方法

### 单个 Dockerfile 项目（根目录）

对于Dockerfile位于项目根目录的项目（如li88iioo/Photonix），使用默认配置：

```yaml
jobs:
  call-reusable-workflow:
    uses: ./.github/workflows/docker-build-reusable.yml
    with:
      source_repo: 'li88iioo/Photonix'
      docker_image_name: 'photonix'
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 多个 Dockerfile 项目（不同目录）

对于具有多个Dockerfile且位于不同目录的项目（如JefferyHcool/BiliNote），需要为每个Dockerfile创建单独的构建任务：

```yaml
jobs:
  call-reusable-workflow:
    strategy:
      fail-fast: false
      matrix:
        include:
          # 构建后端Dockerfile
          - repo: 'JefferyHcool/BiliNote'
            image_name: 'bili-note-backend'
            multi_dockerfiles: |
              [
                {"path": "backend/Dockerfile", "context": "backend"}
              ]
          # 构建前端Dockerfile
          - repo: 'JefferyHcool/BiliNote'
            image_name: 'bili-note-frontend'
            multi_dockerfiles: |
              [
                {"path": "BillNote_frontend/Dockerfile", "context": "BillNote_frontend"}
              ]
    uses: ./.github/workflows/docker-build-reusable.yml
    with:
      source_repo: ${{ matrix.repo }}
      docker_image_name: ${{ matrix.image_name }}
      multi_dockerfiles: ${{ matrix.multi_dockerfiles }}
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 参数说明

| 参数名 | 是否必需 | 默认值 | 说明 |
|--------|---------|--------|------|
| source_repo | 是 | 无 | 需要检出的 Git 仓库地址 |
| docker_image_name | 是 | 无 | 推送到 Docker Hub 的镜像名称 |
| dockerfile_path | 否 | "Dockerfile" | Dockerfile 路径 |
| context_path | 否 | "." | 构建上下文路径 |
| build_args | 否 | "{}" | 额外的 Docker 构建参数（JSON 格式） |
| multi_dockerfiles | 否 | "[]" | 是否构建多个 Dockerfile（JSON 数组格式） |

### 完整配置示例

在主工作流中使用矩阵策略构建多个仓库：

```yaml
jobs:
  call-reusable-workflow:
    strategy:
      fail-fast: false
      matrix:
        include:
          # 单个Dockerfile项目
          - repo: 'li88iioo/Photonix'
            image_name: 'photonix'
          # 多个Dockerfile项目 - 后端
          - repo: 'JefferyHcool/BiliNote'
            image_name: 'bili-note-backend'
            multi_dockerfiles: |
              [
                {"path": "backend/Dockerfile", "context": "backend"}
              ]
          # 多个Dockerfile项目 - 前端
          - repo: 'JefferyHcool/BiliNote'
            image_name: 'bili-note-frontend'
            multi_dockerfiles: |
              [
                {"path": "BillNote_frontend/Dockerfile", "context": "BillNote_frontend"}
              ]
    uses: ./.github/workflows/docker-build-reusable.yml
    with:
      source_repo: ${{ matrix.repo }}
      docker_image_name: ${{ matrix.image_name }}
      multi_dockerfiles: ${{ matrix.multi_dockerfiles || '[]' }}
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```