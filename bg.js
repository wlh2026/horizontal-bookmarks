'use strict';
/* ===== 横向收藏夹 v7.2 · 后台唤醒脚本 =====
 * 负责在用户点击工具栏图标时，打开（或聚焦已打开的）书签面板窗口。
 * 面板本身是一个独立的、可自由拖拽调整大小的浏览器窗口，
 * 因此不受 action popup 的硬性尺寸上限（约 800×600）限制。
 */

const PANEL_PAGE = 'popup.html';

// 打开或聚焦面板窗口：若已存在则聚焦，否则新建（沿用上次记忆的尺寸）
function openOrFocusPanel() {
  const target = chrome.runtime.getURL(PANEL_PAGE);

  chrome.storage.local.get(['bmWin'], (winRes) => {
    const saved = winRes && winRes.bmWin;
    const w = (saved && saved.w) || 1280;
    const h = (saved && saved.h) || 800;
    const state = (saved && saved.state) || 'normal';

    chrome.storage.session.get('panelWinId', async (saved2) => {
      const id = saved2 && saved2.panelWinId;
      if (typeof id === 'number') {
        try {
          await chrome.windows.update(id, { focused: true });
          return; // 已聚焦到已存在的窗口
        } catch (e) {
          // 窗口已被关闭，继续走新建流程
        }
      }
      // 若上次是最大化，则直接用 state 打开；否则沿用记忆的宽高
      const createOpts = {
        url: target,
        type: 'popup',
        focused: true
      };
      if (state === 'maximized') {
        createOpts.state = 'maximized';
      } else {
        createOpts.width = w;
        createOpts.height = h;
      }
      const win = await chrome.windows.create(createOpts);
      if (win && typeof win.id === 'number') {
        chrome.storage.session.set({ panelWinId: win.id });
      }
    });
  });
}

chrome.action.onClicked.addListener(openOrFocusPanel);
