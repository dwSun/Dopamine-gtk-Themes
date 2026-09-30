# Dopamine Themes 主题定制手册

本文档记录 `Dopamine Themes` 主题的来源、定制过程与验证方法。
后续要定制其他主题时，按「第 6 节 SOP」执行即可复用整套流程。

---

## 1. 主题从哪来

```mermaid
flowchart LR
    A["vinceliuice/Fluent-gtk-theme<br/>（本地 Fluent-gtk-theme，只读）"] -->|完整复制| B["Dopamine Themes<br/>（独立副本，可改）"]
    C["Maple Mono 官网<br/>font.subf.dev/zh-cn"] -->|提取 CSS 色板| D["Maple 色板"]
    D -->|第一轮：可读性| B
    D -->|第二轮：双主色| B
    B -->|install.sh| E["~/.themes/Dopamine-*&lt;色&gt;-Dark"]
    E -->|symlink| F["~/.config/gtk-3.0 / gtk-4.0"]
```

- **上游**：`/path/to/Fluent-gtk-theme`（你本地的 Fluent-gtk-theme 只读副本），保持 `git status` 干净，**永不修改**。
- **副本**：`Dopamine Themes` 项目根目录（你即将把文件夹重命名为 Dopamine），所有改动都在这里。
- **配色来源**：Maple Mono 官网 CSS（`curl` 页面 → 提取 `/_astro/*.css` → 统计 hex 频率）。

本 fork 的颜色变体：13 个完整调色板主题（8 个经典配色 nord/dracula/gruvbox/tokyo-night/everforest/monokai/solarized/catppuccin + 5 个多巴胺风格配色 candy/tangerine/minty/berry/nebula，参考终端/编辑器经典配色并重新为桌面设计）、
明暗变体、5 个 tweak（solid/float/round/noborder/square；本 fork **不提供** blur 版本）、
GTK 2/3/4、GNOME Shell 3-28~48、Cinnamon、Metacity、xfwm4、labwc、plank、Firefox 资源。

名称迁移点：`install.sh` 的 `THEME_NAME`、`release/make-release.sh`、README、
Firefox chrome、Metacity/xfwm4 元数据。

### 1.1 完整调色板主题（第四轮重构）

旧的 15 个 btop 衍生变体只替换了一个强调色，导致各主题除了 accent 外几乎一样。
第四轮重构把每个主题做成**完整调色板**：背景、表面、基底、正文、次级文字、链接、成功/警告/错误、标题栏/面板全部按主题重新设计。

参考来源包括 btop 主题、Nord/Dracula/Gruvbox/Tokyo Night/Everforest/Monokai/Solarized/Catppuccin 等经典配色，
但为 GTK/GNOME 桌面调整了对比度与可读性，不照搬终端色值。

| 主题 | 个性 | dark 主色 | light 主色 | dark 背景 | light 背景 |
|---|---|---|---|---|---|
| nord | 冰蓝/北极 | `#88c0d0` | `#5e81ac` | `#2e3440` | `#eceff4` |
| dracula | 紫粉/霓虹 | `#ff79c6` | `#bd93f9` | `#282a36` | `#f8f8f2` |
| gruvbox | 暖黄/大地 | `#fabd2f` | `#d79921` | `#282828` | `#fbf1c7` |
| tokyo-night | 深夜蓝/青 | `#7aa2f7` | `#565f89` | `#1a1b26` | `#d5d6db` |
| everforest | 森绿/自然 | `#a7c080` | `#8da101` | `#2b3339` | `#fdf6e3` |
| monokai | 高对比/霓虹 | `#f92672` | `#fd971f` | `#272822` | `#f8f8f2` |
| solarized | 经典青/琥珀 | `#b58900` | `#268bd2` | `#002b36` | `#fdf6e3` |
| catppuccin | pastel/现代 | `#f5c2e7` | `#8839ef` | `#1e1e2e` | `#eff1f5` |
| candy | 糖果粉 | `#FF4F9A` | `#E91E63` | `#2D1B2E` | `#FFF5F8` |
| tangerine | 活力橙 | `#FF8A1F` | `#F57C00` | `#3A1E12` | `#FFF8F0` |
| minty | 薄荷绿 | `#69F0AE` | `#00BFA5` | `#0F2E2B` | `#F0FFF7` |
| berry | 浆果红 | `#FF6F91` | `#E91E63` | `#2D1B2E` | `#FFF0F3` |
| nebula | 星云青 | `#00E5FF` | `#0091EA` | `#0A1E2E` | `#F0FCFF` |

完整色板定义在 `src/_sass/_theme-palettes.scss`，GTK 与 GNOME Shell 共用同一份 map。
每个主题不再区分「这是亮系还是暗系」；只保证 light/dark 两种 GNOME 变体都协调、对比足够。

每个变体的资源链（本机无 inkscape/rendersvg，PNG 用**像素色相重映射**生成）：

| 资源 | 来源 | 方法 |
|---|---|---|
| GTK3 `assets-<theme>/`（52 PNG）| `assets/` | HSV 色相旋转（蓝域 → 目标色相），S/V 按主色比例缩放；`-dark` 文件映射到 light 主色 |
| GTK2 `assets-<theme>{,-Dark}/`（30+30 PNG）| `assets{,-Dark}/` | 同上 |
| GTK2 `gtkrc-<theme>{,-Dark}` | `gtkrc{,-Dark}` | sed `#0078D4` |
| Shell `theme-<theme>/`（3 SVG）| `theme/` | sed `#0078D4`/`#1A73E8` |
| `assets-<theme>.svg` 源 | `assets.svg` | sed `#1A73E8`/`#3281EA`（供上游渲染链）|
| thumbnail PNG | `thumbnail*.png` | 色相重映射 |

注意 GTK2 Dark 目录命名是 `assets-<theme>-Dark`（`install.sh` 拼 `assets$theme$ELSE_DARK`），
不要写成 `assets-Dark-<theme>`。

新增自动化脚本：`scripts/generate-theme-assets.py`，一次生成 8 个主题的全部 PNG/SVG/gtkrc/thumbnail。

---

## 2. 配色系统

### 2.1 完整调色板（共享 map）

色板集中在 `src/_sass/_theme-palettes.scss`，每个主题提供 light/dark 两组完整颜色：

| 角色 | 说明 |
|---|---|
| `primary` | 选中/开关/进度/suggested 主强调色 |
| `background` | 窗口背景 `$background` |
| `surface` | 卡片/弹出层 `$surface` |
| `base` | 内容区/输入框 `$base` |
| `base-alt` | 次级表面 `$base-alt` |
| `foreground` | 正文色（`on()` 据此推导）|
| `foreground-secondary` | 次级文字 |
| `foreground-on-dark` | 用于深色背景上的动态前景 |
| `foreground-on-light` | 用于浅色背景上的动态前景 |
| `link` / `link-visited` | 链接色 |
| `success` / `warning` / `error` | 语义色 |
| `titlebar` / `panel` | 标题栏与面板底色 |

GTK 通过 `@import 'theme-palettes'` 读取 map，再用 `theme-color('background')`、`theme-color-mode('dark', 'titlebar')` 等函数绑定到 `$background`、`$titlebar` 等变量。
GNOME Shell 的 `_colors.scss` 同样导入该 map，绑定到 `$base_color`、`$fg_color`、`$primary_color` 等 Shell 变量。

### 2.2 动态前景

```mermaid
flowchart TD
    A["$background / $surface / $titlebar"] --> B["on($color, $state)"]
    B --> C{"亮度 ≥ 156?"}
    C -->|是| D["rgba(foreground-on-light, 0.87)"]
    C -->|否| E["rgba(foreground-on-dark, 0.97)"]
```

- GTK：`src/_sass/_colors.scss` 的 `on($color, $state)`。
- Shell：`src/gnome-shell/sass/_colors.scss` 的 `foreground($color)`。
- 亮度公式 `(R*299+G*587+B*114)/1000`，阈值 156。
- `foreground-on-dark` / `foreground-on-light` 来自当前主题调色板，因此暗色主题可以用暖灰正文（如 Gruvbox `#ebdbb2`），亮色主题可以用冷灰正文（如 Nord `#2e3440`）。

### 2.3 default 主题

`default`（未指定 `-t` 时安装）保留为独立调色板：
- dark：`#fbdbb6` 暖桃强调 + `#273749` 蓝灰背景
- light：`#bf7c50` 深桃强调 + `#eef3f8` 冷白背景

它不再退回到某个 btop 变体，确保无 `-t` 时仍有统一且可预测的外观。

---

## 3. 我们做过什么（操作史）

### 第一轮：可读性修复（Nautilus/设置内容区近黑、Shell 选中白字）

1. 深色 `$base` `#1e1e1f` → `#263847`（含 blur 分支 `rgba(#263847, $blur_opacity)`）——
   根因是内容区基底，不是文字色。
2. 正文/标题/禁用等全部走 `on()` 动态前景；Shell 侧 `$fg_color` 等变量换
   `#d9e9f2` / `rgba(#10222d, …)` 系列。
3. Shell 选中态 `color: white` → 动态前景，涉及文件：
   - `widgets/_quick-settings-42/44/48.scss`（checked/hover/active/菜单按钮/header 图标）
   - `widgets/_switches-47.scss`（含 `.handle`）
   - `widgets/_buttons.scss`（`%default_button` 全状态）
   - `widgets/_calendar.scss`、`_calendar-46.scss`（today 全状态）
   - `widgets/_dialogs-47.scss`（destructive/suggested）
   - `widgets/_window-picker.scss`、`_app-grid{,-44,-46}.scss`、`_screenshot.scss`
   - `_common-3-28.scss`（system-menu-action/calendar-today/app-view-control）
4. GTK 微修：`_common-3.20.scss` 红色 OSD 按钮 `on()` 化；
   `_common-4.0.scss` coverflow cover 黑边 `black` → `$border`。
5. **刻意保留**纯白/纯黑的专用高对比元素：`lightbox`、`flashspot`、screen-shield 解锁时钟、
   截图 UI 选择框、GTK `%osd-button`、`.avatar.contrasted`、Shell `$system_bg_color: #1e1e1f`。

### 第二轮：双主色鲜明化（解决「灰败」单色相）

1. 从网页提取 vivid 色，用户选定「桃选中 + 紫进度」组合。
2. 两份 `_colors.scss` 的 `theme()`：default dark `#abd5ed→#fbdbb6`、light `#527cad→#bf7c50`；
   orange dark 错开为 `#f7cf9e` 避免与新 default 撞色。
3. 新增 `$focus`（GTK）/`$focus_color`（Shell），替换引用：
   - GTK：`_common-3.20.scss`（树进度、progressbar、osd progress、levelbar）、
     `_common-4.0.scss`（同上 + editablelabel editing 轮廓 ×2）、`apps/_mate.scss`（OSD 进度）。
   - Shell：`_slider.scss`、`_slider-47.scss`、`_osd.scss`、`_osd-42.scss`、
     `_common-3-28.scss` 的全部 `-barlevel-active-*` 及 OSD 槽底。
4. Cinnamon 共用 `src/_sass/colors`，自动跟随，无需单独改。

### 第四轮：完整调色板重构（废弃 15 个单 accent btop 变体）

1. 废弃旧的 15 个 btop 单强调色变体，重新设计 8 个完整调色板主题：
   nord / dracula / gruvbox / tokyo-night / everforest / monokai / solarized / catppuccin。
2. 新增 `src/_sass/_theme-palettes.scss`：每个主题定义 light/dark 完整色板，
   GTK 与 Shell 共用同一份 map，避免两份 `_colors.scss` 重复维护。
3. 重写 `src/_sass/_colors.scss` 与 `src/gnome-shell/sass/_colors.scss`：
   - 背景、表面、基底、正文、链接、语义色、标题栏、面板全部取自调色板。
   - `on()` / `foreground()` 使用主题自己的 `foreground-on-dark` / `foreground-on-light`。
   - 标题栏/面板在「light 内容 + dark 标题栏」标准变体下使用 dark 调色板。
4. `install.sh`、`release/make-release.sh`、各 `render-assets.sh`、
   `scripts/gen-previews.py` 的主题列表同步更新。
5. 新增 `scripts/generate-theme-assets.py`（8 个经典主题）：
   从上游蓝色资源通过 HSV 色相重映射批量生成 8 主题的 GTK2/3 PNG、GTK2 gtkrc、
   Shell SVG、thumbnail PNG。
6. 新增 `scripts/generate-dopamine-assets.sh`（5 个多巴胺主题）：
   为 candy / tangerine / minty / berry / nebula 生成 SVG/PNG/gtkrc/thumbnail/README 预览图。
   因本机无 `inkscape`/`rendersvg`，GTK PNG 资源先复制默认蓝色资源作为 fallback，
   后续安装 `inkscape` 后可重新渲染主题色资源。
6. default 主题独立为完整调色板，不再 fallback 到 dracula。

### 工具链修复

- **`install.sh --name` 无效 bug**：原代码 `-n|--name` 分支写的是 `_name="$2"`，
  而安装循环用 `${name:-$THEME_NAME}`，`name` 从未赋值 → tweak 版会**同名覆盖**普通版。
  已修为 `name="$2"`。
- 安装命名策略：普通版 `--name Dopamine`，所有 tweak 版都用各自独立的 `--name` 区分。

---

## 4. 目录/文件地图

| 路径 | 作用 |
|---|---|
| `src/_sass/_colors.scss` | GTK/Cinnamon 配色：`on()`、`theme()`、`$primary/$focus`、语义色 |
| `src/gnome-shell/sass/_colors.scss` | Shell 配色：`foreground()`、`theme()`、`$focus_color` |
| `src/_sass/gtk/_common-{3.20,4.0}.scss` | GTK 控件样式（进度/levelbar/OSD） |
| `src/gnome-shell/sass/widgets/_quick-settings-*.scss` 等 | Shell 各版本控件，**必须按版本分层改**，不能合并 |
| `parse-sass.sh` | 全量编译（GTK3/4、Shell 各版本、Cinnamon） |
| `install.sh` | 安装/卸载/tweak/变体选择 |
| `release/make-release.sh` | 打包发布 |

---

## 5. 常用命令速查

```bash
cd /path/to/Dopamine-themes

# 1. 改完 scss 后必须重建
./parse-sass.sh

# 2. 安装全 13 色（深色）
./install.sh --dest ~/.themes --name Dopamine \
  --theme all --color dark

# 3. 切换 GTK 主题（libadwaita 应用读 ~/.config/gtk-4.0/gtk.css）
#    每个主题目录都自带 gtk-set.sh，会自动清理旧链接并建立新链接
~/.themes/Dopamine-nord-Dark/gtk-set.sh

# 5. 验证生成 CSS 中的颜色（nord 主题预期出现 #88c0d0）
grep -m3 -E '#88c0d0' ~/.themes/Dopamine-nord-Dark/gtk-4.0/gtk-dark.css
```

---

## 6. 新主题定制 SOP

1. **复制副本**：`cp -r Fluent-gtk-theme <NewTheme>`，只改副本；上游保持干净。
2. **名称迁移**：全局替换 `install.sh` 的 `THEME_NAME`、`release/make-release.sh`、
   README、Firefox/Metacity 元数据中的 `Fluent` → 新名。
3. **定色板**：从设计参考提取 10–14 个颜色，
   区分：背景系（3–4 档）、正文两枚（深/浅）、前景-on-dark/on-light 两枚、主强调 1 枚、链接/已访问链接 2 枚、语义 3 枚（红绿黄）、标题栏/面板。
4. **改 `src/_sass/_theme-palettes.scss`**：
   - 为主题新增 light/dark 两个 map。
   - 同步更新 `install.sh`、`release/make-release.sh`、各 `render-assets.sh`、
     `scripts/gen-previews.py`、文档中的主题列表。
5. **改两份 `_colors.scss`**（GTK + Shell 各一份）：
   - 使用 `theme-color()` / `theme-color-mode()` 绑定变量。
   - 正文仍走 `on()`/`foreground()` 动态前景，阈值 156。
   - 标题栏/面板处理「light 内容 + dark 标题栏」标准变体。
6. **控件层按需替换**前景引用（`color: white` → 动态前景）。
   Shell 文件**按版本分层**（-42/-44/-46/-47/-48、_common-3-28），逐一修改。
7. **生成资源**：`python3 scripts/generate-theme-assets.py`。
8. **保留专用高对比**：遮罩、flashspot、截图框、OSD、avatar.contrasted、`system_bg_color`。
9. `./parse-sass.sh` 重建。
10. 安装：tweak 版**用各自独立的 `--name`**。
11. **验证清单**：
    - [ ] `parse-sass.sh` 退出成功，关键 CSS 非空；
    - [ ] grep 生成 CSS：选中色、进度色、动态前景（如 `rgba(16, 34, 45, …)`）均出现；
    - [ ] `~/.config/gtk-{3,4}.0` 链接指向预期目录且 `test -e` 通过；
    - [ ] `git -C Fluent-gtk-theme status --short` 无输出；
    - [ ] Wayland 下无法用 X11 工具截屏时，视觉确认需注销重登后人工查看，
      不要凭 CSS 断言「已生效」。
12. 桌面验证：重启 GTK 应用；Shell 主题需注销重登（Wayland 不能 `Alt+F2 r`）。

---

## 7. 已知坑

| 坑 | 处理 |
|---|---|
| `install.sh` 原 `--name` 写入 `_name` 无效 | 已修复为 `name`；tweak 版必须独立命名 |
| Metacity 3 XML `version="< 3.1"` 解析告警 | 上游固有，与配色无关，忽略 |
| `~/.themes` 下同名目录重装即覆盖 | 切换主题组合时用不同 `--name` |
| GNOME 设置用 libadwaita：改 GTK4 链接后才生效 | 见第 5 节命令 4 |
| Wayland 无法 `import -window root` 截屏 | 视觉验证靠注销重登人工确认 |
