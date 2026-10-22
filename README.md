# docker-build-and-mirror

[![定时任务](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/schedule.yml/badge.svg)](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/schedule.yml)  [![构建镜像](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/build.yml/badge.svg)](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/build.yml)  [![迁移镜像](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/migrate.yml/badge.svg)](https://github.com/FormatToday/docker-build-and-mirror/actions/workflows/migrate.yml)


仓库名就是它的两件事：**build**（拉源码构建镜像）和 **mirror**（搬运第三方 registry 的已有镜像）。两者各用一条独立流水线，产物同时落地 **Docker Hub 与 GHCR（ghcr.io）**，配置全部集中在 `config/` 下的两个 JSON 里。

## 目录结构

```
.
├── .github/workflows/
│   ├── schedule.yml         # 定时入口，只有三步：构建 → 迁移 → 清理
│   ├── build.yml            # 读 build-list.json 展开矩阵 → 检出源码 → 构建 → 推 DH + GHCR
│   └── migrate.yml          # 读 migrate-list.json 展开矩阵 → skopeo 复制到 DH + GHCR
├── config/
│   ├── build-list.json      # 需要构建的项目清单
│   └── migrate-list.json    # 需要迁移的镜像清单
└── README.md
```

`schedule.yml` 只负责触发与串联，清单解析和矩阵展开都在各自的流水线内部完成，所以 Actions 里每次运行只呈现三个步骤：

```
构建镜像 ──┐
迁移镜像 ──┴─→ 清理历史运行记录
```

| 文件 | 类型 | 触发方式 |
|------|------|----------|
| `schedule.yml` | 定时入口 | 每天 12:00（北京时间）、手动、清单/工作流变更时；**同时驱动构建与迁移** |
| `build.yml` | 流水线 | 由 `schedule.yml` 调用；也可手动运行 |
| `migrate.yml` | 流水线 | 由 `schedule.yml` 调用；也可手动运行，或 `migrate-list.json` 变更时单独触发 |

## 前置准备

在仓库 `Settings → Secrets and variables → Actions` 中添加：

| Secret | 说明 |
|--------|------|
| `DOCKERHUB_TOKEN` | Docker Hub Access Token（需 Read & Write 权限） |
| `CLEANUP_TOKEN` | 个人访问令牌，仅用于清理旧运行记录（需 `workflow` 权限） |

Docker Hub **用户名不再作为 secret**（见下文命名空间说明），原来的 `DOCKERHUB_USERNAME` 可以删除。GHCR 使用 GitHub 内置的 `GITHUB_TOKEN`，也无需额外 secret，但需要满足两个前提：

1. 工作流已声明 `packages: write` 权限（本仓库已内置）；
2. 仓库 `Settings → Actions → General → Workflow permissions` 允许读写，组织若禁用了包写入，需要改用具备 `write:packages` 的 PAT。

两个 registry 的目标仓库不存在时都会被自动创建，无需提前建库。GHCR 首次推送后包默认为 **私有**，如需公开在包包页面的 Danger Zone 里改。

镜像命名空间在两个工作流顶部固定写死为 `formattoday`（`env: HUB_OWNER` / `env: GHCR_OWNER`），登录 Docker Hub 也用它：

```yaml
env:
  HUB_OWNER: formattoday
  GHCR_OWNER: formattoday
```

### 为什么用户名不能放在 secret 里

GitHub 的日志脱敏是**按值全文替换**的：它把「当前 job 里用到的 secret 值」当作待脱敏字符串，在日志和 Job Summary 里做全局替换。所以只要 job 里还引用了值等于 `formattoday` 的 secret，**任何位置**出现 `formattoday` 都会被换成 `***`——哪怕这个字符串是你写死的常量，甚至只是镜像名 `formattoday/reader` 里的一段。

因此这里把用户名写成常量、只把 `DOCKERHUB_TOKEN` 作为 secret 传入。换命名空间时：

1. 改这两行常量；
2. 确保仓库里没有值相同的 secret（否则仍会被脱敏），最稳的做法是删掉 `DOCKERHUB_USERNAME`。

---

## 功能一：从指定仓库构建并推送

构建产物会用同一批标签同时推送到 `Docker Hub` 与 `ghcr.io`。

### 配置 `config/build-list.json`

数组，每个元素对应一个镜像：

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `source_repo` | 是 | — | 源码仓库，`owner/repo` |
| `docker_image_name` | 是 | — | 镜像名（不含用户名），Docker Hub 与 GHCR 共用 |
| `branch` | 否 | 源码仓库默认分支 | 从哪个分支构建；也可填 tag 或 commit |
| `dockerfile_path` | 否 | `Dockerfile` | Dockerfile 路径，相对仓库根目录 |
| `context_path` | 否 | `.` | 构建上下文，相对仓库根目录 |
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
    "branch": "dev",
    "dockerfile_path": "backend/Dockerfile",
    "context_path": "backend",
    "platforms": "linux/amd64,linux/arm64",
    "additional_tags": "type=raw,value=dev"
  }
]
```

`branch` 省略时检出源码仓库的默认分支；填了分支就检出该分支的最新提交，填 tag / commit 则检出对应的固定版本。旧配置里的 `source_ref` 仍然可用，两者同时存在时以 `branch` 为准。

### 产出标签

每次构建固定推送两个标签：`latest` 与当天日期（如 `2026.10.21`），同一批标签会**同时打到两个仓库**：

```
formattoday/<镜像名>:latest
formattoday/<镜像名>:2026.10.21
ghcr.io/formattoday/<镜像名>:latest
ghcr.io/formattoday/<镜像名>:2026.10.21
```

同一天重复构建会覆盖当天标签。

### 新增项目

往 `config/build-list.json` 里追加一条，提交后流水线自动按新清单执行，无需改工作流文件。

### 手动触发

Actions 页面选择「构建镜像」只跑构建，选择「定时任务」则构建 + 迁移 + 清理一起跑。

---

## 功能二：迁移第三方镜像

用于把 GHCR、Quay、cnb.cool 等 registry 的已有镜像搬到 Docker Hub 与 GHCR，不构建、不重打层。

### 原理

用 `skopeo copy` 在 registry 之间直连复制，全程不落本地磁盘：

- 镜像内容**逐字节不变**，digest 与原镜像一致，并打印源、Docker Hub、GHCR 三处 digest 供核对；
- 使用 `--all` 复制，多架构镜像的 manifest list **原样保留**，不会退化成单架构；
- 不依赖 Dockerfile，也不需要 `docker pull` / `docker push`；
- 复制链路为「源 → Docker Hub → GHCR」，其余标签都在各自仓库内复制，registry 侧复用已有 blob，几乎不产生额外流量。

为什么不直接用 `docker pull` + `docker tag` + `docker push`：那样只会拉取 runner 当前架构（linux/amd64）的镜像，多架构镜像会退化成单架构，digest 也会变。

### 配置 `config/migrate-list.json`

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `source_img` | 是 | — | 源镜像地址，**不含 tag** |
| `hub_name` | 是 | — | 镜像名（不含用户名），Docker Hub 与 GHCR 共用 |
| `tag` | 是 | — | 源镜像的 tag |

```json
[
  {
    "source_img": "docker.cnb.cool/hectorqin/reader",
    "hub_name": "reader",
    "tag": "main"
  },
  {
    "source_img": "ghcr.io/metacubex/metacubexd",
    "hub_name": "metacubexd",
    "tag": "latest"
  }
]
```

### 产出标签

与构建完全一致：每次迁移固定推送 `latest` 与当天日期（如 `2026.10.21`），同一批标签**同时打到两个仓库**：

```
formattoday/<镜像名>:latest
formattoday/<镜像名>:2026.10.21
ghcr.io/formattoday/<镜像名>:latest
ghcr.io/formattoday/<镜像名>:2026.10.21
```

源镜像的 tag 只用于**定位源**（`source_img:tag`），不会带到目标仓库。同一天重复迁移会覆盖当天标签。

### 新增迁移镜像

往 `config/migrate-list.json` 追加一条即可。单个镜像失败不影响其他镜像（`fail-fast: false`）。

### 手动触发

Actions 页面选择「迁移镜像」→ Run workflow。

> 源镜像需可匿名拉取。若源 registry 需要认证，在 `migrate.yml` 的「复制镜像」步骤前追加一个 `docker/login-action` 指向该 registry，并补充对应 secret。

---

## 行为约定

- **清单为空即失败**：两条流水线各自在解析阶段校验数组长度，空清单会直接报错退出，避免“跑绿但什么都没做”。
- **权限最小化**：工作流只申请 `contents: read` 与 `packages: write`（推送 GHCR 所需），不涉及任何写仓库内容的权限。
- **并发安全**：矩阵内各任务互不影响；同一工作流重复触发时，两个 registry 都以最后一次推送为准。
- **构建缓存**：构建走 GitHub Actions 缓存（`type=gha`），同镜像的重复构建会复用层缓存。
- **运行摘要**：构建与迁移都会用中文写 Actions 运行摘要，逐个标签给出 Docker Hub 与 GHCR 的直达链接（日期标签可直接跳转，不会停在 `latest`），并附拉取命令。`docker/build-push-action` 自带的英文摘要已用 `DOCKER_BUILD_SUMMARY: false` 关闭，摘要里只会有一份中文内容。
