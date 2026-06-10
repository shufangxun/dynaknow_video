# VDCR v1 Concept Name Review v8

Date: 2026-06-06

## Verdict

当前这版“视频动态专有名字”总体方向是合理的，但不能把 246 个概念等价使用。真正适合 v1 主 benchmark 的，是名字本身编码了动态机制、相位序列、传播/失稳/反馈/转运/反应过程的概念。

生产时应按三层使用：

| Tier | 用法 | 结论 |
|---|---|---|
| `main_pool` | 主生产池 | 可以优先采样，但仍要逐条过视频 gate。 |
| `strict_gate` | 条件生产池 | 名字可以成立，但必须用视频本身证明动态过程；不能靠标题、来源页或场景先验。 |
| `extension` / `stress_slice` | 非主集 | 不计入 v1 主统计；最多用于压力切片或未来扩展。 |

一句话边界：

> VDCR 的答案不是“看到的动作/事件”，而是“这个连续时序过程在专家知识体系里的专有动态概念名”。

## Strong Names

这些名字最符合 VDCR 的 video-native knowledge 叙事。

| Domain | 推荐保留类型 | 代表概念 |
|---|---|---|
| 自然物理规律 | 流体不稳定性、界面断裂、非线性振动、刚体/颗粒动力学 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Faraday Waves`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect` |
| 物质变化机制 | 振荡反应、自组织沉淀、枝晶/晶体生长、相分离、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Liesegang Ring Formation`, `Dendritic Crystal Growth`, `Spinodal Decomposition`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | 植物趋性/感性、细胞转运、细胞骨架动态、显微信号波、机制化生态策略 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `C-Start Escape Response`, `Metachronal Wave Locomotion`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | 风暴旋转/外流、密度流、河流改道、熔岩流变、机制化雪崩/泥石流 | `Supercell Mesocyclone Rotation`, `Downburst / Microburst Outflow`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `River Avulsion`, `Debris-Flow Surge Propagation`, `Slab Avalanche Release` |

## Names That Are Reasonable But Need Strict Gate

这些概念名本身可以保留，但如果视频证据不够，很容易退化成普通视频理解。

| Concept | Risk | Production rule |
|---|---|---|
| `Medusan Bell-Contraction Jet Propulsion` | 容易被看成“水母在游”。 | 必须看到伞体收缩、排水/反冲、位移推进的完整节律。 |
| `Murmuration` | 单帧鸟群轮廓有外观捷径。 | 必须看到群体形状波、同步转向或集群流动。 |
| `Benedict Positive Reducing-Sugar Reaction` | 容易依赖试剂标签或来源文本。 | 只有在无文字泄漏、且加热后颜色/沉淀演化非常清楚时才收；否则 reject。 |
| `Diffusion Flame` | 容易变成“看到火焰”。 | 必须是能显示非预混燃料/氧化剂界面、火焰建立或稳定过程的实验视频。 |
| `Convective Smoke Plume Rise` | 容易变成“烟在上升”。 | 必须显示热浮力烟羽的连续生成、上升和扩展，不能只是一团烟。 |
| `Ice Cliff Calving` | 容易变成“冰掉下来”。 | 必须看到裂缝/失稳/崩解/坠落入水序列。 |
| `Plunging Breaker` | 单帧卷浪可能给捷径。 | 必须看到波峰陡化、前倾、卷入、破碎的阶段序列。 |
| `Barchan Dune Migration` | 静态新月形沙丘外观很强。 | 只收真正迁移 time-lapse；航拍/飞越静态沙丘 reject。 |
| `Marangoni-Driven Flow` | 视觉上可能只是普通液体流动。 | 必须有源文本 double-check，但视频本身也要显示界面/表面张力梯度驱动的定向输运；只靠标题 reject。 |
| `Endocytosis` / `Exocytosis` | 名字宽，但专业性强。 | 必须是显微视频中可见膜内陷、囊泡形成/融合、颗粒释放等阶段；ASL、科普图、静态显微图 reject。 |

## Names To Tighten

这些不是错，但表述还可以更像“知识点/机制名”，不应停留在动作描述。

| Current | Better name | Reason |
|---|---|---|
| `Stomatal Opening and Closing` | `Guard-Cell Turgor-Driven Stomatal Aperture Dynamics` | “气孔开闭”太像描述；新名字强调保卫细胞膨压驱动的孔径变化。 |
| `Medusan Bell-Contraction Jet Propulsion` | `Medusan Jet Propulsion by Bell Contraction` | 语义更自然，突出喷射推进机制。 |
| `Embryonic Cleavage Division Sequence` | `Early Embryonic Cleavage Sequence` | 更像标准发育生物学术语，避免“division sequence”累赘。 |
| `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` | 更明确是浮力/对流机制，不是普通烟雾上升。 |
| `Dune Slip-Face Avalanche` | `Dune Slip-Face Grain Avalanche` | 更明确是颗粒沿雪崩面运动，不是一般沙丘事件。 |

## Names That Should Stay Out Of v1 Main

| Group | Decision | Reason |
|---|---|---|
| 临床运动体征与步态 | 删除/延期 | 患者隐私、同意和伦理成本高。 |
| 球类技巧与战术 | 不进主集 | 即使有专名，也容易被认为是 sport action/play recognition。 |
| 人体专项运动术语 | 只做 `stress_slice` | 可以测试“专有动态动作概念”，但不能支撑主 benchmark 叙事。 |
| `Anguilliform Undulation` | `extension` | 正式术语成立，但太接近普通动物运动识别；未来可做受控 locomotion contrast set。 |
| `Iceberg Rollover`, `Snow Avalanche Release`, `Glacier Flow` | 已移出或替换 | 这些更像可见事件/宽泛过程，机制承载不足。 |
| 人造系统与操作 | 延期 | 术语很垂直，适合工程子 benchmark，不适合当前 v1 主故事。 |

## Production Implication

后续构造数据时，我建议执行下面的硬规则：

1. 主集优先从 `main_pool` 出样本。
2. `strict_gate` 可以补量，但每条必须写清楚：视频动态证据、来源 double-check、为什么单帧不够、为什么不是泛动作/泛事件。
3. `extension` 和 `stress_slice` 不用于凑主集数量。
4. 现有已通过样本中，如果 answer 落在 `Diffusion Flame`, `Convective Smoke Plume Rise`, `Marangoni-Driven Flow`, `Medusan Bell-Contraction Jet Propulsion`, `Murmuration`, `Endocytosis`, `Exocytosis` 这类边界概念，需要在 dashboard 里保留 gate reason，不能只显示 answer。
5. 概念级去重继续保持；同一概念不能用多个视频重复凑数。
