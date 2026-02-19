---
name: liquid-glass-ui
description: |
  液态玻璃（Liquid Glass）风格 HTML 页面生成器。
  对标 Apple iOS 26 / WWDC25 Liquid Glass 设计语言，
  通过 SVG 滤镜边缘折射 + 方向性高光 + 多层毛玻璃叠加 + 深色沉浸背景，
  创造出具有透镜感、光泽感、深度感的现代 UI。

  适用场景：产品展示页、个人主页、Dashboard、单词卡片、Keynote 风格展示、
  App Landing Page、作品集等一切需要高级视觉质感的单页 HTML。

  触发条件（满足任一即触发）：
  - 用户要求制作"液态玻璃"、"毛玻璃"、"glassmorphism"风格页面
  - 用户提到"Apple 风格"、"WWDC 风格"、"iOS 风格"UI
  - 用户要求制作有"折射效果"、"玻璃质感"的 HTML
  - 用户说"做一个好看的展示页面"且未指定其他风格
  - 用户要求 Bento Grid 布局 + 玻璃卡片

  触发词：liquid glass、液态玻璃、毛玻璃、玻璃风格、glassmorphism、Apple风格、
  WWDC风格、iOS 26、Bento Grid、玻璃卡片、折射效果、glass UI
version: 1.1.1
---

# Liquid Glass UI — 液态玻璃风格 HTML 生成器

生成对标 Apple iOS 26 Liquid Glass 设计语言的液态玻璃风格单页 HTML。
核心特征：SVG 边缘集中折射、方向性 Specular 高光、brightness 增益透镜感、弹性交互动画、入场/鼠标追踪微动效。

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
    <div class="liquidGlass-shine"></div>    <!-- Layer 2: 方向性光泽层 -->
    <div class="liquidGlass-text">           <!-- Layer 3: 内容层 -->
        <!-- 实际内容放在这里 -->
    </div>
</div>
```

### CSS 定义（必须完整包含）

```css
/* --- 液态玻璃卡片系统 v1.1 --- */

/* 容器：包裹所有层，提供圆角、阴影、边缘微光、hover 动画 */
.liquidGlass-wrapper {
    position: relative;
    display: flex;
    overflow: hidden;
    padding: 0.6rem;
    border-radius: 2rem;
    cursor: pointer;
    box-shadow:
        0 6px 6px rgba(0, 0, 0, 0.2),
        0 0 20px rgba(0, 0, 0, 0.1),
        0 0 1px rgba(255, 255, 255, 0.3);  /* [v1.1] 边缘微光：增加玻璃浮起感 */
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.5);
}

/* Hover：弹性放大 + 增强阴影 + 微光扩散 */
.liquidGlass-wrapper:hover {
    transform: scale(1.03);
    box-shadow:
        0 10px 20px rgba(0, 0, 0, 0.25),
        0 0 40px rgba(0, 0, 0, 0.15),
        0 0 2px rgba(255, 255, 255, 0.4);  /* [v1.1] hover 时微光增强 */
}

/* Layer 0 - 扭曲折射层：backdrop-filter 模糊 + brightness 增益 + SVG 滤镜扭曲 */
.liquidGlass-effect {
    position: absolute;
    z-index: 0;
    inset: 0;
    backdrop-filter: blur(3px) brightness(1.4);  /* [v1.1] brightness 增益：模拟真实玻璃透镜增亮 */
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

/* [v1.1] Layer 2 - 方向性光泽层：模拟定向光源，左上亮右下暗 */
.liquidGlass-shine {
    position: absolute;
    z-index: 2;
    inset: 0;
    border-radius: inherit;
    /* 方向性高光：左上角明亮，右下角柔暗，模拟 Apple 的 Specular Rim */
    box-shadow:
        inset 1px 1px 2px 0 rgba(255, 255, 255, 0.6),   /* 左上高光：更亮更宽 */
        inset -1px -1px 2px 0 rgba(255, 255, 255, 0.08); /* 右下暗光：极弱 */
    /* 左上角光斑：模拟定向光源照射 */
    background: radial-gradient(
        ellipse 80% 60% at 15% 15%,
        rgba(255, 255, 255, 0.12) 0%,
        rgba(255, 255, 255, 0) 70%
    );
}

/* Layer 3 - 内容层：承载文字、图标等实际内容 */
.liquidGlass-text {
    position: relative;
    z-index: 3;
    width: 100%;
    height: 100%;
}

/* [v1.1] 入场动画：卡片从模糊透明渐入 */
@keyframes glassAppear {
    0% {
        opacity: 0;
        transform: translateY(20px) scale(0.97);
        filter: blur(8px);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
        filter: blur(0);
    }
}
.liquidGlass-wrapper {
    animation: glassAppear 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}
/* 多卡片时错开入场 */
.liquidGlass-wrapper:nth-child(1) { animation-delay: 0s; }
.liquidGlass-wrapper:nth-child(2) { animation-delay: 0.1s; }
.liquidGlass-wrapper:nth-child(3) { animation-delay: 0.2s; }
.liquidGlass-wrapper:nth-child(4) { animation-delay: 0.3s; }
.liquidGlass-wrapper:nth-child(5) { animation-delay: 0.4s; }
.liquidGlass-wrapper:nth-child(6) { animation-delay: 0.5s; }
```

### 各层参数可调范围

| 层 | 属性 | 默认值 | 可调范围 | 说明 |
|----|------|--------|----------|------|
| wrapper | border-radius | 2rem | 1rem ~ 3rem | 圆角越大越柔和 |
| wrapper | padding | 0.6rem | 0.4rem ~ 1rem | 内边距 |
| wrapper | 边缘微光 | 0.3 opacity | 0.2 ~ 0.5 | 玻璃浮起感强度 |
| wrapper:hover | scale | 1.03 | 1.02 ~ 1.08 | 悬停放大比例 |
| effect | blur | 3px | 2px ~ 8px | 背景模糊强度 |
| effect | brightness | 1.4 | 1.2 ~ 1.6 | 透镜增亮效果 |
| tint | background opacity | 0.12 | 0.08 ~ 0.20 | 白色覆盖层透明度 |
| shine | 左上高光 | 0.6 | 0.4 ~ 0.7 | 高光侧亮度 |
| shine | 右下暗光 | 0.08 | 0.05 ~ 0.15 | 暗光侧亮度 |
| shine | 光斑 opacity | 0.12 | 0.08 ~ 0.18 | 左上角光斑强度 |

---

## SVG 扭曲滤镜

此 SVG 必须放在 `</body>` 前，是液态玻璃折射效果的来源。

### [v1.1] 推荐：内联径向位移贴图（边缘集中折射）

Apple iOS 26 的关键特征：**边缘折射强，中心区域清晰**。使用内联 SVG 径向渐变作为位移贴图实现：

```html
<svg style="display: none">
    <!-- [v1.1] 径向位移贴图：中心中性色(不扭曲)，边缘红绿渐变(产生折射) -->
    <defs>
        <radialGradient id="edge-refraction-map" cx="50%" cy="50%" r="50%">
            <stop offset="0%"  stop-color="rgb(128,128,0)" />   <!-- 中心：不位移 -->
            <stop offset="60%" stop-color="rgb(128,128,0)" />   <!-- 60%范围内保持清晰 -->
            <stop offset="85%" stop-color="rgb(160,100,0)" />   <!-- 边缘开始折射 -->
            <stop offset="100%" stop-color="rgb(200,60,0)" />   <!-- 最边缘：最强折射 -->
        </radialGradient>
    </defs>

    <filter id="glass-distortion" x="-5%" y="-5%" width="110%" height="110%">
        <!-- 方案 A：使用径向位移贴图（边缘集中折射，推荐） -->
        <feImage result="dispMap" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cdefs%3E%3CradialGradient id='g' cx='50%25' cy='50%25' r='50%25'%3E%3Cstop offset='0%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='55%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='80%25' stop-color='rgb(155,105,0)'/%3E%3Cstop offset='100%25' stop-color='rgb(195,65,0)'/%3E%3C/radialGradient%3E%3C/defs%3E%3Crect width='400' height='400' fill='url(%23g)'/%3E%3C/svg%3E" />
        <feGaussianBlur in="dispMap" stdDeviation="6" result="softMap"/>
        <feDisplacementMap in="SourceGraphic" in2="softMap" scale="55" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
</svg>
```

### 备选：feTurbulence 噪声（均匀折射，兼容性更好）

如果内联 feImage 在目标浏览器不生效，回退到 feTurbulence 方案：

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
| 径向中性区 offset | 55% | 中心多大范围保持清晰，越大 = 中心越清晰 |
| 边缘折射色 | rgb(195,65,0) | 红通道越大 = 水平折射越强；绿通道越小 = 垂直折射越强 |
| stdDeviation | 6 | 位移贴图模糊度，越大过渡越柔和 |
| scale | 55 | 整体扭曲强度。30=微妙，55=中等，80+=强烈 |
| feTurbulence baseFrequency | 0.01 | 值越小扭曲块越大越柔和；值越大纹理越细碎 |

### 预设配置

**轻柔折射**（单卡展示、阅读类）：
```
径向方案：scale="30" 中性区 offset="65%"
噪声方案：baseFrequency="0.005 0.01" scale="40"
```

**中等折射**（通用推荐）：
```
径向方案：scale="55" 中性区 offset="55%"
噪声方案：baseFrequency="0.01 0.01" scale="80"
```

**强烈折射**（Bento Grid 展示、Keynote 风格）：
```
径向方案：scale="80" 中性区 offset="40%"
噪声方案：baseFrequency="0.01 0.01" scale="150-200"
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

### [v1.1.1] 超大字体（Display Typography）使用指南

超大字体（6xl ~ `text-[16rem]`）是 Apple Keynote 风格的标志，但有严格的适用边界。

**判断标准：一张卡片的核心信息能否用 1-3 个词概括？能 → 用大字体；否 → 不用。**

#### 适合使用的场景

| 场景 | 示例 | 说明 |
|------|------|------|
| 产品/品牌展示 | "M4 **Ultra**"、"vision**OS 3**" | 一张卡片只传递一个概念 |
| 数据亮点 / KPI | "**99.9**% uptime"、"**2M+** users" | 数字本身就是最重要的信息 |
| 单词/短语学习 | "**Ephemeral**"、"**Serendipity**" | 逐字阅读、细细品味 |
| 倒计时/事件预告 | "**3** days"、"**Jun 9**" | 时间紧迫感需要视觉冲击 |
| 404/状态页 | "**404**"、"**Nothing here**" | 简单直接，无其他信息竞争 |

#### 不适合使用的场景

| 场景 | 原因 |
|------|------|
| 信息密集的表单/表格 | 挤占空间，无法容纳字段 |
| 长文阅读（文章、文档） | 大字体破坏阅读节奏 |
| 多层级导航 | 层级关系无法通过字号区分 |
| 移动端小屏 | 一个词就撑满屏幕，无法扫视 |
| 同屏超过 3 个大标题 | 互相争夺注意力，全部失效 |

#### 搭配规则

- **超大字体必须搭配轻量副标题**：`text-6xl font-extrabold` + `text-lg font-light text-gray-300`
- **关键词用渐变高亮**：部分文字使用 `.text-gradient-apple` 引导视觉焦点
- **卡片内容底部对齐**：使用 `flex flex-col justify-end` 让大字压在卡片底部
- **留白即信息**：大字体卡片至少保持 40% 面积留白，不要填满

#### 字号选择参考

| 卡片类型 | 推荐字号 | 示例 |
|----------|---------|------|
| Hero 大卡片（col-span-7+） | `text-[12rem]` ~ `text-[16rem]` | 单个数字或字母 |
| 中卡片（col-span-5） | `text-6xl` ~ `text-7xl` | 2-4 个词的产品名 |
| 小卡片（col-span-3~4） | `text-4xl` ~ `text-5xl` | 产品名 + 版本号 |
| 居中单卡片 | `text-6xl` ~ `text-8xl` | 品牌名或核心词 |

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
| 高光边缘（亮侧） | 半透明白 | `rgba(255, 255, 255, 0.6)` |
| 高光边缘（暗侧） | 极弱白 | `rgba(255, 255, 255, 0.08)` |
| 边缘微光 | 半透明白 | `rgba(255, 255, 255, 0.3)` |

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

### [v1.1] 亮暗自适应色调变体

当需要支持亮色背景场景时，提供深色 tint 变体：

```css
/* 暗色 tint：用于亮色背景或需要增强文字对比度的场景 */
.liquidGlass-tint-dark {
    position: absolute;
    z-index: 1;
    inset: 0;
    background: rgba(0, 0, 0, 0.25);
    border-radius: inherit;
}

/* 自动适配：通过 CSS 媒体查询切换 */
@media (prefers-color-scheme: light) {
    .liquidGlass-tint-auto {
        background: rgba(0, 0, 0, 0.15);
    }
}
@media (prefers-color-scheme: dark) {
    .liquidGlass-tint-auto {
        background: rgba(255, 255, 255, 0.12);
    }
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
- 阴影增强 + 边缘微光扩散

### 入场动画（已内置于 CSS）

`glassAppear` 动画使卡片从模糊透明状态渐入，多卡片通过 `nth-child` 错开延迟。

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

### [v1.1] 可选：鼠标追踪光效

鼠标移动时，光斑跟随鼠标位置，模拟 Apple 的定向光源响应：

```javascript
document.querySelectorAll('.liquidGlass-wrapper').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        const shine = card.querySelector('.liquidGlass-shine');
        if (shine) {
            shine.style.background = `radial-gradient(
                ellipse 80% 60% at ${x}% ${y}%,
                rgba(255, 255, 255, 0.15) 0%,
                rgba(255, 255, 255, 0) 70%
            )`;
        }
    });
    card.addEventListener('mouseleave', () => {
        const shine = card.querySelector('.liquidGlass-shine');
        if (shine) {
            shine.style.background = `radial-gradient(
                ellipse 80% 60% at 15% 15%,
                rgba(255, 255, 255, 0.12) 0%,
                rgba(255, 255, 255, 0) 70%
            )`;
        }
    });
});
```

### [v1.1] 可选：滚动渐入动画（IntersectionObserver）

卡片进入视口时触发入场动画，适用于长页面：

```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animationPlayState = 'running';
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.liquidGlass-wrapper').forEach(card => {
    card.style.animationPlayState = 'paused';
    observer.observe(card);
});
```

### 可选：动态 SVG 噪声动画

```javascript
let frame = 0;
const turbulence = document.querySelector('#glass-distortion feTurbulence');
function animateTurbulence() {
    frame += 0.5; // 值越大抖动越快；设为 0 则静止
    if (turbulence) turbulence.setAttribute('seed', Math.floor(frame));
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
        /* 粘贴完整的液态玻璃 CSS v1.1（见上方"CSS 定义"章节） */
        .liquidGlass-wrapper { /* ... */ }
        .liquidGlass-wrapper:hover { /* ... */ }
        .liquidGlass-effect { /* ... backdrop-filter: blur(3px) brightness(1.4); ... */ }
        .liquidGlass-tint { /* ... */ }
        .liquidGlass-shine { /* ... 方向性高光 + radial-gradient 光斑 ... */ }
        .liquidGlass-text { /* ... */ }
        @keyframes glassAppear { /* ... */ }
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
    <!-- SVG 滤镜 v1.1 -->
    <svg style="display: none">
        <filter id="glass-distortion" x="-5%" y="-5%" width="110%" height="110%">
            <feImage result="dispMap" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cdefs%3E%3CradialGradient id='g' cx='50%25' cy='50%25' r='50%25'%3E%3Cstop offset='0%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='55%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='80%25' stop-color='rgb(155,105,0)'/%3E%3Cstop offset='100%25' stop-color='rgb(195,65,0)'/%3E%3C/radialGradient%3E%3C/defs%3E%3Crect width='400' height='400' fill='url(%23g)'/%3E%3C/svg%3E" />
            <feGaussianBlur in="dispMap" stdDeviation="6" result="softMap"/>
            <feDisplacementMap in="SourceGraphic" in2="softMap" scale="55" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
    </svg>
    <script>
        /* 可选：鼠标追踪光效 */
        document.querySelectorAll('.liquidGlass-wrapper').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                const shine = card.querySelector('.liquidGlass-shine');
                if (shine) {
                    shine.style.background = `radial-gradient(ellipse 80% 60% at ${x}% ${y}%, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%)`;
                }
            });
            card.addEventListener('mouseleave', () => {
                const shine = card.querySelector('.liquidGlass-shine');
                if (shine) {
                    shine.style.background = `radial-gradient(ellipse 80% 60% at 15% 15%, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%)`;
                }
            });
        });
    </script>
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
        /* 粘贴完整的液态玻璃 CSS v1.1 */
        .liquidGlass-wrapper { /* ... */ }
        /* ... 所有层的 CSS（含 v1.1 升级） ... */
        @keyframes glassAppear { /* ... */ }
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
    <!-- SVG 滤镜 v1.1（Bento Grid 用强烈折射） -->
    <svg style="display: none">
        <filter id="glass-distortion" x="-5%" y="-5%" width="110%" height="110%">
            <feImage result="dispMap" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cdefs%3E%3CradialGradient id='g' cx='50%25' cy='50%25' r='50%25'%3E%3Cstop offset='0%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='40%25' stop-color='rgb(128,128,0)'/%3E%3Cstop offset='75%25' stop-color='rgb(160,95,0)'/%3E%3Cstop offset='100%25' stop-color='rgb(200,55,0)'/%3E%3C/radialGradient%3E%3C/defs%3E%3Crect width='400' height='400' fill='url(%23g)'/%3E%3C/svg%3E" />
            <feGaussianBlur in="dispMap" stdDeviation="6" result="softMap"/>
            <feDisplacementMap in="SourceGraphic" in2="softMap" scale="80" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
    </svg>
    <script>
        /* 鼠标追踪光效 + 滚动渐入 */
        document.querySelectorAll('.liquidGlass-wrapper').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                const shine = card.querySelector('.liquidGlass-shine');
                if (shine) {
                    shine.style.background = `radial-gradient(ellipse 80% 60% at ${x}% ${y}%, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%)`;
                }
            });
            card.addEventListener('mouseleave', () => {
                const shine = card.querySelector('.liquidGlass-shine');
                if (shine) {
                    shine.style.background = `radial-gradient(ellipse 80% 60% at 15% 15%, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%)`;
                }
            });
        });
    </script>
</body>
</html>
```

---

## 设计约束（v1.1 新增）

Apple 在 iOS 26 中明确定义了 Liquid Glass 的使用边界。Web 实现同样需要遵守：

### 约束 1：不要到处使用玻璃
Liquid Glass 对**导航层**最有效（Header、Tab Bar、Sidebar、Toolbar）。内容区域应保持实底或高对比度。当所有元素都是玻璃时，什么都不突出。

### 约束 2：避免玻璃叠玻璃
不要在一个 `liquidGlass-wrapper` 内部嵌套另一个 `liquidGlass-wrapper`。多层 `backdrop-filter` 叠加会导致性能问题和视觉混乱。

### 约束 3：限制同屏玻璃卡片数量
- 居中布局：1-2 张
- Bento Grid：最多 6-8 张
- 超过此数量时，考虑将部分卡片改为半透明实底 (`bg-white/5 rounded-2xl`)

### 约束 4：背景决定效果质量
Liquid Glass 的视觉效果**完全依赖背景**。单色深背景效果最弱，丰富的暗色图片效果最好。如果背景不合适，玻璃就只是一块模糊的白色方块。

### 约束 5：文字可读性优先
效果再好也不能牺牲可读性。如果背景导致文字难以辨认：
1. 增加 `.liquidGlass-tint` 的 opacity（0.15 → 0.25）
2. 增加 `text-shadow` 强度
3. 使用 `.liquidGlass-tint-dark` 暗色垫底变体

---

## 无障碍指引（v1.1 新增）

### 对比度要求

- 主文字（白色 on 玻璃）：确保至少 **WCAG AA 4.5:1** 对比度
- 大标题（>= 18pt bold）：至少 **3:1** 对比度
- Apple 在 iOS 26 Beta 3 中因可读性问题增加了玻璃不透明度

### 减弱动效支持

```css
@media (prefers-reduced-motion: reduce) {
    .liquidGlass-wrapper {
        animation: none;
        transition: none;
    }
    .liquidGlass-wrapper:hover {
        transform: none;
    }
}
```

### 高对比度模式支持

```css
@media (prefers-contrast: high) {
    .liquidGlass-tint {
        background: rgba(0, 0, 0, 0.5); /* 大幅增强对比度 */
    }
    .liquidGlass-effect {
        backdrop-filter: blur(6px) brightness(1.1); /* 降低增亮避免刺眼 */
    }
}
```

---

## 执行规则

### 规则 1：4 层结构不可省略
每张卡片必须包含 wrapper + effect + tint + shine + text 共 5 个元素。缺少任何一层都会破坏玻璃效果。

### 规则 2：SVG 滤镜必须存在
`<svg style="display: none">` 中的 `#glass-distortion` 滤镜是折射效果的来源，必须放在 HTML 中。整个页面只需一份。优先使用 v1.1 径向位移贴图方案。

### 规则 3：深色背景是前提
液态玻璃效果依赖深色背景。背景越暗越丰富（如城市夜景、星空），玻璃折射效果越好。禁止使用浅色或白色背景（除非使用 tint-dark 变体）。

### 规则 4：所有文字为白色系
body 必须有 `text-white antialiased`。副文字用 `text-gray-300`，弱化文字用 `text-white/60`。

### 规则 5：字体只用 Inter
所有文字必须使用 Inter 字体族。不得替换为其他字体。

### 规则 6：根据卡片数量选择布局
- 1-2 张卡片 → 模式 A（居中）
- 3 张以上卡片 → 模式 B（Bento Grid）

### 规则 7：根据内容量调节折射强度
- 展示型（少量大文字）→ scale 30~55
- 信息型（多卡片、多内容）→ scale 55~80

### 规则 8：保持 hover 弹性动画
`cubic-bezier(0.175, 0.885, 0.32, 1.5)` 是液态玻璃的标志性交互感。不得替换为 linear 或 ease。

### 规则 9：响应式适配
- 使用 Tailwind 响应式前缀：`sm:`, `md:`, `lg:`
- Bento Grid 在移动端所有卡片 `col-span-12`（全宽堆叠）
- 字号使用响应式：`text-3xl lg:text-4xl`

### 规则 10：单文件输出
生成的 HTML 必须是完整的独立文件，所有 CSS 写在 `<style>` 标签内，所有 JS 写在 `<script>` 标签内。不依赖外部文件（CDN 除外）。

### 规则 11（v1.1 新增）：遵守设计约束
参照"设计约束"章节，避免玻璃叠玻璃、限制同屏数量、确保文字可读性。

### 规则 12（v1.1 新增）：高光必须有方向性
`.liquidGlass-shine` 必须使用不对称高光（左上亮，右下暗）+ 光斑 radial-gradient。禁止使用四边均匀的 inset box-shadow。

---

## 对话流程

### 第一步：确认需求
向用户确认：
1. 页面用途？（展示卡片/Dashboard/Landing Page/其他）
2. 需要几张卡片？（决定使用居中布局还是 Bento Grid）
3. 每张卡片的内容？（标题、副标题、图标、数据等）
4. 是否有背景图偏好？（默认使用深色渐变）
5. 折射强度偏好？（轻柔/中等/强烈，默认中等）
6. 是否需要鼠标追踪光效？（默认启用）

### 第二步：生成 HTML
根据需求选择模板，填充内容，输出完整的单文件 HTML。

### 第三步：确认效果
建议用户在浏览器中打开预览，根据反馈微调：
- 折射太强/太弱 → 调整 SVG scale 和中性区 offset
- 玻璃太白/太透 → 调整 tint 层 opacity
- 文字看不清 → 增加 text-shadow 或使用 tint-dark 变体
- 背景不合适 → 更换背景图或渐变
- 高光不自然 → 调整 shine 层的 radial-gradient 位置和强度

---

## 常见问题

### Q: 滤镜效果不显示？
A: 确认 SVG `<filter id="glass-distortion">` 存在且 `.liquidGlass-effect` 的 `filter: url(#glass-distortion)` 正确引用。如果用径向位移贴图方案，检查 feImage href 的 data URI 是否完整。

### Q: 背景图加载慢？
A: 使用 Unsplash 时添加 `?q=80&w=2071&auto=format&fit=crop` 优化。或改用 CSS 渐变作为兜底。

### Q: 移动端效果差？
A: 移动端可降低 SVG scale（如 30），减少 backdrop-filter blur 以优化性能。考虑在移动端禁用鼠标追踪光效（移动端无 hover）。

### Q: 想要彩色玻璃而非白色？
A: 修改 `.liquidGlass-tint` 的 background 为 `rgba(R, G, B, 0.1)` 实现彩色色调。

### Q: feImage 内联方案在某些浏览器不生效？
A: 目前 Chromium 系浏览器支持最好。Safari/Firefox 可能不支持 backdrop-filter 中的 SVG 滤镜。回退到 feTurbulence 备选方案即可。

### Q: brightness 增益让背景过曝？
A: 将 `brightness(1.4)` 降低到 `brightness(1.2)` 或 `brightness(1.1)`，尤其在背景本身较亮时。

---

## 版本历史

### v1.1.1（当前版本）
- **排版指南**：新增超大字体（Display Typography）使用指南 — 适用场景、禁区、搭配规则、字号选择参考

### v1.1.0
- **P0 方向性高光**：shine 层从均匀 inset shadow 升级为左上亮右下暗 + radial-gradient 光斑
- **P0 边缘集中折射**：新增内联径向位移贴图 SVG 方案，中心清晰、边缘折射
- **P1 brightness 增益**：effect 层 backdrop-filter 增加 `brightness(1.4)` 透镜增亮
- **P1 边缘微光**：wrapper box-shadow 增加 `0 0 1px rgba(255,255,255,0.3)` 浮起感
- **P1 设计约束**：新增"设计约束"章节，避免过度使用和玻璃叠玻璃
- **P2 入场动画**：新增 `glassAppear` keyframe + nth-child 错开延迟
- **P2 鼠标追踪光效**：新增 JS mousemove 光斑跟随
- **P2 亮暗自适应**：新增 tint-dark 变体和 prefers-color-scheme 自动切换
- **P3 无障碍指引**：新增对比度要求、prefers-reduced-motion、prefers-contrast 支持
- **P3 滚动渐入**：新增 IntersectionObserver 可选方案

### v1.0.0
- 初始版本：4 层玻璃架构、feTurbulence SVG 滤镜、两种布局模板、10 条执行规则
