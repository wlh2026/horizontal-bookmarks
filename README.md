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

## 安装

发行包两种格式（`dist/horizontal-bookmarks-{chrome,edge}-vX.Y.Z.{zip,crx}`），内容一致，均可装入 Edge 与 Chrome。

### 方式一：加载已解压缩（推荐，无任何警告）
> 自签名 `.crx` 在 Edge 中会触发“外来扩展不安全”拦截，**开发 / 自用请优先用这种方式**，干净无警告。

1. 解压 `*.zip`（解压后即为扩展文件夹）
2. 打开 `edge://extensions`（Edge）或 `chrome://extensions`（Chrome）
3. 打开 **“开发人员模式”**
4. 点击 **“加载已解压缩的扩展” / “加载已解压缩的扩展程序”**，选择解压后的文件夹
5. 若提示授予 `windows` / `storage` 权限，请允许；点击工具栏图标即可使用

### 方式二：直接拖入 `.crx` 安装
> ⚠️ 仅适用于自测。**Edge 会拦截非 Microsoft Store 签名的 `.crx`**，提示“外来扩展不安全，要求删除”。
> 若坚持用 `.crx`，需先按下方【排错】把本扩展 ID 加入放行列表，否则会被强制删除。

1. 打开 `edge://extensions`，开启“开发人员模式”
2. 将 `*.crx` 直接拖入浏览器窗口
3. 若提示拦截 → 见下方【排错】添加放行策略后重试

## 排错：Edge 提示“外来扩展不安全，要求删除”

**原因**：Edge 只信任 Microsoft Store 官方签名的扩展；自签名（自己用 `build.py` 生成的）`.crx` 一律被判定为“非商店来源 / 不安全”，因此弹出删除警告。这不是打包错误，无法通过重新打包消除。

**解决方案（任选其一）**

**方案 A（最干净，推荐）**：改用【方式一】加载解压缩文件夹，完全不触发该警告。

**方案 B（保留 `.crx`，本机放行）**：把本扩展 ID 加入 Edge 组策略放行列表，Edge 便不再拦截。
- 本扩展固定 ID：`b15b748eda62cf0da6ef1c3be63c2266`
- 仓库内已提供 `edge-allowlist.reg`，**双击导入**即可（写入 `HKCU`，无需管理员）；导入后重启 Edge。
- 若想手动操作：注册表 `HKEY_CURRENT_USER\Software\Policies\Microsoft\Edge\ExtensionInstallAllowlist` 下新建字符串值，名称 `1`，数据填上面的 ID。
- 注意：一旦设置 `ExtensionInstallAllowlist`，**只允许列表内的扩展**，其它扩展需一并加入，否则会被禁装。

**方案 C（给他人分发，彻底无警告）**：将扩展提交到 **Microsoft Edge Add-ons 商店** 完成官方签名。只有通过商店签名的 `.crx` 才不会警告。这是面向最终用户的唯一正规途径。

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
