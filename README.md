# Emby DG1 镜像

基于 Arch Linux，面向 Intel DG1 宿主机上的 `linux/amd64` Docker。镜像使用 Emby 官方安装包及 Arch 的 Intel 用户态驱动，支持现有 `/config` 和 `/dev/dri` 挂载方式。

GitHub Actions 构建并发布 `ghcr.io/kiliter/emby-dg1:4.10.2.0` 和 `ghcr.io/kiliter/emby-dg1:latest`。

构建方式参考 [Linvery/emby_intelgpu](https://github.com/Linvery/emby_intelgpu)，原代码的 MIT 许可证见 [LICENSE](LICENSE)。
