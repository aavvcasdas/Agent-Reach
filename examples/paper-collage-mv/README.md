# 纸片拼贴风 MV：用代码生成（不用视频生成模型）

参考截图（小红书账号「纸片情书」系列）的风格特征：

- **撕纸字卡**：每个字印在一张边缘不规则、带白色纤维边的彩色纸片上，纸片轻微歪斜并投影。
- **背景**：柔和渐变、光斑、纸纹颗粒，画面缓慢推拉。
- **角色**：手绘卡通人物做成抠图贴在纸上（本脚本支持导入透明 PNG 角色）。
- **动态**：纸片“啪”地落下、弹一下、定格；动作按 12fps 抖动，有手工定格动画的感觉。
- **转场**：沿一条抖动的“撕裂线”把上一场景撕开，露出下一场景。

## 实现思路

| 效果 | 做法 |
| --- | --- |
| 撕边 | 四条边各自随机锯齿的多边形遮罩；膨胀遮罩减原遮罩得到白色纤维边 |
| 纸纹 | 基色 + 高斯噪点颗粒 |
| 投影 | 遮罩高斯模糊 + 偏移 + 透明度 |
| 入场弹跳 | easeOutBack 缩放 + easeOutCubic 下落、旋转 |
| 定格感 | 运动量先量化到 12fps（`floor(t*12)/12`） |
| 撕裂转场 | 每行一个随机偏移的撕裂线；线处加白边、线左侧阴影 |
| 编码 | PIL/numpy 逐帧 → 管道 → ffmpeg（`imageio-ffmpeg` 自带二进制） |

## 运行

```bash
pip install pillow numpy imageio-ffmpeg
python make_mv.py --fetch-font                       # 首次：下载中文字体（Noto Sans SC，约 70MB，缓存到 ~/.cache/paper-mv）
python make_mv.py --out out/paper_mv.mp4             # 渲染内置 demo（约 13 秒）
python make_mv.py --stills out/stills                # 只导出关键帧，快速调样式
python make_mv.py --out out/mv.mp4 --bgm song.mp3    # 叠加配乐，结尾淡出
```

## 做你自己的 MV

1. 写一个分镜 JSON（格式参考脚本里的 `DEMO`），每个场景包含 `dur`（秒）、背景色 `top`/`bottom`、装饰纸 `decor`、字卡 `items`：

```json
[
  {"dur": 3.4, "top": "#F7C6B2", "bottom": "#E9A0A0",
   "items": [{"text": "我", "paper": "#F4A6A6", "rot": -3, "x": 0.3, "y": 0.4, "size": 330},
             {"image": "girl.png", "rot": 0, "x": 0.5, "y": 0.75, "size": 700}]}
]
```

2. 角色用透明底 PNG（可以用 AI 抠图或自己画），放在分镜文件同目录，用 `image` 字段引用。
3. `python make_mv.py --script my_mv.json --out out/my_mv.mp4 --bgm song.mp3`

时间轴：场景按 `dur` 顺序排列，相邻场景重叠 0.9 秒做撕裂转场；每个字卡按 0.12 秒错开入场。

## 想更接近原视频还可以加

- 角色做口型/眨眼：把角色拆成几张 PNG（嘴、眼）按节拍切换。
- 歌词字幕与音乐节拍对齐：用 `librosa` 检测 BPM，把入场时间对齐到节拍。
- 纸张真实纹理：替换 `paper_sprite` 里的噪点为扫描的纸张图片。
