# 横向收藏夹 · 仿 360 书签面板

一个轻量（零依赖、原生 MV3）的浏览器扩展：点击工具栏图标，在**独立可缩放窗口**中展开多列的横向书签面板，使用体验接近 360 浏览器的收藏夹。

> 采用 Manifest V3，**同时支持 Microsoft Edge 与 Google Chrome**（同一份代码，提供两种发行包）。

## 功能特性

- 点击图标 → 弹出独立窗口（非 popup，因此**不受约 800×600 弹窗尺寸上限限制**，可自由拖拽边缘缩放、可最大化）
- 左侧文件夹导航 + 右侧书签网格的**双栏布局**（仿 360），点击文件夹原地切换，永远只有一列导航 + 一列书签
- 设置可持久化（列宽 / 行高 / 列数 / 字号），窗口尺寸与**最大化状态**也会记住，下次打开保持一致
- 点击书签在新标签页打开，并自动收起/关闭面板窗口
- 顶部支持书签**搜索**
- 零依赖、纯原生 JS，占用资源极小

## 安装（加载已解压缩的扩展）

两种发行包（`dist/horizontal-bookmarks-chrome-vX.Y.Z.zip` 与 `dist/horizontal-bookmarks-edge-vX.Y.Z.zip`）内容一致，均可装入 Edge 与 Chrome。任选其一解压即可。

### Microsoft Edge
1. 打开 `edge://extensions`
2. 打开左下角 **“开发人员模式”**
3. 点击 **“加载已解压缩的扩展”**，选择解压后的文件夹
4. 若提示授予 `windows` / `storage` 权限，请允许；点击工具栏图标即可使用

### Google Chrome
1. 打开 `chrome://extensions`
2. 打开右上角 **“开发者模式”**
3. 点击 **“加载已解压缩的扩展程序”**，选择解压后的文件夹
4. 点击工具栏拼图图标 → 钉住“横向收藏夹”，点击即可使用

## 重新加载
修改代码后，回到扩展管理页点击对应扩展的 **↻ 重新加载**（或快捷键 `Ctrl+R`）。

## 目录结构
```
manifest.json        扩展清单（MV3）
bg.js                后台 service worker：点击图标打开/聚焦面板窗口
popup.html/.css/.js  面板窗口 UI（双栏书签 + 设置 + 搜索）
icons/               16/48/128 图标
build.py             打包脚本：生成 edge / chrome 两种 zip 到 dist/
dist/                发行包输出目录
```

## 打包
```bash
python build.py
# 输出 dist/horizontal-bookmarks-edge-vX.Y.Z.zip
#      dist/horizontal-bookmarks-chrome-vX.Y.Z.zip
```

## 许可证
MIT
