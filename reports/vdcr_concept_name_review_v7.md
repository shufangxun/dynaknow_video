# VDCR v1 Concept Name Review v7

Date: 2026-06-06

## Updated Verdict

这轮 review 后，我建议把 v1 的概念名分成三层：

1. **主 benchmark 概念**：名字本身编码机制、相位、传播、失稳、反馈、反应、转运或生态策略。
2. **strict gate 概念**：名字可以成立，但视频必须证明时序必要性，且不能靠单帧、场景、物种或来源标题猜中。
3. **extension / stress slice**：术语成立，但容易把 VDCR 叙事拉向动作识别、赛事战术识别、仪器识别或长时标地貌解释，不进入 v1 主统计。

核心边界保持不变：

> VDCR 不是识别“视频中发生了什么动作/事件”，而是识别“这个连续动力学过程在专家知识体系中叫什么”。

## Pool Update

`data/vdcr_concept_pool_v1.csv` 已按这轮 review 重建。

| Pool tier | Count | Meaning |
|---|---:|---|
| `main_pool` | 47 | 优先生产池。 |
| `strict_gate` | 145 | 可作为候选，但每条视频必须人工 gate。 |
| `extension` | 37 | 不进入 v1 主目标。 |
| `stress_slice` | 16 | 只做小比例压力切片，不计主 benchmark 分布。 |

## Reasonable Names

这些名字最符合 VDCR 主故事，可以作为主生产方向。

| Domain | 合理概念类型 | 代表概念 |
|---|---|---|
| 自然物理规律 | 流体不稳定性、涡动力学、界面断裂、非线性刚体/颗粒过程 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Saffman-Taylor Viscous Fingering`, `Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect` |
| 物质变化机制 | 振荡反应、自组织沉淀、枝晶/晶体生长、相分离、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Liesegang Ring Formation`, `Dendritic Crystal Growth`, `Spinodal Decomposition`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | 植物趋性/感性、细胞转运、细胞骨架、显微信号波、机制化生态策略 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `C-Start Escape Response`, `Metachronal Wave Locomotion`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | 风暴旋转/出流、密度流、河流改道、熔岩流变、机制化雪崩/泥石流 | `Supercell Mesocyclone Rotation`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `River Avulsion`, `Debris-Flow Surge Propagation`, `Slab Avalanche Release` |

## Names That Need Downgrade

这些不是完全错误，但不应作为 v1 主池补量。

| Concept | New handling | Reason |
|---|---|---|
| `Anguilliform Undulation` | `extension` | 虽然是正式游动模式，但太接近“鱼/蛇在波状摆动”的普通动物运动识别。除非未来做受控 locomotion-family contrast set，否则不进主池。 |
| `Medusan Bell-Contraction Jet Propulsion` | `strict_gate` | 可以成立，但必须看到伞体收缩、排水、反冲推进序列；不能只收“水母在游”。 |
| `Murmuration` | `strict_gate` | 是专有集群行为名，但单帧鸟群轮廓有外观捷径；必须看到群体形状波和协同转向。 |
| `Ice Cliff Calving` | `strict_gate` | 容易变成灾害事件识别；必须看到裂缝/失稳/崩解/入水时序。 |
| `Tornadogenesis` | `strict_gate` | 只收生成过程；成熟龙卷静帧不合格。 |
| `Downburst / Microburst Outflow` | `strict_gate` | 必须看到下沉气流触地后的径向扩散或雨幕外流边界。 |
| `Benedict Positive Reducing-Sugar Reaction` | `strict_gate` | 容易依赖试剂身份和文字；必须看到加热后的颜色/沉淀演化且无文本泄漏。 |
| `Coffee-Ring Formation` | `strict_gate` | 最终环形沉积有静态捷径；必须显示蒸发诱导输运/沉积前沿。 |

## Names To Keep Out Of v1 Main Benchmark

| Group | Concepts | Decision |
|---|---|---|
| 人体专项动作 | `Axel Jump`, `Salchow Jump`, `Yurchenko Vault`, `Ippon Seoi Nage`, `Eskimo Roll / Kayak Roll`, `Carving Turn` 等 | 术语成立，但 v1 主统计不使用；最多作为 `stress_slice`。当前样本里的 `Eskimo Roll / Kayak Roll` 应视为压力切片，不计主集。 |
| 球类个人技巧 | `Elastico / Flip Flap`, `Marseille Turn / Roulette`, `Cruyff Turn`, `Rainbow Flick` | 从 v1 主目标移出。即使有专名，也太容易被审稿人认为是 sport action recognition。 |
| 球类战术序列 | `Spain Action`, `Elevator Screen`, `Hammer Action`, `Floppy Action`, `Iverson Cut`, `UCLA Cut`, `Ram Screen`, `Spain Back Screen` | 从 v1 主目标移出。它们更像战术视频理解/比赛语境识别，不适合支撑 video-native scientific knowledge。 |
| 临床运动体征与步态 | 全部 | 删除/延期。隐私、同意与伦理风险高，不适合当前数据构建。 |
| 人造系统与操作 | 全部 | 仍延期为工程垂直 benchmark。 |

## Practical Sampling Rule

后续采样按这个顺序执行：

1. 优先从 `main_pool` 找视频。
2. 主池视频不够时，只从 `strict_gate` 中选“视频本身能证明机制”的条目。
3. `extension` 不补主集数量。
4. `stress_slice` 单独统计，不能和主 benchmark 混算。
5. 所有通过样本必须去重到 concept level，不能用同一个概念的不同视频重复凑数。

## Implementation Note

This review is reflected in `scripts/build_vdcr_concept_pool.py` and the rebuilt `data/vdcr_concept_pool_v1.csv`.
