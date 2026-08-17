# 上架 Microsoft Edge Add-ons 商店 · 资料包

本目录已为你备齐上架 **Microsoft Edge Add-ons** 所需的全部材料。按本指南操作即可完成提交。

> 说明：上架后，商店会为扩展分配**官方 ID**，自签名 `.crx` 的固定 ID（`b15b748eda62cf0da6ef1c3be63c2266`）仅用于本机自托管，与商店版本无关；此前用于绕过“外来扩展”警告的 `edge-allowlist.reg` 在商店版本上也不再需要（商店签名无警告）。

---

## 一、材料清单（Checklist）

- [x] **扩展包（.zip）** —— `dist/horizontal-bookmarks-store-v7.3.0.zip`（已生成，仅含扩展本体，无 `update_url`、无 Edge 专用块，符合商店要求）
- [x] **128×128 图标** —— `icons/icon128.png`（已校验尺寸）
- [x] **隐私政策** —— `PRIVACY.md`（可托管到 GitHub Pages，见第三节）
- [ ] **截图 1–10 张（1280×800 推荐，单张 ≤ 1 MB）** —— 见第四节拍摄指南
- [ ] **支持网站 / 联系方式** —— 建议填本仓库 Issues：`https://github.com/wlh2026/horizontal-bookmarks/issues`
- [ ] **宣传图（可选）** —— 440×280 / 1400×560 PNG，可后续补充

---

## 二、Partner Center 提交信息（可直接复制）

> 下列“显示名称 / 简短描述 / 详细描述”在 Partner Center 后台**手动填写**，不会从 `manifest.json` 自动读取（manifest 里的 `description` 只显示在浏览器扩展管理页）。两类语言都准备好，建议至少提交 **中文(简体) zh-CN** 与 **英语 en-US**。

### 1. 显示名称（Display name，≤ 128 字符，不能含 Microsoft/Edge/Windows 等）
```
horizontal-bookmarks
```
> 若想要更友好的商店名，可改 `manifest.json` 的 `name` 后重新 `python build.py` 再打包。例如 `Horizontal Bookmarks Panel` / `横向书签面板` 均可。

### 2. 简短描述（Short description，≤ 132 字符）

**中文（简体）：**
```
点击工具栏图标，在独立窗口展开多列横向书签面板（仿360收藏夹），可自由缩放并记忆布局。
```

**English：**
```
Click the toolbar icon to open a resizable multi-column horizontal bookmarks panel (like 360 Browser) in its own window.
```

### 3. 详细描述（Detailed description）

**中文（简体）：**
```
horizontal-bookmarks 是一个轻量（零依赖、原生 Manifest V3）的浏览器扩展，使用体验接近 360 浏览器的收藏夹：

• 点击工具栏图标，在独立可缩放窗口中展开多列横向书签面板，不再受弹窗尺寸上限限制，可拖拽边缘自由缩放、可最大化。
• 左侧文件夹导航 + 右侧书签网格的双栏布局（仿 360），点击文件夹原地切换，始终只有一列导航 + 一列书签。
• 界面设置（列宽 / 行高 / 列数 / 字号）可持久化；窗口尺寸与最大化状态也会记住，下次打开保持一致。
• 点击书签在新标签页打开，并自动收起/关闭面板窗口。
• 顶部支持书签搜索。
• 零依赖、纯原生 JavaScript，占用资源极小。

本扩展不会将任何数据发送到外部服务器，所有设置仅保存在您本地浏览器中。
```

**English：**
```
horizontal-bookmarks is a lightweight (zero-dependency, native Manifest V3) browser extension that works like the 360 Browser bookmarks panel:

• Click the toolbar icon to open a resizable multi-column horizontal bookmarks panel in its own window — no popup size limit, freely resizable, and maximizable.
• Two-column layout (like 360): a folder navigator on the left and a bookmark grid on the right. Click a folder to drill in; only one nav column + one bookmark column is ever shown.
• UI settings (column width / row height / column count / font size) persist. Window size and maximized state are also remembered.
• Clicking a bookmark opens it in a new tab and auto-closes the panel window.
• Built-in bookmark search in the header.
• Zero dependencies, pure native JavaScript — minimal resource usage.

This extension does not send any data to external servers; all settings are stored only in your local browser.
```

### 4. 类别（Category）
```
Productivity
```

### 5. 语言（Languages）
```
中文(简体) zh-CN
英语 en-US
```

### 6. 价格（Pricing）
```
免费 (Free)
```

---

## 三、隐私与权限声明（审核必填）

在提交表单的 **“隐私实践 / Privacy practices”** 部分：

- 数据收集选择：**“本扩展不收集或使用任何用户数据”**（This extension does not collect or use any user data）。
- 无需强制填写隐私政策 URL；但本仓库已提供 `PRIVACY.md`。如需填写，可托管到 GitHub Pages：
  1. 在仓库 `Settings → Pages` 启用，Source 选 `main` 分支根目录；
  2. 稍候片刻后访问 `https://wlh2026.github.io/horizontal-bookmarks/PRIVACY.md` 作为隐私政策 URL。

**权限用途说明（供审核参考，可粘贴到“补充说明”）：**
| 权限 | 用途 |
|------|------|
| `bookmarks` | 读取书签树以展示，并打开所点击的书签 |
| `windows` | 以独立窗口打开面板，记忆窗口大小/最大化状态 |
| `storage` | 在本地保存界面设置与窗口尺寸 |

三个权限均**仅在本地浏览器内**使用，不上传任何数据。

---

## 四、截图拍摄指南（必填，1–10 张）

商店要求至少 1 张截图，推荐 1280×800，单张 ≤ 1 MB，格式 PNG/JPG。

**拍摄步骤：**
1. 在 Edge 中按 README【方式一】加载本扩展（解压目录）。
2. 点击工具栏图标打开面板窗口，按需调整大小或最大化。
3. 用 `Win + Shift + S` 或 Edge 内置捕获，截取 **1280×800** 区域。
4. 保存为 PNG，确认单张 ≤ 1 MB（可用画图或在线工具压缩）。
5. 建议准备 4 张：① 默认双栏展开；② 设置面板（齿轮）；③ 搜索状态；④ 最大化状态。

> 如果你希望我用无头浏览器（Playwright）直接生成真实截图，告诉我，我可以安装并在本机渲染后导出。

---

## 五、提交流程（分步）

1. **注册开发者账号**：访问 https://partner.microsoft.com/dashboard/microsoftedge ，“注册”为 Edge 扩展开发者（按页面提示，历史上个人开发者有过一次性注册费，请以当前官方页面为准）。
2. 进入 **Edge Add-ons 开发人员仪表板** → **“新建扩展”**。
3. **上传包**：选择 `dist/horizontal-bookmarks-store-v7.3.0.zip`。
4. **填写Listing**：复制第二节的显示名称、简短描述、详细描述、类别、语言、价格。
5. **上传资源**：128×128 图标 + 截图（第四节）；可选上传宣传图。
6. **隐私声明**：按第三节选择“不收集数据”，如需可填隐私政策 URL。
7. **补充说明**：粘贴第三节的权限用途表。
8. **提交审核**：提交后通常数个工作日内完成审核；被驳回会邮件通知，按意见修改后重新提交即可。

---

## 六、注意事项

- 商店只接受 **.zip** 包（不接受 `.crx`），且必须为 **Manifest V3**。本包已满足。
- 包内**不能含 `update_url`**；本包已确认不含。
- 商店会重新分配扩展 ID，与本地自签名 `.crx` 的固定 ID 无关。
- 上架成功后，建议把此前对话中暴露过的 GitHub PAT（`ghp_...`）吊销重发。
- 后续发版：更新 `manifest.json` 的 `version` → `python build.py` → 在仓库重新打包并推送；商店侧需在仪表板上传新包并更新版本。

---

## 七、本资料包新增文件

| 文件 | 说明 |
|------|------|
| `STORE-SUBMISSION.md` | 本指南（含可直接复制的提交信息） |
| `PRIVACY.md` | 隐私政策（中/英） |
| `dist/horizontal-bookmarks-store-v7.3.0.zip` | 商店提交用干净扩展包 |
