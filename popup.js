'use strict';
/* ===== 横向收藏夹 v7.2 · Popup 逻辑 =====
 * 运行在 popup 环境中：可直接访问 chrome.bookmarks API。
 * 双栏布局：左侧导航列（文件夹）+ 右侧书签网格。
 * 点击文件夹 → 原地替换导航列 + 同步更新右侧书签。
 * 永远只有一列导航 + 一列书签，无级联多列。
 */

// 兜底：确保独立窗口标题栏显示短名称，而非完整 URL
document.title = 'horizontal-bookmarks';

const $ = id => document.getElementById(id);

// ---------- 默认配置 ----------
// 注意：面板运行在独立窗口中，外框尺寸由窗口本身决定（可自由拖拽缩放），
// 因此不再需要 width/height 参数。以下为面板内部布局密度参数。
const DEFAULTS = {
  navW: 110, rowH: 46, bmCols: 3, font: 13
};

let cfg = { ...DEFAULTS };
let rootContainers = [];
let currentNode = null;    // 当前选中的文件夹节点（null = 显示根容器第一个）
let navHistory = [];       // 导航历史栈
let setInputs = {}, valDisplays = {};

// ---------- 设置 ----------
function saveSettings() {
  try { chrome.storage.local.set({ bmCfg: cfg }); } catch (e) {}
}
function applySettings() {
  document.body.style.setProperty('--nw', cfg.navW + 'px');
  document.body.style.setProperty('--rh', cfg.rowH + 'px');
  document.body.style.setProperty('--bc', String(cfg.bmCols));
  document.body.style.setProperty('--fs', cfg.font + 'px');
  ['navW','rowH','bmCols','font'].forEach(k => {
    const inp = setInputs[k]; if (inp) inp.value = cfg[k];
    const vd = valDisplays[k]; if (vd) vd.textContent = cfg[k];
  });
}

// ---------- 工具函数 ----------
function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function colorFromUrl(url) {
  let host = '';
  try { host = new URL(url).hostname; } catch { host = url || ''; }
  let h = 0;
  for (let i = 0; i < host.length; i++) h = (h * 31 + host.charCodeAt(i)) % 360;
  return `hsl(${h}, 58%, 48%)`;
}
function avatar(node) {
  const ch = (node.title || node.url || '?').trim().charAt(0).toUpperCase() || '?';
  const bg = node.url ? colorFromUrl(node.url) : '#8a92a4';
  return `<span class="avatar" style="background:${bg}">${esc(ch)}</span>`;
}
function openUrl(url) {
  if (!url) return;
  // 在新标签页打开书签
  chrome.tabs.create({ url });
  // 打开后关闭整个面板窗口（点击书签即收起/关闭）
  closePanel();
}

// 关闭当前面板窗口（优先用 chrome API，回退 window.close）
function closePanel() {
  try {
    if (chrome.windows && chrome.windows.getCurrent) {
      chrome.windows.getCurrent(win => {
        if (win && win.id != null) { chrome.windows.remove(win.id); return; }
        window.close();
      });
      return;
    }
  } catch (e) {}
  window.close();
}
function countAll() {
  let n = 0;
  const walk = node => { if (node.children) node.children.forEach(walk); else n++; };
  rootContainers.forEach(walk);
  return n;
}

// ---------- 构建左侧导航列 ----------
function buildNavCol(title, folders) {
  const col = document.createElement('div');
  col.className = 'nav-col';
  const head = document.createElement('div');
  head.className = 'col-head';
  head.textContent = title;
  col.appendChild(head);
  if (!folders.length) {
    const e = document.createElement('div');
    e.className = 'empty-item'; e.textContent = '(无子文件夹)';
    col.appendChild(e); return col;
  }
  folders.forEach(f => {
    const el = document.createElement('div');
    el.className = 'item folder';
    el.innerHTML = `<span class="name">${esc(f.title || '未命名')}</span><span class="arrow">›</span>`;
    el.addEventListener('click', () => {
      if (currentNode) navHistory.push(currentNode);
      currentNode = f;
      render();
    });
    col.appendChild(el);
  });
  return col;
}

// ---------- 面包屑导航 ----------
function buildBreadcrumb() {
  const bar = document.createElement('div');
  bar.className = 'breadcrumb';
  // 首页按钮
  const homeBtn = document.createElement('span');
  homeBtn.className = 'crumb home';
  homeBtn.textContent = '🏠 收藏夹栏';
  homeBtn.addEventListener('click', () => {
    if (currentNode) navHistory.push(currentNode);
    currentNode = null;
    render();
  });
  bar.appendChild(homeBtn);
  // 历史路径
  navHistory.forEach((node, i) => {
    const sep = document.createElement('span'); sep.className = 'crumb-sep'; sep.textContent = '›'; bar.appendChild(sep);
    const crumb = document.createElement('span'); crumb.className = 'crumb'; crumb.textContent = node.title || '文件夹';
    crumb.addEventListener('click', () => { currentNode = node; navHistory = navHistory.slice(0, i); render(); });
    bar.appendChild(crumb);
  });
  // 当前位置
  if (currentNode) {
    const sep = document.createElement('span'); sep.className = 'crumb-sep'; sep.textContent = '›'; bar.appendChild(sep);
    const cur = document.createElement('span'); cur.className = 'crumb current'; cur.textContent = currentNode.title || '文件夹';
    bar.appendChild(cur);
  }
  return bar;
}

// ---------- 书签网格 ----------
function buildBookmarkGrid(title, bookmarks) {
  const wrap = document.createElement('div');
  wrap.className = 'bm-wrap';
  const head = document.createElement('div');
  head.className = 'bm-head'; head.textContent = title + ` (${bookmarks.length})`;
  wrap.appendChild(head);
  const grid = document.createElement('div');
  grid.className = 'bm-grid';
  if (!bookmarks.length) {
    const e = document.createElement('div'); e.className = 'empty-item'; e.textContent = '此文件夹下没有书签';
    grid.appendChild(e);
  } else {
    bookmarks.forEach(node => {
      const el = document.createElement('div');
      el.className = 'item link';
      const name = node.title || node.url || '未命名';
      el.innerHTML = `${avatar(node)}<span class="name">${esc(name)}</span>`;
      const url = node.url || '';
      el.title = name + (url ? '\n' + url : '');
      el.addEventListener('click', () => openUrl(url));
      grid.appendChild(el);
    });
  }
  wrap.appendChild(grid);
  return wrap;
}

// ---------- 主渲染（双栏）----------
function render() {
  const mainEl = $('main');
  const statusEl = $('status');
  mainEl.innerHTML = '';

  // 面包屑
  mainEl.appendChild(buildBreadcrumb());

  // 决定显示哪个节点的数据
  let displayNode = currentNode ? currentNode : (rootContainers[0] || null);
  if (!displayNode) { statusEl.textContent = '未找到书签数据（收藏夹可能为空）'; return; }

  const contentRow = document.createElement('div');
  contentRow.className = 'content-row';

  // 左侧：导航列（只显示子文件夹）
  const navWrap = document.createElement('div');
  navWrap.className = 'nav-wrap';
  const folders = (displayNode.children || []).filter(c => c.children);
  navWrap.appendChild(buildNavCol(displayNode.title || '文件夹', folders));
  contentRow.appendChild(navWrap);

  // 右侧：书签网格
  const links = (displayNode.children || []).filter(c => !c.children);
  if (links.length > 0) {
    contentRow.appendChild(buildBookmarkGrid(displayNode.title || '书签', links));
  } else {
    // 无书签时让导航区占满宽度
    navWrap.style.flex = '1 1 auto';
    if (folders.length > 0) {
      const tip = document.createElement('div');
      tip.className = 'empty-item nav-tip';
      tip.textContent = '← 点击左侧文件夹查看书签';
      contentRow.appendChild(tip);
    }
  }

  mainEl.appendChild(contentRow);
  statusEl.textContent = `共 ${countAll()} 个书签 · 点击文件夹切换 · ⚙️ 可调布局`;
}

// ---------- 搜索 ----------
function doSearch(q) {
  const mainEl = $('main');
  const statusEl = $('status');
  const clearEl = $('clear');
  q = q.trim().toLowerCase();
  if (!q) { render(); clearEl.style.display = 'none'; return; }
  clearEl.style.display = 'flex';

  const results = [];
  const walk = (node, path) => {
    if (node.children) {
      node.children.forEach(c => walk(c, path.concat(node.title || '')));
    } else {
      const t = (node.title || '').toLowerCase();
      const u = (node.url || '').toLowerCase();
      if (t.includes(q) || u.includes(q)) results.push({ node, path: path.filter(Boolean) });
    }
  };
  rootContainers.forEach(c => walk(c, []));

  mainEl.innerHTML = '';
  const list = document.createElement('div');
  list.className = 'search-list';
  if (!results.length) {
    const e = document.createElement('div'); e.className = 'empty-item';
    e.textContent = `"${esc(q)}" — 未找到匹配的书签`; list.appendChild(e);
  } else {
    results.forEach(({ node, path }) => {
      const r = document.createElement('div');
      r.className = 'result';
      r.innerHTML = `${avatar(node)}<span class="r-path">${esc(path.join(' › '))}</span><span class="r-name">${esc(node.title || node.url)}</span>`;
      r.title = node.url || '';
      r.addEventListener('click', () => openUrl(node.url));
      list.appendChild(r);
    });
  }
  mainEl.appendChild(list);
  statusEl.textContent = `找到 ${results.length} 个匹配 · 共 ${countAll()} 个书签`;
}

// ---------- 初始化 ----------
function init(tree) {
  if (chrome.runtime?.lastError) {
    $('status').textContent = '读取书签失败：' + chrome.runtime.lastError.message;
    return;
  }
  rootContainers = tree?.[0]?.children || [];
  currentNode = null;
  navHistory = [];

  // 设置面板绑定
  setInputs = {
    navW: $('set-nav-w'),
    rowH: $('set-row-h'),
    bmCols: $('set-bm-cols'),
    font: $('set-font')
  };
  valDisplays = {
    navW: $('val-nav'),
    rowH: $('val-row'),
    bmCols: $('val-cols'),
    font: $('val-font')
  };

  Object.keys(setInputs).forEach(k => {
    const el = setInputs[k]; if (!el) return;
    el.addEventListener('input', () => { cfg[k] = Number(el.value); if (valDisplays[k]) valDisplays[k].textContent = el.value; });
  });

  const overlayEl = $('settings-overlay');
  $('btn-settings').addEventListener('click', () => overlayEl.classList.add('open'));
  $('settings-close').addEventListener('click', () => overlayEl.classList.remove('open'));
  overlayEl.addEventListener('click', e => { if (e.target === overlayEl) overlayEl.classList.remove('open'); });

  $('set-reset').addEventListener('click', () => { cfg = { ...DEFAULTS }; applySettings(); });
  $('set-apply').addEventListener('click', () => {
    Object.keys(setInputs).forEach(k => { cfg[k] = Number(setInputs[k].value); });
    saveSettings(); applySettings(); overlayEl.classList.remove('open'); render();
  });

  // 搜索
  const searchEl = $('search'), clearEl = $('clear');
  searchEl.addEventListener('input', () => doSearch(searchEl.value));
  clearEl.addEventListener('click', () => { searchEl.value = ''; doSearch(''); searchEl.focus(); });

  applySettings();
  render();
}

// ---------- 窗口尺寸/状态记忆 ----------
function trackWindowSize() {
  let t = null;
  function persist() {
    // 同时记录当前窗口状态（maximized / normal 等），下次直接以该状态打开
    try {
      chrome.windows.getCurrent({}, (win) => {
        const st = (win && win.state) || 'normal';
        chrome.storage.local.set({
          bmWin: { w: window.innerWidth, h: window.innerHeight, state: st }
        });
      });
    } catch (e) {}
  }
  window.addEventListener('resize', () => {
    clearTimeout(t);
    t = setTimeout(persist, 400);
  });
}

// 启动：先加载持久化设置，再读取书签
function start() {
  trackWindowSize();
  chrome.storage.local.get(['bmCfg'], (res) => {
    if (res.bmCfg) cfg = { ...DEFAULTS, ...res.bmCfg };
    applySettings();
    if (chrome && chrome.bookmarks && chrome.bookmarks.getTree) {
      chrome.bookmarks.getTree(init);
    } else {
      const s = $('status');
      if (s) s.textContent = '错误：当前环境不支持书签 API';
    }
  });
}
start();
