# 接收外部参数：源镜像地址
ARG SRC_IMG

FROM ${SRC_IMG}
#直接继承全部内容、环境、启动命令、端口、卷
