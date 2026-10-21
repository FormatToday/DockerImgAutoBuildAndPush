# DockerImgAutoBuildAndPush

[![定时任务](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/schedule.yml/badge.svg)](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/schedule.yml)

[![构建镜像](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/build.yml/badge.svg)](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/build.yml)

[![迁移镜像](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/migrate.yml/badge.svg)](https://github.com/FormatToday/DockerImgAutoBuildAndPush/actions/workflows/migrate.yml)


把「拉源码构建镜像并推送 Docker Hub」和「搬运第三方 registry 的已有镜像」这两件事，各用一条独立流水线做好，配置全部集中在 `config/` 下的两个 JSON 里。

## 目录结构

```
.
├── .github/workflows/
│   ├── build.yml            # 可复用工作流：检出仓库 → 构建 → 推送 Docker Hub
│   ├── schedule.yml         # 入口：读 build-list.json，按矩阵调 build.yml，并清理旧运行记录
│   └── migrate.yml          # 入口：读 migrate-list.json，按矩阵复制镜像
├── config/
│   ├── build-list.json      # 需要构建的项目清单
│   └── migrate-list.json    # 需要迁移的镜像清单
└── README.md
```

| 文件 | 类型 | 触发方式 |
|------|------|----------|
| `schedule.yml` | 入口工作流 | 每天 12:00（北京时间）、手动、清单变更时 |
| `migrate.yml` | 入口工作流 | 每天 11:00（北京时间）、手动、清单变更时 |
| `build.yml` | 可复用工作流 | 仅由 `schedule.yml` 调用，不单独触发 |

## 前置准备

在仓库 `Settings → Secrets and variables → Actions` 中添加：

| Secret | 说明 |
|--------|------|
| `DOCKERHUB_USERNAME` | Docker Hub 用户名，同时作为镜像命名空间 |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token（需 Read & Write 权限） |
| `CLEANUP_TOKEN` | 个人访问令牌，仅用于清理旧运行记录（需 `workflow` 权限） |

目标仓库不存在时会被自动创建，无需提前在 Docker Hub 建库。

---

## 功能一：从指定仓库构建并推送

### 配置 `config/build-list.json`

数组，每个元素对应一个镜像：

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `source_repo` | 是 | — | 源码仓库，`owner/repo` |
| `docker_image_name` | 是 | — | 推送后的镜像名（不含用户名） |
| `dockerfile_path` | 否 | `Dockerfile` | Dockerfile 路径，相对仓库根目录 |
| `context_path` | 否 | `.` | 构建上下文，相对仓库根目录 |
| `source_ref` | 否 | 默认分支 | 分支 / tag / commit |
| `platforms` | 否 | `linux/amd64` | 目标平台，逗号分隔 |
| `additional_tags` | 否 | 空 | 额外标签，每行一个，遵循 metadata-action 语法 |

```json
[
  {
    "source_repo": "kurisu-agi/AssppWeb",
    "docker_image_name": "assppweb"
  },
  {
    "source_repo": "JefferyHcool/BiliNote",
    "docker_image_name": "bili-note",
    "dockerfile_path": "backend/Dockerfile",
    "context_path": "backend",
    "platforms": "linux/amd64,linux/arm64",
    "additional_tags": "type=raw,value=dev"
  }
]
```

### 产出标签

每次构建固定推送两个标签：`latest` 与当天日期（如 `2026.10.21`）。同一天重复构建会覆盖当天标签。

### 新增项目

往 `config/build-list.json` 里追加一条，提交后流水线自动按新清单执行，无需改工作流文件。

### 手动触发

Actions 页面选择「定时任务」→ Run workflow。

---

## 功能二：迁移第三方镜像

用于把 GHCR、Quay、cnb.cool 等 registry 的已有镜像搬到 Docker Hub，不构建、不重打层。

### 原理

用 `skopeo copy` 在 registry 之间直连复制，全程不落本地磁盘：

- 镜像内容**逐字节不变**，digest 与原镜像一致，并打印源/目标 digest 供核对；
- 使用 `--all` 复制，多架构镜像的 manifest list **原样保留**，不会退化成单架构；
- 不依赖 Dockerfile，也不需要 `docker pull` / `docker push`；
- 同一镜像的多个目标标签，除第一个外都从已复制好的仓库再复制，registry 侧复用已有 blob，几乎不产生额外流量。

为什么不直接用 `docker pull` + `docker tag` + `docker push`：那样只会拉取 runner 当前架构（linux/amd64）的镜像，多架构镜像会退化成单架构，digest 也会变。

### 配置 `config/migrate-list.json`

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `source_img` | 是 | — | 源镜像地址，**不含 tag** |
| `hub_name` | 是 | — | 推送后的镜像名（不含用户名） |
| `tag` | 是 | — | 源镜像的 tag |
| `target_tags` | 否 | `[tag]` | 目标标签数组，可一次推多个 |

```json
[
  {
    "source_img": "cnb.cool/hectorqin/reader",
    "hub_name": "reader",
    "tag": "latest"
  },
  {
    "source_img": "ghcr.io/metacubex/metacubexd",
    "hub_name": "metacubexd",
    "tag": "latest",
    "target_tags": ["latest", "2026.10.21"]
  }
]
```

### 新增迁移镜像

往 `config/migrate-list.json` 追加一条即可。单个镜像失败不影响其他镜像（`fail-fast: false`）。

### 手动触发

Actions 页面选择「迁移镜像」→ Run workflow。

> 源镜像需可匿名拉取。若源 registry 需要认证，在 `migrate.yml` 的「复制镜像」步骤前追加一个 `docker/login-action` 指向该 registry，并补充对应 secret。

---

## 行为约定

- **清单为空即失败**：两个入口都会在解析阶段校验数组长度，空清单会直接报错退出，避免“跑绿但什么都没做”。
- **只读权限**：所有工作流仅申请 `contents: read`，不使用任何写仓库的权限。
- **并发安全**：矩阵内各任务互不影响；同一工作流重复触发时，Docker Hub 侧以最后一次推送为准。
- **构建缓存**：构建走 GitHub Actions 缓存（`type=gha`），同镜像的重复构建会复用层缓存。
- **摘要输出**：构建与迁移的最终标签都会写入 Actions 运行摘要，便于回查。
