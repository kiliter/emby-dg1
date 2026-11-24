FROM archlinux:latest AS runtime

ARG EMBY_V=4.10.2.0
ARG EMBY_SHA256=80da662b58b7fd058f80fa3e21b3c4e0ec6ccfb1a5cab9e8aaca718907e44ba3
ARG S6_VERSION=v2.2.0.3
ARG S6_SHA256=7140eafc62720ecc43f81292c9bdd75bc7f4d0421518d42707e69f8e78e55088

LABEL org.opencontainers.image.source="https://github.com/kiliter/emby-dg1" \
      org.opencontainers.image.version="$EMBY_V"

ENV TZ=Asia/Shanghai \
    UID=2 \
    GID=2 \
    GIDLIST=2 \
    PROGRAM_DATA=/config \
    FFDETECT=/usr/bin/ffdetect-emby \
    FFMPEG=/usr/local/bin/emby-ffmpeg \
    FFPROBE=/usr/bin/ffprobe \
    LIBVA_DRIVERS_PATH=/usr/lib/dri \
    LIBVA_DRIVER_NAME=iHD

# 关键：用 Arch 的系统驱动提供 VAAPI、QSV 和 OpenCL。
# vpl-gpu-rt 是 onevpl-intel-gpu 在 Arch 的当前包名。
RUN pacman -Syu --needed --noconfirm \
        aspnet-runtime-8.0 ca-certificates clinfo curl dash dotnet-runtime-8.0 \
        emby-ffmpeg ffmpeg intel-compute-runtime intel-media-driver intel-media-sdk \
        libdrm libmfx libva libva-utils libvips libvpl ocl-icd skia-sharp2 sqlite \
        ttf-dejavu unzip vpl-gpu-rt \
    && pacman -Scc --noconfirm \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 构建依赖只进入编译阶段。成品保留原版 Arch 的 QSV、VAAPI 和 OpenCL。
FROM runtime AS ffmpeg-build
RUN pacman -S --needed --noconfirm base-devel amf-headers avisynthplus clang \
        ffnvcodec-headers frei0r-plugins git ladspa mesa nasm opencl-headers spirv-headers vulkan-headers
WORKDIR /tmp/ffmpeg-build
COPY ffmpeg/ ./
RUN bash build-libavformat

FROM runtime
COPY --from=ffmpeg-build /patched/ /
RUN --mount=type=bind,source=ffmpeg/check-seek,target=/tmp/check-seek bash /tmp/check-seek

# 用同一套 Arch 运行库启动官方 Emby。保留系统 FFmpeg 的 VAAPI、QSV 和 OpenCL 支持。
RUN curl -fSL --retry 4 --retry-all-errors \
        "https://github.com/MediaBrowser/Emby.Releases/releases/download/${EMBY_V}/embyserver-netcore_${EMBY_V}.zip" \
        -o /tmp/emby.zip \
    && printf '%s  %s\n' "$EMBY_SHA256" /tmp/emby.zip | sha256sum -c - \
    && unzip -q /tmp/emby.zip 'system/*' -d / \
    && rm /tmp/emby.zip \
    && test -f /system/EmbyServer.dll \
    && test -x "$FFDETECT" \
    && test -r "$LIBVA_DRIVERS_PATH/iHD_drv_video.so"

# 延用 Linvery 的 s6 服务入口，同时校验安装文件。
RUN curl -fSL --retry 4 --retry-all-errors \
        "https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64-installer" \
        -o /tmp/s6-installer \
    && printf '%s  %s\n' "$S6_SHA256" /tmp/s6-installer | sha256sum -c - \
    && chmod 0755 /tmp/s6-installer \
    && /tmp/s6-installer / \
    && rm /tmp/s6-installer \
    && test -x /init

# Emby 调用包装脚本，DG1 的 HDR QSV 任务先创建 VAAPI 父设备。
COPY --chmod=0755 emby-ffmpeg /usr/local/bin/emby-ffmpeg
COPY --chmod=0755 run finish /etc/services.d/emby-server-s6/

WORKDIR /config
EXPOSE 8096 8920
ENTRYPOINT ["/init"]
