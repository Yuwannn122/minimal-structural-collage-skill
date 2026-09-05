# 极简结构拼贴｜通用 Prompt

这份提示词可直接交给支持参考图 / 图像编辑的 Agent 或 AI。它复刻的是“上半原始实拍 + 下半抽象纸本关系构成”的版式，不是把照片改画成写实插画。

默认包含一则真实排版的两行英文小字。若要无字版，在提示词末尾追加：“文字模式改为无文字，不生成任何字母、符号或伪文字。”

## 一次生成版（直接复制）

```text
请以我上传的照片作为唯一内容参考，制作一张高级、安静、克制的“极简结构拼贴”成品。

【输出与版式】
- 最终画布必须是纵向 2:3，建议 1024×1536 px。
- 在 50% 高度处横向分为上下两部分，约 1:1；分界干净、自然、无厚边框。
- 上半是原始实拍照片，下半是与照片呼应的高留白抽象纸本结构构成。

【上半：最高优先级，保留源像素】
- 必须使用上传原图本身，只允许 EXIF 方向纠正、等比缩放和裁切。
- 不得重新生成、重绘、美颜、磨皮、锐化、HDR、降噪、换脸或调色；不得改变人物五官、身体、手臂、手指、物体及空间比例。
- 不得拉伸；不得用镜像或复制边缘补宽。
- 构图顺序：①不破坏主体的 4:3 安全裁切；②若会丢失必要肢体或完整物件，只扩展外围背景，并把原始主体 / 原始中央照片区域无羽化覆盖回去；③背景不适合扩展时，将完整原图等比置于同款暖象牙纸色上。
- 人像至少保留能解释姿态的肩线 / 手臂；不要为了脸更大而让身体比例失衡。
- 若系统无法真正保留原照片像素，把上半当作待替换占位区，不要擅自美化主体；把生成能力集中在下半。

【下半：抽象关系，不复刻物体】
- 暖象牙色哑光纤维纸，保持 60–75% 连续而安静的留白。
- 先提炼关系：重心位置、主方向轴、面积比例、层叠遮挡、负形、色彩节奏。完整物件轮廓、完整人物、五官和包装文字都不是默认锚点。
- 用三级尺度组织：一个大的负形 / 未闭合空框；3–6 个中尺度矩形、弧形或网点块；1–3 个微小点、短线或印记。
- 必须保留一个明显的空框、缺口或未完成形，避免所有线索闭合成一件完整物体。
- 只有必要时保留一个微型具象线索，约占下半宽度 8–12%；它只是记忆碎片，不是主角。
- 使用少量断裂炭笔线、干刷、丝网印刷颗粒、轻微套色错位和克制纸片；避免写实体积、连续明暗和照片描边。
- 全图只用 4–6 种低饱和颜色：暖象牙、炭黑、驼棕，以及从原图抽取的一个强调色；强调色只出现 1–2 处。
- 构成群组约占下半宽度 32–55%、高度 28–58%，不要铺满。
- 若下半脱离上图后仍像一幅完整的相机、碗、花、购物袋或人物插画，说明太具象，必须重做。

【近景人像去写实门槛】
- 即使原图是大脸自拍，下半也要主动缩成小型胸像、半身符号或断裂剪影，周围留足空白。
- 只保留发量块面、脸朝向、姿态轴、手臂方向和 1–2 个标志性配件。
- 皮肤全部或大面积留成纸色，只用极少断裂线提示结构。
- 禁止完整眼睛、虹膜、睫毛、眼妆、鼻部塑形、唇部高光、写实肤色明暗、毛孔和照片级五官相似度。
- 第一眼若仍是“大脸肖像”而不是“负形 + 姿态 + 留白”，必须重做。

【题材关系翻译】
- 食物：用椭圆边界、堆叠色块、流动线和疏密节奏暗示容器—内容物—餐具方向，不画完整碗筷。
- 花卉：用放射方向、绿白面积和深色负形暗示植物，只留一个不完整纸白花瓣缺口，不画完整花朵。
- 日常物件：提取倾斜轴、矩形叠压、重量和色彩节奏；可用一个 8–12% 宽的微型物件印记，不画大号完整物体。
- 室内 / 场景：一个大负形框配 3–6 个正交模块，只表达空间分区和遮挡，不把杂物逐件图标化。

【英文小字：默认必须有】
- 先生成无字底图，再用真实字体在下半留白处排一则很小的两行英文短句，共 5–10 个词。
- 语气含蓄、安静，与场景有情绪关联但不直白命名物体；若我提供文案，逐字使用。
- 使用经典小号衬线或打字机感字体，常规字重，不用大标题、粗体或全大写。
- 不要让图像模型伪造字；无法保证拼写时必须留白，后期再排真实文字。

【审美目标】
高级编辑设计、现代东方留白、温暖、克制、手工但干净。上下媒介形成反差，同时通过重心、方向、负形、强调色和视觉重量彼此呼应。

【严格排除】
禁止写实插画、完整物体插画、大脸肖像、动漫、Q 版、儿童绘本、厚重水彩、油画、3D、赛博霓虹、纯白数码背景、强烈复古污渍、密集描线、满版 scrapbook、厚边框、大段文字、Logo、水印、账号、日期、社交媒体 UI、额外人物或物体、重复肢体、错误手指、伪文字，以及对上半照片的任何 AI“优化”。

输出一张完成度高的单幅成品，不要输出九宫格、过程图、mockup 或多个版本。
```

## 最可靠的两步版

扩散式模型通常会重绘整张画面。需要严格保留人物、食物或物体质感时，优先把生成与合成拆开。

### 第一步：只生成 4:3 下半构成

```text
根据我上传的照片，生成一幅独立的 4:3 横向“极简抽象纸本结构构成”，之后会放在一张 2:3 海报的下半部分。

暖象牙色纤维纸，60–75% 连续留白。不要画照片中的完整主体；先把它翻译成重心位置、主方向轴、面积比例、层叠遮挡、负形和色彩节奏。用一个大的负形 / 未闭合空框、3–6 个中尺度几何或网点块、1–3 个微小印记组织画面。只有必要时保留一个约占画面宽度 8–12% 的微型具象线索。使用 4–6 种低饱和颜色，从原图抽取一个强调色，只出现 1–2 次。加入少量断裂炭笔线、干刷、丝网颗粒与轻微套色错位，避免写实明暗与体积塑形。

若原图是近景人像，下半主动降尺度成小型胸像 / 半身符号或断裂剪影；皮肤留成纸色，不画完整眼睛、虹膜、睫毛、鼻部塑形、唇部高光或写实肤色。若第一眼像大脸肖像，重做。

不要生成任何文字、字母、Logo 或符号；为后期真实英文小字保留安静空白。

禁止完整物件插画、写实人像、照片滤镜、动漫、Q 版、厚水彩、3D、密集描线、强烈做旧、满版装饰、伪文字、水印、UI、额外物件和错误人体结构。只输出一张 4:3 下半构成，不输出完整海报。
```

### 第二步：确定性拼接与真实排字

在任意图片编辑器中建立 `1024 × 1536` 画布：

1. 将原照片安全地等比裁切成 `1024 × 768`，放在 `y=0–768`；只缩放和裁切，不加滤镜。
2. 若安全裁切会丢失必要肢体或完整物件，只扩展外围背景，再把原始主体 / 原始中央照片区域覆盖回去；背景不适合扩展时，用暖象牙纸色空边容纳完整原图。
3. 将 4:3 下半构成完整缩放到 `1024 × 768` 后放在 `y=768–1536`，不要裁掉留白。
4. 导出无字 PNG，并先验证尺寸、上半来源与下半来源。
5. 除非用户明确要求无字，用真实衬线字体在下半留白处排入一则两行英文短句，共 5–10 个词。
6. 排字后再次验证尺寸与上半来源；此时不要再做下半逐像素来源比较。

使用本 Skill 附带脚本时，把 `<python>` 和 `<skill-root>` 替换为实际路径：

```text
<python> "<skill-root>/scripts/assemble_collage.py" "original.jpg" "lower-panel.png" "base.png" --artwork-mode panel --focus-x 0.5 --focus-y 0.5
<python> "<skill-root>/scripts/verify_collage.py" "base.png" --original "original.jpg" --artwork "lower-panel.png" --artwork-mode panel --focus-x 0.5 --focus-y 0.5
<python> "<skill-root>/scripts/add_caption.py" "base.png" "final.png" --line1 "First line" --line2 "second line."
<python> "<skill-root>/scripts/verify_collage.py" "final.png" --original "original.jpg" --focus-x 0.5 --focus-y 0.5
```

## English version

```text
Use the uploaded photograph as the sole reference and create one refined “minimal structural collage.”

OUTPUT: exact 1024×1536 portrait canvas (2:3), divided at 50% into two clean edge-to-edge panels.

TOP — SOURCE PIXELS ONLY: use the original photograph itself. Only correct EXIF orientation, resize proportionally, and crop. Do not regenerate, repaint, beautify, retouch, sharpen, denoise, grade, distort, mirror, or duplicate edges. Preserve every face, body, limb, hand, object, and spatial proportion. Use a safe 4:3 crop; if that would remove an essential limb or object, outpaint background only and paste the untouched original subject / central photo area back; otherwise contain the full photo on matching warm-ivory paper. Never enlarge a face at the expense of body proportion.

BOTTOM — ABSTRACT RELATIONSHIPS, NOT AN OBJECT ILLUSTRATION: warm ivory matte fibrous paper with 60–75% continuous negative space. Translate the source into visual weight, directional axes, area ratios, overlap, negative shapes, and color rhythm. Build three scales: one large open or incomplete frame; 3–6 medium geometric/halftone blocks; 1–3 tiny marks. Keep at least one conspicuous gap or unfinished contour. A single literal clue is optional and must remain a tiny 8–12%-wide memory token, never the hero. Use broken charcoal lines, dry brush, screen-print grain, slight registration errors, and 4–6 muted colors with one sampled accent used once or twice. If the lower panel still reads as a complete camera, bowl, flower, shopping bag, or figure when viewed alone, it is too literal and must be redesigned.

CLOSE-UP PORTRAITS: reduce the face to a small bust, half-body symbol, or interrupted silhouette regardless of the source crop. Preserve only hair mass, face direction, pose axis, arm direction, and 1–2 signature accessories. Leave skin as paper. No fully drawn eyes, irises, lashes, nose modeling, glossy lips, skin shading, pores, or photoreal likeness. If the first impression is “large portrait” instead of “negative space and structure,” redo it.

CAPTION — INCLUDED BY DEFAULT: create the art text-free, then typeset one tiny, correctly spelled, two-line English phrase of 5–10 words in a real classic serif/typewriter-like font. Place it in open space. Omit only when explicitly requested.

ART DIRECTION: premium editorial composition, modern East Asian negative space, warm, restrained, handmade but clean. The panels should echo through weight, direction, negative shape, accent color, and rhythm—not through literal duplication.

AVOID: photoreal illustration, complete object drawings, large-face portraits, anime, chibi, children’s illustration, heavy watercolor, oil paint, 3D, neon, bright-white digital backgrounds, aggressive stains, dense outlines, full-page scrapbook decoration, large typography, fake text, logos, watermarks, UI, duplicated limbs or objects, altered anatomy, and any AI enhancement of the top photo.

Return one finished image only—no grid, process sheet, mockup, or variations.
```
