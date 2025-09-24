# DockerImgAutoBuildAndPush

## 简介

DockerImgAutoBuildAndPush 是一个自动化构建和推送 Docker 镜像的 GitHub Actions 工作流。

## 功能特性

- 自动检出 Git 仓库
- 构建 Docker 镜像
- 推送镜像到 Docker Hub
- 支持单个和多个 Dockerfile 的构建
- 可复用的工作流设计

## 使用方法

### 单个 Dockerfile 构建

在你的工作流中调用可复用工作流：

```yaml
jobs:
  call-reusable-workflow:
    uses: ./.github/workflows/docker-build-reusable.yml
    with:
      source_repo: 'username/repository'
      docker_image_name: 'image-name'
      # 可选参数
      dockerfile_path: 'Dockerfile'  # 默认为项目根目录的 Dockerfile
      context_path: '.'              # 默认为项目根目录
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 多个 Dockerfile 构建

如果需要构建多个 Dockerfile，可以使用 `multi_dockerfiles` 参数：

```yaml
jobs:
  call-reusable-workflow:
    uses: ./.github/workflows/docker-build-reusable.yml
    with:
      source_repo: 'username/repository'
      docker_image_name: 'image-name'
      multi_dockerfiles: |
        [
          {"path": "backend/Dockerfile", "context": "backend"},
          {"path": "frontend/Dockerfile", "context": "frontend"}
        ]
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

### 构建多个仓库示例

在主工作流中使用矩阵策略构建多个仓库：

```yaml
jobs:
  call-reusable-workflow:
    strategy:
      fail-fast: false
      matrix:
        include:
          - repo: 'li88iioo/Photonix'
            image_name: 'photonix'
          - repo: 'JefferyHcool/BiliNote'
            image_name: 'bili-note'
            multi_dockerfiles: |
              [
                {"path": "backend/Dockerfile", "context": "backend"},
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