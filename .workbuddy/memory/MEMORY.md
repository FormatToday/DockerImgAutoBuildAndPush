# 项目长期约定（docker-build-and-mirror，原 DockerImgAutoBuildAndPush）

- 只保留两条核心流水线：`构建并推送`（schedule.yml + build.yml）与 `镜像迁移`（schedule.yml + migrate.yml）。新增能力前先判断是否属于这两件事，否则不加。
- `schedule.yml` 只做触发与串联，固定三步：构建 / 迁移 / 清理；清单解析与矩阵展开下沉到各自流水线内部。
- 所有可配置项集中在 `config/build-list.json` 与 `config/migrate-list.json`；新增项目/镜像只改 JSON，不改工作流。
- 构建路径：checkout 源码到 `src/`，`context = ./src/<context_path>`，`file = ./src/<dockerfile_path>`。不再引入 docker-compose 构建路径。
- 迁移必须用 `skopeo copy --all`（保留多架构与 digest），不用 `FROM` 重打标签，也不用 `docker pull/tag/push`。
- 两条流水线都同时推 Docker Hub 与 GHCR；产出标签固定 `latest` + 当天 UTC 日期（`YYYY.MM.DD`）。
- 权限：`contents: read` + `packages: write`。可复用工作流权限只能降级，调用方也必须声明 `packages: write`。
- **凡是会出现在摘要里的值都不能作为 secret 传入 job**：GitHub 按值全文脱敏，否则镜像地址会被替换成 `***`。命名空间固定写死为 `env: HUB_OWNER` / `GHCR_OWNER`。
- Secrets 仅需 `DOCKERHUB_TOKEN` / `CLEANUP_TOKEN`（`DOCKERHUB_USERNAME` 已弃用，可删除）。
- 清单为空时在解析阶段直接失败；摘要全中文，并按标签给出两个 registry 的直达链接。
