---
name: liquid-glass-ui
description: |
  液态玻璃（Liquid Glass）风格 HTML 页面生成器。
  灵感来源于 Apple WWDC25 设计语言，通过 SVG 滤镜扭曲 + 多层毛玻璃叠加 + 深色沉浸背景，
  创造出具有折射感、光泽感、深度感的现代 UI。

  适用场景：产品展示页、个人主页、Dashboard、单词卡片、Keynote 风格展示、
  App Landing Page、作品集等一切需要高级视觉质感的单页 HTML。

  触发条件（满足任一即触发）：
  - 用户要求制作"液态玻璃"、"毛玻璃"、"glassmorphism"风格页面
  - 用户提到"Apple 风格"、"WWDC 风格"、"iOS 风格"UI
  - 用户要求制作有"折射效果"、"玻璃质感"的 HTML
  - 用户说"做一个好看的展示页面"且未指定其他风格
  - 用户要求 Bento Grid 布局 + 玻璃卡片

  触发词：liquid glass、液态玻璃、毛玻璃、玻璃风格、glassmorphism、Apple风格、
  WWDC风格、Bento Grid、玻璃卡片、折射效果、glass UI
version: 1.0.0
---

# Liquid Glass UI — 液态玻璃风格 HTML 生成器

生成具有 Apple WWDC25 设计语言的液态玻璃风格单页 HTML。核心特征：SVG 滤镜扭曲折射、4 层毛玻璃架构、深色沉浸式背景、弹性交互动画。

---

## 技术栈（固定，不可替换）

每个生成的 HTML 必须包含以下 CDN 引用：

```html
<!-- TailwindCSS CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Google Fonts: Inter -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<!-- Font Awesome CDN -->
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css">
```

---

## 核心架构：4 层液态玻璃卡片

每张卡片由 5 个 HTML 元素组成：1 个容器 + 4 个层。**此结构是液态玻璃效果的核心，任何卡片都必须严格遵循。**

### HTML 结构（必须逐字使用）

```html
<div class="liquidGlass-wrapper">
    <div class="liquidGlass-effect"></div>   <!-- Layer 0: 扭曲折射层 -->
    <div class="liquidGlass-tint"></div>     <!-- Layer 1: 半透明色调层 -->
    <div class="liquidGlass-shine"></div>    <!-- Layer 2: 边缘光泽层 -->
    <div class="liquidGlass-text">           <!-- Layer 3: 内容层 -->
        <!-- 实际内容放在这里 -->
    </div>
</div>
```

### CSS 定义（必须完整包含）

```css
/* --- 液态玻璃卡片系统 --- */

/* 容器：包裹所有层，提供圆角、阴影、hover 动画 */
.liquidGlass-wrapper {
    position: relative;
    display: flex;
    overflow: hidden;
    padding: 0.6rem;
    border-radius: 2rem;
    cursor: pointer;
    box-shadow: 0 6px 6px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 0, 0, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.5);
}

/* Hover：弹性放大 + 增强阴影 */
.liquidGlass-wrapper:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25), 0 0 40px rgba(0, 0, 0, 0.15);
}

/* Layer 0 - 扭曲折射层：backdrop-filter 模糊 + SVG 滤镜扭曲 */
.liquidGlass-effect {
    position: absolute;
    z-index: 0;
    inset: 0;
    backdrop-filter: blur(3px);
    filter: url(#glass-distortion);
}

/* Layer 1 - 色调层：半透明白色叠加，营造雾化感 */
.liquidGlass-tint {
    position: absolute;
    z-index: 1;
    inset: 0;
    background: rgba(255, 255, 255, 0.12);
    border-radius: inherit;
}

/* Layer 2 - 光泽层：内嵌阴影模拟玻璃边缘的高光和暗光 */
.liquidGlass-shine {
    position: absolute;
    z-index: 2;
    inset: 0;
    border-radius: inherit;
    box-shadow:
        inset 1px 1px 1px 0 rgba(255, 255, 255, 0.5),
        inset -1px -1px 1px 0 rgba(255, 255, 255, 0.2);
}

/* Layer 3 - 内容层：承载文字、图标等实际内容 */
.liquidGlass-text {
    position: relative;
    z-index: 3;
    width: 100%;
    height: 100%;
}
```

### 各层参数可调范围

| 层 | 属性 | 默认值 | 可调范围 | 说明 |
|----|------|--------|----------|------|
| wrapper | border-radius | 2rem | 1rem ~ 3rem | 圆角越大越柔和 |
| wrapper | padding | 0.6rem | 0.4rem ~ 1rem | 内边距 |
| wrapper:hover | scale | 1.03 | 1.02 ~ 1.08 | 悬停放大比例 |
| effect | blur | 3px | 2px ~ 8px | 背景模糊强度 |
| tint | background opacity | 0.12 | 0.08 ~ 0.20 | 白色覆盖层透明度 |
| shine | highlight opacity | 0.5 / 0.2 | 0.3~0.6 / 0.1~0.3 | 高光/暗光边缘强度 |

---

## SVG 扭曲滤镜

此 SVG 必须放在 `</body>` 前，是液态玻璃折射效果的来源：

```html
<svg style="display: none">
    <filter id="glass-distortion">
        <feTurbulence type="fractalNoise" baseFrequency="0.01 0.01" numOctaves="1" seed="5"/>
        <feGaussianBlur stdDeviation="3" result="softMap"/>
        <feDisplacementMap in="SourceGraphic" in2="softMap" scale="80" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
</svg>
```

### 滤镜参数调节指南

| 参数 | 默认值 | 效果说明 |
|------|--------|----------|
| type | fractalNoise | `fractalNoise` 更自然柔和；`turbulence` 更规则对称 |
| baseFrequency | 0.01 0.01 | 值越小扭曲块越大越柔和；值越大纹理越细碎 |
| numOctaves | 1 | 噪声层数，1 层最干净；2-3 增加细节但可能过于杂乱 |
| stdDeviation | 3 | 高斯模糊强度，软化噪声贴图 |
| scale | 80 | **关键参数** — 扭曲强度。40=微妙，80=中等，150-200=强烈波浪 |

### 预设配置

**轻柔折射**（单卡展示、阅读类）：
```
baseFrequency="0.005 0.01" scale="40"
```

**中等折射**（通用推荐）：
```
baseFrequency="0.01 0.01" scale="80"
```

**强烈折射**（Bento Grid 展示、Keynote 风格）：
```
baseFrequency="0.01 0.01" scale="150-200"
```

---

## 背景系统

### 必须遵守的规则

1. **深色底色兜底**：`background-color: #050210` 或 `#000`（图片加载前显示）
2. **全屏背景图**：覆盖整个视口
3. **白色文字**：`<body class="text-white antialiased">`

### 方案 A — 固定背景（推荐用于多卡片/可滚动页面）

```css
body {
    font-family: 'Inter', sans-serif;
    background-color: #000;
    background-image: url('背景图URL');
    background-size: cover;
    background-position: center;
    background-attachment: fixed; /* 固定背景，滚动时卡片折射产生视差 */
}
```

### 方案 B — 动画背景（推荐用于单卡片/展示页）

```css
@keyframes backgroundPan {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

body {
    font-family: 'Inter', sans-serif;
    background-color: #050210;
    background-image: url('背景图URL');
    background-size: 200% 200%;
    background-position: center;
    animation: backgroundPan 180s linear infinite;
}
```

### 背景图选择原则

- **优先选择**：城市夜景、星空、抽象渐变光斑、深色自然风景
- **避免选择**：纯白/浅色背景、高对比度文字多的图片
- **推荐来源**：Unsplash（使用 `?q=80&w=2071&auto=format&fit=crop` 参数优化加载）
- 如果用户未指定，使用纯深色渐变 CSS 背景：
```css
background: linear-gradient(135deg, #0a0015 0%, #050210 30%, #0d1b2a 70%, #1b0a2e 100%);
```

---

## 排版系统

### 字体规则

| 用途 | 字号 | 字重 | Tailwind 类 |
|------|------|------|-------------|
| 超大标题 | 6xl ~ 9xl (60-128px) | font-extrabold / font-black (800/900) | `text-6xl font-extrabold tracking-tighter` |
| 大标题 | 3xl ~ 4xl (30-36px) | font-bold (700) | `text-3xl font-bold tracking-tight` |
| 副标题 | lg ~ xl (18-20px) | font-light (300) | `text-lg font-light text-gray-300` |
| 正文 | base (16px) | font-medium (500) | `text-base font-medium` |
| 辅助文字 | sm (14px) | font-medium (500) | `text-sm font-medium text-white/60` |

### 文字质感增强

```css
/* 为标题添加柔和阴影，增加深度感和可读性 */
.liquidGlass-text h1,
.liquidGlass-text h2,
.liquidGlass-text h3 {
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}
```

### 渐变文字效果

**Apple 彩虹渐变**（用于高亮关键词）：
```css
.text-gradient-apple {
    background-image: linear-gradient(120deg, #ff2d55, #ff9500, #ffcc00, #4cd964, #5ac8fa, #007aff, #5856d6);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

**清冷蓝渐变**（用于科技/产品名称）：
```css
.text-gradient-cool {
    background-image: linear-gradient(90deg, #5ac8fa, #a8e0ff);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

**紫金渐变**（用于高端/奢华感）：
```css
.text-gradient-luxury {
    background-image: linear-gradient(120deg, #b388ff, #ffcc00, #ff9500);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

用法示例：
```html
<h3 class="text-6xl font-extrabold tracking-tighter">
    Hello <span class="text-gradient-apple">World</span>
</h3>
```

---

## 色彩系统

### 核心色板

| 用途 | 颜色 | 值 |
|------|------|-----|
| 背景底色 | 深紫黑 | `#050210` |
| 备用底色 | 纯黑 | `#000000` |
| 主文字 | 纯白 | `text-white` |
| 副文字 | 灰色 | `text-gray-300` |
| 弱化文字 | 半透明白 | `text-white/60` |
| 图标弱化 | 半透明白 | `text-white/80` 或 `text-white/60` |
| 玻璃色调 | 半透明白 | `rgba(255, 255, 255, 0.10 ~ 0.15)` |
| 高光边缘 | 半透明白 | `rgba(255, 255, 255, 0.5)` |
| 暗光边缘 | 半透明白 | `rgba(255, 255, 255, 0.2)` |

### Apple 系统色（用于渐变和强调）

```
红:    #ff2d55
橙:    #ff9500
黄:    #ffcc00
绿:    #4cd964
浅蓝:  #5ac8fa
蓝:    #007aff
紫:    #5856d6
```

### 高亮渐变条（用于功能展示区域）

```css
.highlight-fade-blue {
    background: linear-gradient(90deg, rgba(90, 200, 250, 0.4), rgba(90, 200, 250, 0));
}
.highlight-fade-purple {
    background: linear-gradient(90deg, rgba(88, 86, 214, 0.4), rgba(88, 86, 214, 0));
}
```

---

## 布局模式

### 模式 A — 居中单卡片

适用：单词卡片、个人简介、产品展示卡、启动页

```html
<div class="min-h-screen w-full flex items-center justify-center p-4">
    <div class="w-full max-w-md">
        <div class="liquidGlass-wrapper h-64">
            <!-- 4 层玻璃结构 -->
            <div class="liquidGlass-effect"></div>
            <div class="liquidGlass-tint"></div>
            <div class="liquidGlass-shine"></div>
            <div class="liquidGlass-text p-8 flex flex-col justify-between">
                <!-- 内容 -->
            </div>
        </div>
    </div>
</div>
```

### 模式 B — Bento Grid（多卡片网格）

适用：Dashboard、Keynote 展示、功能一览、产品发布页

```html
<div class="min-h-screen w-full p-4 sm:p-6 lg:p-8 py-24 flex items-center justify-center">
    <div class="w-full max-w-screen-2xl mx-auto grid grid-cols-12 gap-4 sm:gap-6">

        <!-- 大卡片 (跨 7 列 3 行) -->
        <div class="col-span-12 md:col-span-7 row-span-3">
            <div class="liquidGlass-wrapper h-full">
                <!-- 4 层 + 内容 -->
            </div>
        </div>

        <!-- 中卡片 (跨 5 列 2 行) -->
        <div class="col-span-12 md:col-span-5 row-span-2">
            <div class="liquidGlass-wrapper h-full">
                <!-- 4 层 + 内容 -->
            </div>
        </div>

        <!-- 小卡片 (跨 3-4 列 1 行) -->
        <div class="col-span-6 md:col-span-3 row-span-1">
            <div class="liquidGlass-wrapper h-full">
                <!-- 4 层 + 内容 -->
            </div>
        </div>

        <!-- 宽卡片 (跨 12 列 2 行) -->
        <div class="col-span-12 row-span-2">
            <div class="liquidGlass-wrapper h-full">
                <!-- 4 层 + 内容 -->
            </div>
        </div>

    </div>
</div>
```

### Bento Grid 常见卡片尺寸

| 卡片类型 | 列宽 | 行高 | 适用内容 |
|----------|------|------|----------|
| Hero 大卡片 | col-span-7 | row-span-3 | 主产品展示、大数字、大图标 |
| 中卡片 | col-span-5 | row-span-2 | 功能介绍、带图标的标题 |
| 横向小卡片 | col-span-5 | row-span-1 | 单行功能名称 |
| 正方小卡片 | col-span-3 | row-span-1 | 图标 + 标签 |
| 全宽长卡片 | col-span-12 | row-span-2 | 功能列表、详细介绍 |

---

## 交互与动画

### 卡片 hover 效果（已内置于 CSS）

- 弹性放大：`scale(1.03)` + `cubic-bezier(0.175, 0.885, 0.32, 1.5)`
- 阴影增强：从 `6px` 提升到 `20px`

### 可选：内容层反向缩放（制造"呼吸感"）

```css
.liquidGlass-text {
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.5);
}
.liquidGlass-wrapper:hover .liquidGlass-text {
    transform: scale(0.98);
}
```

### 可选：内容淡入淡出切换

```css
.content-transition {
    transition: opacity 0.5s ease-in-out;
}
.content-transition.fade-out {
    opacity: 0;
}
```

### 可选：动态 SVG 噪声动画

```javascript
let frame = 0;
const turbulence = document.querySelector('#glass-distortion feTurbulence');
function animateTurbulence() {
    frame += 0.5; // 值越大抖动越快；设为 0 则静止
    turbulence.setAttribute('seed', Math.floor(frame));
    requestAnimationFrame(animateTurbulence);
}
animateTurbulence();
```

---

## 图标使用规范

使用 Font Awesome 5 图标库：

```html
<!-- 大图标（装饰用，弱化透明度） -->
<i class="fas fa-cube text-[20rem] text-white/5"></i>

<!-- 中图标（功能标识） -->
<i class="fas fa-microchip text-4xl text-white/80"></i>

<!-- 小图标（卡片角落装饰） -->
<i class="fas fa-bookmark text-3xl text-white/60"></i>

<!-- 渐变图标 -->
<i class="fas fa-brain text-6xl text-gradient-apple"></i>
```

图标放置规则：
- 装饰性大图标：`absolute` 定位，低透明度 (`text-white/5`)，可旋转 (`transform rotate-12`)
- 功能标识图标：卡片左上角或右上角，`absolute top-6 left-6`
- 内联图标：与文字同行，使用 `flex items-center` 对齐

---

## 完整页面模板

### 模板 A — 居中展示卡片

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #050210;
            background-image: url('背景图URL');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        /* 粘贴完整的液态玻璃 CSS（见上方"CSS 定义"章节） */
        .liquidGlass-wrapper { /* ... */ }
        .liquidGlass-wrapper:hover { /* ... */ }
        .liquidGlass-effect { /* ... */ }
        .liquidGlass-tint { /* ... */ }
        .liquidGlass-shine { /* ... */ }
        .liquidGlass-text { /* ... */ }
        .text-gradient-apple { /* ... */ }
    </style>
</head>
<body class="text-white antialiased">
    <div class="min-h-screen w-full flex items-center justify-center p-4">
        <div class="w-full max-w-md">
            <div class="liquidGlass-wrapper h-64">
                <div class="liquidGlass-effect"></div>
                <div class="liquidGlass-tint"></div>
                <div class="liquidGlass-shine"></div>
                <div class="liquidGlass-text p-8 flex flex-col justify-end">
                    <h3 class="text-6xl font-extrabold tracking-tighter">
                        标题<span class="text-gradient-apple">高亮</span>
                    </h3>
                    <p class="text-lg font-light text-gray-300 mt-2">副标题描述文字</p>
                </div>
            </div>
        </div>
    </div>
    <!-- SVG 滤镜 -->
    <svg style="display: none">
        <filter id="glass-distortion">
            <feTurbulence type="fractalNoise" baseFrequency="0.01 0.01" numOctaves="1" seed="5"/>
            <feGaussianBlur stdDeviation="3" result="softMap"/>
            <feDisplacementMap in="SourceGraphic" in2="softMap" scale="80" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
    </svg>
</body>
</html>
```

### 模板 B — Bento Grid 多卡片

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #000;
            background-image: url('背景图URL');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        /* 粘贴完整的液态玻璃 CSS */
        .liquidGlass-wrapper { /* ... */ }
        /* ... 所有层的 CSS ... */
        .text-gradient-apple { /* ... */ }
        .highlight-fade-blue { /* ... */ }
        .highlight-fade-purple { /* ... */ }
    </style>
</head>
<body class="text-white antialiased">
    <div class="min-h-screen w-full p-4 sm:p-6 lg:p-8 py-24 flex items-center justify-center">
        <div class="w-full max-w-screen-2xl mx-auto grid grid-cols-12 grid-rows-6 gap-4 sm:gap-6 h-[80vh] min-h-[900px]">

            <!-- Hero 大卡片 -->
            <div class="col-span-12 md:col-span-7 row-span-3">
                <div class="liquidGlass-wrapper h-full">
                    <div class="liquidGlass-effect"></div>
                    <div class="liquidGlass-tint"></div>
                    <div class="liquidGlass-shine"></div>
                    <div class="liquidGlass-text p-6 lg:p-10 flex flex-col justify-between">
                        <!-- Hero 内容 -->
                    </div>
                </div>
            </div>

            <!-- 更多卡片... -->

        </div>
    </div>
    <svg style="display: none">
        <filter id="glass-distortion">
            <feTurbulence type="fractalNoise" baseFrequency="0.01 0.01" numOctaves="1" seed="5"/>
            <feGaussianBlur stdDeviation="3" result="softMap"/>
            <feDisplacementMap in="SourceGraphic" in2="softMap" scale="150" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
    </svg>
</body>
</html>
```

---

## 执行规则

### 规则 1：4 层结构不可省略
每张卡片必须包含 wrapper + effect + tint + shine + text 共 5 个元素。缺少任何一层都会破坏玻璃效果。

### 规则 2：SVG 滤镜必须存在
`<svg style="display: none">` 中的 `#glass-distortion` 滤镜是折射效果的来源，必须放在 HTML 中。整个页面只需一份。

### 规则 3：深色背景是前提
液态玻璃效果依赖深色背景。背景越暗越丰富（如城市夜景、星空），玻璃折射效果越好。禁止使用浅色或白色背景。

### 规则 4：所有文字为白色系
body 必须有 `text-white antialiased`。副文字用 `text-gray-300`，弱化文字用 `text-white/60`。

### 规则 5：字体只用 Inter
所有文字必须使用 Inter 字体族。不得替换为其他字体。

### 规则 6：根据卡片数量选择布局
- 1-2 张卡片 → 模式 A（居中）
- 3 张以上卡片 → 模式 B（Bento Grid）

### 规则 7：根据内容量调节 SVG scale
- 展示型（少量大文字）→ scale 40~80
- 信息型（多卡片、多内容）→ scale 100~200

### 规则 8：保持 hover 弹性动画
`cubic-bezier(0.175, 0.885, 0.32, 1.5)` 是液态玻璃的标志性交互感。不得替换为 linear 或 ease。

### 规则 9：响应式适配
- 使用 Tailwind 响应式前缀：`sm:`, `md:`, `lg:`
- Bento Grid 在移动端所有卡片 `col-span-12`（全宽堆叠）
- 字号使用响应式：`text-3xl lg:text-4xl`

### 规则 10：单文件输出
生成的 HTML 必须是完整的独立文件，所有 CSS 写在 `<style>` 标签内，所有 JS 写在 `<script>` 标签内。不依赖外部文件（CDN 除外）。

---

## 对话流程

### 第一步：确认需求
向用户确认：
1. 页面用途？（展示卡片/Dashboard/Landing Page/其他）
2. 需要几张卡片？（决定使用居中布局还是 Bento Grid）
3. 每张卡片的内容？（标题、副标题、图标、数据等）
4. 是否有背景图偏好？（默认使用深色渐变）
5. 折射强度偏好？（轻柔/中等/强烈，默认中等）

### 第二步：生成 HTML
根据需求选择模板，填充内容，输出完整的单文件 HTML。

### 第三步：确认效果
建议用户在浏览器中打开预览，根据反馈微调：
- 折射太强/太弱 → 调整 SVG scale
- 玻璃太白/太透 → 调整 tint 层 opacity
- 文字看不清 → 增加 text-shadow 或调整 tint opacity
- 背景不合适 → 更换背景图或渐变

---

## 常见问题

### Q: 滤镜效果不显示？
A: 确认 SVG `<filter id="glass-distortion">` 存在且 `.liquidGlass-effect` 的 `filter: url(#glass-distortion)` 正确引用。

### Q: 背景图加载慢？
A: 使用 Unsplash 时添加 `?q=80&w=2071&auto=format&fit=crop` 优化。或改用 CSS 渐变作为兜底。

### Q: 移动端效果差？
A: 移动端可降低 SVG scale（如 40），减少 backdrop-filter blur 以优化性能。

### Q: 想要彩色玻璃而非白色？
A: 修改 `.liquidGlass-tint` 的 background 为 `rgba(R, G, B, 0.1)` 实现彩色色调。
