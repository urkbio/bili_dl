# B站视频下载工具

这是一个简单的命令行工具，用于下载B站视频。该工具会分别下载视频和音频流。

## 功能特点

- 支持通过BV号下载B站视频
- 显示下载进度条
- 分别下载视频流和音频流
- 自动保存到用户的Downloads目录下

## 安装要求

请确保您的系统已安装 Python 3.7+，然后安装所需依赖：

- 需要安装 FFmpeg（用于合并音视频）
  - Windows: 可以从 https://ffmpeg.org/download.html 下载
  - Linux: sudo apt install ffmpeg
  - macOS: brew install ffmpeg

## 使用方法

1. 运行程序后,将B站视频链接粘贴到命令行中
   例如: https://www.bilibili.com/video/BV1xx411c7mD
