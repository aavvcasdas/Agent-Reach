# Day10 售后部渲染器

## 文件
- `render_day10.mjs`：Day10 分镜/有声渲染入口。
- `repair_props.mjs`：修坏墙、委托单、发送键封印、摘要电视。

## 依赖
沿用仓库现有依赖：
- `@napi-rs/canvas`（Day8 渲染器会尝试 `/tmp/node_render/node_modules` 回退）。
- `video-fx/` 引擎与字体。
- Day3 立绘骨架、Day8 共享道具、Day2 字幕。
- 有声整片需要 ffmpeg；无声 `--test/--stills` 不需要 ffmpeg。

## 命令
```bash
node tools/day10制作/render_day10.mjs --test
node tools/day10制作/render_day10.mjs --stills
```
有声：
```bash
node tools/day10制作/render_day10.mjs \
  --voice <用户指定WAV> \
  --alignment <measured_alignment.json> \
  --subtitle-file <subtitles.json> \
  --out Day10/成片/Day10_售后部开张_配音对齐版.mp4
```

## 红线
- 估时只用于无声分镜；有声必须 measured=true、SHA256 对齐、字幕文件。
- 画面不出现运营数据、片尾卡。
- 笨鱼只修不发；发送键封印是剧情道具，不代表真实权限变更。
- 不覆盖 Day0–Day9 已发布成片。
