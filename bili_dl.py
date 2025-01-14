import asyncio
import aiohttp
import sys
import subprocess
from pathlib import Path
from bilibili_api import video, Credential
from tqdm import tqdm

class BiliDownloader:
    def __init__(self):
        self.download_path = Path.home() / "Downloads" / "bili-downloads"
        self.download_path.mkdir(parents=True, exist_ok=True)
        
    async def download_file(self, url: str, filepath: Path, desc: str):
        """下载文件并显示进度条"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                total_size = int(resp.headers.get('content-length', 0))
                with open(filepath, 'wb') as f, tqdm(
                    desc=desc,
                    total=total_size,
                    unit='iB',
                    unit_scale=True
                ) as pbar:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))

    async def merge_video_audio(self, video_path: Path, audio_path: Path, output_path: Path):
        """合并视频和音频"""
        try:
            print("正在合并音视频...")
            
            # 使用 ffmpeg 命令行方式合并，添加格式指定
            cmd = [
                'ffmpeg',
                '-i', str(video_path),  # 视频输入
                '-i', str(audio_path),  # 音频输入
                '-c:v', 'copy',  # 视频直接复制
                '-c:a', 'aac',  # 音频使用 AAC 编码
                '-strict', 'experimental',  # 允许实验性编码器
                str(output_path),  # 输出文件
                '-y'  # 覆盖已存在的文件
            ]
            
            # 执行命令
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'  # 指定编码
            )
            
            if process.returncode != 0:
                print("FFmpeg 错误输出:", process.stderr)
                raise Exception("合并失败")
            
            # 删除原始文件
            video_path.unlink()
            audio_path.unlink()
            
            print(f"合并完成！文件保存在: {output_path}")
        except Exception as e:
            print(f"合并失败: {str(e)}")
            if hasattr(e, 'stderr'):
                print("详细错误:", e.stderr)
            raise

    async def download_video(self, bvid: str):
        """下载视频"""
        try:
            # 创建视频对象
            v = video.Video(bvid=bvid)
            
            # 获取视频信息
            info = await v.get_info()
            title = info['title']
            print(f"正在下载: {title}")
            
            # 获取视频下载地址
            download_url = await v.get_download_url(0)
            video_url = download_url['dash']['video'][0]['baseUrl']
            audio_url = download_url['dash']['audio'][0]['baseUrl']
            
            # 准备下载路径
            safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_')).rstrip()
            video_path = self.download_path / f"{safe_title}_video.mp4"  # 直接使用 .mp4 扩展名
            audio_path = self.download_path / f"{safe_title}_audio.m4a"  # 使用 .m4a 扩展名
            output_path = self.download_path / f"{safe_title}.mp4"
            
            # 下载视频和音频
            print("下载视频流...")
            await self.download_file(video_url, video_path, "视频")
            
            print("下载音频流...")
            await self.download_file(audio_url, audio_path, "音频")
            
            # 合并音视频
            await self.merge_video_audio(video_path, audio_path, output_path)
            
        except Exception as e:
            print(f"下载失败: {str(e)}", file=sys.stderr)
            sys.exit(1)

def extract_bvid_from_url(url: str) -> str:
    """从B站URL中提取BV号"""
    if '/video/BV' not in url:
        raise ValueError("无效的B站视频URL")
    bvid = url.split('/video/')[1].split('/')[0].split('?')[0]
    if not bvid.startswith('BV'):
        raise ValueError("无效的B站视频URL")
    return bvid

async def main():
    if len(sys.argv) != 2:
        print("使用方法: python bili_dl.py 视频URL")
        print("示例: python bili_dl.py https://www.bilibili.com/video/BV1xx411c7mD")
        sys.exit(1)
        
    url = sys.argv[1]
    try:
        bvid = extract_bvid_from_url(url)
        downloader = BiliDownloader()
        await downloader.download_video(bvid)
    except ValueError as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"下载失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 