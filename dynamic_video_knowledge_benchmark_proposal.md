# DynaKnow-Video: 面向动态视频知识识别的 Benchmark Proposal

## 0. 一句话定位

**DynaKnow-Video** 评估多模态模型是否能从视频中的动态过程识别出其承载的知识点，例如物理规律、化学现象、生物过程、材料变化、因果机制或操作原理。

执行包已放在 `dynaknow_video/`，包含数据获取表、taxonomy、标注规范、样本 schema、prompt 模板和 JSONL validator。

这里的重点不是先给示范视频、再做新情境泛化，而是更基础的问题：

> 这个视频本身展示了什么动态知识？

例如，一个静态苹果图片只能支持“这是苹果”“苹果在桌上”等图像知识；但一个苹果从树上落到地面的视频，可以支持“物体在重力作用下向下加速运动”这样的动态知识。DynaKnow-Video 的 v1 目标就是识别这类必须通过观察时间过程才能得到的知识点。

## 1. Motivation

现有 video QA 里很多所谓 knowledge question 仍可能退化为：

- **静态视觉知识**：看一帧就能识别实体、场景、仪器、图表或文本。
- **字幕知识**：视频只是讲解载体，模型读 transcript 即可回答。
- **常识/百科知识**：题目本身可由语言先验回答，视频不是必要证据。
- **普通事件理解**：模型只需复述发生了什么，不需要识别背后的知识点。

DynaKnow-Video 希望隔离出一类更具体的能力：**dynamic video knowledge recognition**。它要求模型从运动、变化、对照、因果链或过程演化中识别知识，而不是只描述表面事件。

例子：

- 视频：苹果从高处掉到地面。  
  动态知识：重力导致物体向地面运动，物体下落过程体现加速度。
- 视频：小车碰撞后两个小车一起移动。  
  动态知识：动量传递或非弹性碰撞。
- 视频：冰块受热融化成水。  
  动态知识：固体吸热发生相变。
- 视频：植物幼苗持续向光源方向弯曲。  
  动态知识：植物向光性。
- 视频：金属片受热后弯曲。  
  动态知识：材料热膨胀差异导致形变。

这些知识点不是单帧中“有苹果”“有小车”“有冰块”这样的静态事实，而是由动态过程本身承载。

## 2. Related Work Survey and Gap

### WorldVQA

WorldVQA 关注 atomic visual world knowledge，主要评估模型能否识别图像中的长尾实体、地点、物种、文物、品牌等。它处理的是静态图像世界知识，不评估视频动态过程诱导出的知识。

### Video-MME

Video-MME 是综合视频理解评测，覆盖多种视频长度、领域和多模态输入。它包含 temporal/contextual dynamics，但目标是 full-spectrum video understanding，并没有把“知识点必须由动态过程识别”作为样本准入条件。

### Video-MME-v2

Video-MME-v2 已经显式强调 dynamic evolution、causal relations、temporal understanding 和 video-based knowledge acquisition。DynaKnow-Video 不应声称首次评估动态视频能力。更准确的差异是：Video-MME-v2 是综合视频能力分层评测；DynaKnow-Video 则专门构造“动态知识点识别”任务，并对每个样本验证其不能由 answer-only、单帧、稀疏帧、字幕或常识 shortcut 解决。

### Video-MMMU

Video-MMMU 明确评估从多学科专业视频中获取知识，并采用 Perception、Comprehension、Adaptation 三阶段设计。它更偏 educational/professional videos，知识经常由课程讲解、幻灯片、公式、图表或教师语言承载。DynaKnow-Video v1 更偏 demonstration/phenomenon videos，知识由可见动态过程承载，例如掉落、碰撞、融化、扩散、弯曲、发芽、振动等。

### Demo-ICL-Bench

Demo-ICL-Bench 评估从示范视频中学习 procedural knowledge 并应用到目标任务。它更接近 in-context learning 和 procedure/task transfer。DynaKnow-Video v1 不要求模型先学习一个任务再迁移，而是识别单个视频片段中展示的动态知识点。

### VideoZeroBench

VideoZeroBench 强调长视频 QA 的 spatio-temporal evidence verification，要求模型定位答案对应的时空证据。DynaKnow-Video 可以借鉴 evidence span 标注，但核心不同：它评估的是模型是否能把动态证据上升为知识点，而不是仅回答和定位视频事实。

### 核心 Gap

更稳妥的 claim：

> Existing video benchmarks evaluate temporal reasoning, video QA, or knowledge acquisition, but they do not isolate dynamic knowledge point recognition as a first-class task with sample-level shortcut verification.

DynaKnow-Video 的贡献是把“动态知识点”作为样本基本单位：

- 每个视频必须展示一个明确知识点。
- 知识点必须依赖时间过程，而不是静态画面。
- 问题必须要求识别知识点，而不是复述事件。
- 样本必须通过 answer-only、single-frame、sparse-frame、subtitle-only 和 prior-only 过滤。

## 3. Task Definition

### 3.1 Dynamic Video Knowledge Recognition

给定视频 `V` 和问题 `q`，模型需要输出视频中动态过程所展示的知识点 `k`。

形式化：

```text
Input: video V + question q + answer choices C
Output: knowledge point k in C
```

主问题模板：

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

或中文：

```text
这个视频中的动态过程最能体现哪个知识点？
```

关键约束：

- `k` 不是对象名称或场景标签。
- `k` 不是视频字幕中直接说出的句子。
- `k` 不是题干和选项即可推出的常识答案。
- `k` 必须由有序状态变化、运动轨迹、因果反馈或过程演化支持。

### 3.2 什么算动态视频知识

一个样本满足 dynamic video knowledge，当且仅当：

- **Temporal evidence required**：至少需要观察两个以上时间点的状态变化，或连续运动过程。
- **Static frame insufficient**：任意单帧、首帧、尾帧或最佳关键帧都不足以唯一确定知识点。
- **Knowledge-level answer**：答案是规律、现象、机制、原则或过程知识，而不是“发生了什么事件”。
- **Shortcut resistant**：answer-only、subtitle-only、prior-only 表现接近随机或显著低于 full-video。

### 3.3 不是当前 v1 主任务的内容

为了让 v1 足够清晰，以下内容先不作为主任务：

- 不做示范视频后的新情境泛化。
- 不要求模型生成完整解释。
- 不把普通事件问答作为主榜。
- 不把时空定位作为主指标，但可以作为辅助标注。

这些可以作为 v2 扩展：先识别动态知识点，再测试泛化、解释和证据定位。

## 4. Knowledge Taxonomy

### 4.1 Physics and Mechanics

关注运动、力、能量、碰撞、振动、流体等。

例子：

- 物体下落：重力作用、加速度。
- 小车碰撞：动量传递、能量损失、弹性/非弹性碰撞。
- 摆锤往复：周期运动、重力势能和动能转换。
- 斜面滑块：重力分解、摩擦影响运动。
- 浮沉实验：浮力和密度关系。

### 4.2 Chemistry and Material Change

关注反应、相变、扩散、沉淀、燃烧、颜色变化、材料变形。

例子：

- 冰块融化：固体吸热发生熔化相变。
- 碘钟反应：反应进程达到终点后出现延迟的突发颜色变化。
- 过硫酸盐碘钟反应：硫代硫酸盐耗尽后，生成的碘与淀粉形成深蓝色络合物。
- Benedict 试剂检测：还原糖在加热条件下使试剂发生可见颜色变化。
- 酸和碳酸盐反应：生成二氧化碳气泡。
- 可溶性离子混合：形成难溶盐沉淀。
- 盐/糖溶解扩散：溶解物从高浓度区域向低浓度区域扩散。
- 金属片受热弯曲：材料热膨胀差异导致形变。

化学类样本不能只写成“某些反应会变色”“某些反应会产生沉淀”“某些混合物会冒泡”。这些是观察结果类别，不是足够具体的知识点。若无法从视频证据和非泄漏上下文确定具体反应类、材料系统或机制，该候选不进入 final QA。

### 4.3 Biology and Life Processes

关注生长、趋性、运动响应、生态互动、人体/动物动作机制。

例子：

- 幼苗向光弯曲：向光性。
- 水从根部运输到叶片：蒸腾/毛细作用相关过程。
- 昆虫趋光移动：趋光行为。
- 心脏模型泵送液体：循环系统泵送机制。
- 肌肉牵拉带动关节：肌肉收缩和杠杆作用。

### 4.4 Everyday Causal Mechanisms

关注日常生活中可观察的因果机制。

例子：

- 海绵吸水膨胀：多孔结构吸水。
- 热空气推动纸片上升：热空气上升/对流。
- 湿纸受热卷曲：水分蒸发和材料收缩。
- 磁铁靠近铁粉形成图案：磁场影响铁磁材料。
- 轮胎打滑后减速：摩擦不足导致抓地力下降。

### 4.5 Procedural and Operational Principles

关注操作过程体现的原则，但 v1 只识别原则，不测试迁移。

例子：

- 先固定再切割：约束减少运动误差。
- 逐步加热避免破裂：热应力控制。
- 先搅拌再加粉减少结块：分散和混合原则。
- 先排气再密封：压力平衡。

## 5. Question Design

### 5.1 主问题：Knowledge Point Identification

主任务采用多选题，问题尽量保持通用，避免泄漏答案。

推荐题干：

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

选项示例：

- A. Gravity causes unsupported objects to accelerate downward.
- B. Friction converts mechanical motion into heat.
- C. Magnetic fields align ferromagnetic particles.
- D. Evaporation removes heat from a surface.

如果视频是苹果下落，正确答案是 A。题干不提“苹果”“下落”“重力”等关键词，降低 answer-only 推理空间。

### 5.2 辅助问题：Dynamic Evidence Probe

可选辅助题，用于确认模型确实看到动态证据，但不作为主榜核心。

示例：

```text
Which observed change is most important for identifying the knowledge point?
```

这类题帮助分析模型失败原因，但不能取代知识点识别任务。

### 5.3 题目不能泄漏答案

必须避免：

- 题干出现知识点关键词，例如“这个下落过程体现了什么重力规律？”
- 选项只有一个与视频对象语义相关，其他明显无关。
- 正确答案比错误答案更长、更具体或更学术。
- 错误选项是明显荒谬项。
- 候选答案可以通过常识排除到唯一。

推荐做法：

- 题干统一化，只说“dynamic process”。
- 所有选项都使用同一抽象层级，例如都为物理规律，或都为生物现象。
- 同一视频配多个 hard negative，来自相近领域和相似视觉过程。
- 对同一组选项构造多个视频，让不同视频对应不同正确答案。

## 6. Dataset Construction

### Step 1: Video Selection

优先选择短而清晰的 demonstration/phenomenon videos：

- 长度建议 5 到 60 秒。
- 视频中有清楚的起始状态、动态变化、结束状态。
- 画面不依赖字幕讲解。
- 知识点可以由普通高中/本科基础科学或日常机制解释。
- 单帧不足以唯一识别知识点。

视频 source 和本地存储约定：

- 评测使用的视频全部落到本地工程目录中，release 样本只暴露 `local_media`，例如 `media/raw/dynaknow_000001.webm` 或 `media/segments/dynaknow_000088.mp4`。
- 原始下载文件放在 `media/raw/`；解码困难时的转码备份放在 `media/raw_transcoded/`；为去掉片头、片尾、字幕、旁白或 title-card 泄漏而裁剪出的片段放在 `media/segments/`，默认去音频。
- `source_url`、direct media URL、source title、license、author、download note 等 provenance 只保存在 manifest 中，例如 `data/draft_media_manifest*.csv`、`data/pilot_manifest*.csv` 和 `release/<version>/*manifest.csv`。这些字段不进入模型评测 JSONL，避免 source title/file name 泄漏答案。

source 优先级：

1. Wikimedia Commons 的真实世界公开视频，目前作为主 source，因为 file page、direct media URL 和 license metadata 相对稳定。
2. 政府或公共机构的 public-domain/open-license 视频，例如 NASA、NOAA、USGS、NIST 等，但前提是画面本身展示 dynamic knowledge，而不是讲解材料。
3. 大学/OER demonstration library，要求有明确复用条款和可追溯下载地址。
4. Internet Archive、Pixabay、Pexels 等开放 archive/stock 平台只作为补充，且必须是真实世界动态、license 清楚、无解释性字幕/OCR。

主 split 不混入 simulation、animation、lecture、slide、paper supplementary video 或纯讲解视频；这些可以作为单独 diagnostic split，而不是作为 dynamic video knowledge 主评测。

字幕/OCR 泄漏约束：

- 默认偏好无字幕、无 overlay、无 board/slide text、无 title-card、无 end-card 的视频。
- 只要 OCR/subtitle/visible text 直接出现目标知识点或近义词，例如 `gravity`、`surface tension`、`siphon`、`density`、`CO2`、`phototropism`，样本直接 reject 或必须裁剪成 clean segment 后重新审核。
- 即使 source title/file name 泄漏，也不能出现在评测输入中；如果视频帧自身无泄漏，可以保留 provenance 到 manifest，但 evaluation JSONL 必须隐藏 source metadata。
- 可接受的文字只限于与答案无关的 incidental text，例如无语义水印、时间戳、品牌标记；任何能缩小候选答案空间的文字进入 manual review。

### Step 2: Knowledge Point Annotation

每个视频标注一个或多个候选知识点：

```json
{
  "knowledge_point": "Gravity causes unsupported objects to accelerate downward.",
  "knowledge_category": "physics_mechanics",
  "dynamic_evidence": [
    {"start_sec": 0.2, "end_sec": 1.7, "description": "Object moves from high position to lower position with increasing speed."}
  ],
  "static_insufficient_reason": "A single frame cannot show downward acceleration or the direction of motion."
}
```

标注原则：

- 知识点应是可复用的规律/现象/机制。
- 知识点必须具体到可以和相近机制区分；必要时写出反应类、材料系统、条件或变量关系。
- 不写成视频事件描述，例如“苹果掉到地上”。
- 不写成过度宽泛概念，例如“物理学”。
- 不写成泛化观察结果，例如“某些化学反应会变色”“某些反应会生成沉淀”“某些过程导致运动”。
- 不写成需要外部不可见信息才能判断的结论。

Specificity gate：

```text
如果不能用一个明确、可复用、可区分的知识点描述视频动态过程，就不生成 QA。
```

对于化学/材料变化，final 样本必须能落到具体机制或反应类，例如 iodine-clock endpoint、Benedict reducing-sugar test、acid-carbonate CO2 generation、insoluble-salt precipitation、melting/freezing/evaporation/crystallization、thermal expansion mismatch。只观察到“变色/冒泡/变浑浊”但无法命名机制时，保留为 revise 或直接 reject。

Source-grounded annotation：

- 标注者可以使用 source page summary、Commons file description、category、provenance notes 来确定具体知识点。
- 这些信息只用于标注和 manifest，不进入模型评测输入。
- source summary 给出的机制必须有视频中的可见动态锚点，例如延迟后突然变蓝、加热后颜色转变、混合后沉淀出现。
- 如果 source summary 描述的机制在视频中没有可见证据，不能因为网页写了就接受样本。
- 对化学样本尤其如此：视频像素常常只能显示“变色”，但 source summary 可以把它 grounding 到 iodine-clock、Benedict test、acid-carbonate reaction 等具体知识点；评测 JSONL 仍隐藏 source_url/title/summary。

### Step 3: Hard Negative Construction

每道题至少 3 个错误选项，优先来自：

- 同一学科相近知识点。
- 相似视觉动态但不同机制。
- 常见误解。
- 可由静态帧误判的知识点。

例子：苹果下落视频的 hard negatives 不应是“光合作用”“板块运动”这类无关项，而应是：

- inertia keeps an object moving at constant velocity
- friction slows objects sliding on a surface
- elastic force restores a deformed object
- gravity causes unsupported objects to accelerate downward

### Step 4: Shortcut Filtering

每个样本必须跑以下过滤：

- **Specificity audit**：检查知识点是否为过宽 catch-all label。
- **Answer-only**：只给题干和选项，不给视频。
- **Prior-only**：不给视频，但给一个极简场景名，例如“an object moves”。
- **Single-frame**：只给首帧、尾帧、中心帧、人工挑选关键帧。
- **Sparse-frame**：只给少量无序帧或低帧率抽帧。
- **Subtitle-only**：只给 ASR/transcript。
- **Static caption-only**：只给静态图像 caption。

通过标准：

- answer-only 强模型准确率接近随机。
- single-frame / best-frame 明显低于 full-video。
- subtitle-only 不能直接得到答案。
- human full-video 准确率高，human single-frame 准确率显著低。

### Step 5: Human Review

人工审核问题：

- 这个视频是否真的承载一个知识点？
- 这个知识点是否必须观察动态过程？
- 题干和选项是否泄漏答案？
- 错误选项是否足够 plausible？
- 单帧是否已经足够回答？
- 字幕或旁白是否直接说出答案？

## 7. Evaluation Protocol

### 7.1 输入设置

对每个模型评估：

- Full video
- Single best frame
- Sparse frames
- Static captions
- Subtitle only
- Answer only
- Full video + subtitles

### 7.2 指标

主指标：

- **Knowledge Recognition Accuracy**：识别动态知识点的准确率。
- **Dynamic Necessity Gap**：full-video accuracy 减去 best-static accuracy。
- **Leakage Gap**：full-video accuracy 减去 answer-only accuracy。

辅助指标：

- Category-wise accuracy
- Hard-negative confusion matrix
- Evidence probe accuracy
- Human full-video vs single-frame gap

### 7.3 样本级准入指标

一个样本进入 benchmark 前，应满足：

```text
Human_full_video correct
AND Human_single_frame uncertain or wrong
AND Model_answer_only not reliably correct
AND Model_subtitle_only not reliably correct
```

这样 benchmark 的核心不是“题难”，而是“题确实需要动态视频知识”。

## 8. Example Items

### Example 1: Falling Object

视频：一个苹果从树枝上脱落，向地面运动，并最终落地。

主问题：

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

选项：

- A. Unsupported objects accelerate downward under gravity.
- B. Objects moving on rough surfaces slow down due to friction.
- C. A deformed elastic object returns to its original shape.
- D. Magnetic fields can align ferromagnetic particles.

答案：A

为什么是动态知识：

- 单帧只能看到苹果、树或地面。
- 首帧看不到落地，尾帧看不到运动方向。
- 视频过程展示了位置随时间向下变化，支持重力导致下落这一知识点。

### Example 2: Melting Ice

视频：冰块放在热平面上，逐渐变成液态水。

选项：

- A. A solid can absorb heat and undergo melting into a liquid.
- B. A liquid can evaporate when exposed to airflow.
- C. A gas can condense into liquid droplets on a cold surface.
- D. A dissolved solid can crystallize as solvent evaporates.

答案：A

动态依赖：

- 静态冰块或水滴都不足以说明相变方向。
- 必须看到冰块逐渐变小、水逐渐增多。

### Example 3: Seedling Phototropism

视频：幼苗在延时视频中逐渐向单侧光源弯曲。

选项：

- A. A plant shoot can grow toward a light source.
- B. Water moves upward through a stem by transpiration pull.
- C. Roots grow downward in response to gravity.
- D. Leaves lose water vapor through stomata.

答案：A

动态依赖：

- 单帧只显示幼苗形状，不能证明“逐渐朝光源方向改变”。
- 视频中的连续弯曲过程才支持向光性。

## 9. V1 and V2 Roadmap

### V1: Dynamic Knowledge Recognition

核心目标：

- 判断模型能否从视频动态过程识别知识点。
- 建立动态知识 taxonomy。
- 建立 sample-level shortcut filtering。
- 得到可靠的 full-video vs static shortcut gap。

这是最基础、最清晰、最容易做干净的版本。

### V2: Explanation and Grounding

在 v1 基础上增加：

- 要求模型指出支持知识点的 temporal evidence。
- 要求模型解释为什么不是其他选项。
- 引入 VideoZeroBench 式 evidence verification。

### V3: Knowledge Generalization

再进一步测试：

- 看完视频后，把知识点应用到新情境。
- 做 prediction、intervention、counterfactual。
- 这相当于从 recognition 走向 acquisition and transfer。

## 10. Expected Contributions

1. **Conceptual contribution**：提出 dynamic video knowledge recognition，区分动态图像过程知识、静态视觉知识、字幕知识和普通事件理解。
2. **Dataset contribution**：构建以动态知识点为基本单位的视频 benchmark。
3. **Evaluation contribution**：引入 answer-only、single-frame、sparse-frame、subtitle-only 等样本级过滤。
4. **Diagnostic contribution**：通过 Dynamic Necessity Gap 衡量模型是否真的利用了视频动态。

## 11. Paper Abstract Draft

Existing video benchmarks increasingly evaluate temporal reasoning and video-based knowledge acquisition, yet many knowledge-oriented questions can still be answered from static frames, subtitles, answer-option priors, or general world knowledge. We introduce DynaKnow-Video, a benchmark for dynamic video knowledge recognition. Each sample consists of a video whose temporal process demonstrates a specific knowledge point, such as a physical law, biological response, chemical transition, material behavior, or everyday causal mechanism. The main task asks models to identify the knowledge point best demonstrated by the dynamic process, rather than merely describe events in the video. To ensure that each sample truly requires dynamic video understanding, we validate it against answer-only, single-frame, sparse-frame, subtitle-only, and static-caption shortcuts. We further propose Dynamic Necessity Gap, measuring the performance advantage of full-video input over the strongest static or textual shortcut. DynaKnow-Video provides a focused foundation for studying whether multimodal models can recognize knowledge that exists in motion and change, not in isolated frames.

## 12. References for Positioning

- Video-MMMU: https://arxiv.org/abs/2501.13826
- Video-MME: https://video-mme.github.io/home_page.html
- Video-MME-v2: https://github.com/MME-Benchmarks/Video-MME-v2
- WorldVQA: https://www.kimi.com/blog/worldvqa
- Demo-ICL: https://arxiv.org/abs/2602.08439
- VideoZeroBench: https://arxiv.org/abs/2604.01569
