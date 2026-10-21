# 项目长期约定（DockerImgAutoBuildAndPush）

- 只保留两条核心流水线：`构建并推送`（main.yml + build.yml）与 `镜像迁移`（migrate.yml）。新增能力前先判断是否属于这两件事，否则不加。
- 所有可配置项集中在 `config/build-list.json` 与 `config/migrate-list.json`；新增项目/镜像只改 JSON，不改工作流。
- 构建路径：checkout 源码到 `src/`，`context = ./src/<context_path>`，`file = ./src/<dockerfile_path>`。不再引入 docker-compose 构建路径。
- 迁移必须用 `skopeo copy --all`（保留多架构与 digest），不用 `FROM` 重打标签，也不用 `docker pull/tag/push`。
- 工作流只申请 `contents: read`；清单为空时在解析阶段直接失败。
- Secrets 仅需 `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`。
