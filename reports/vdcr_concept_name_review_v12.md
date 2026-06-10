# VDCR Concept Name Review v12

Date: 2026-06-06

## 总体结论

当前 248 个概念不应该被理解为“最终主 benchmark 答案全集”，而应该理解为一个分层候选池。按 VDCR 的边界重新审查后，整体方向是合理的：主线已经从普通动作/事件识别，收紧到“由时序结构定义的专有动态概念”。

但仍有一个关键约束需要继续执行：**名字本身必须承载动态机制，而不是只把可见事件命名得更专业。** 例如 `Slab Avalanche Release` 比 `Snow Avalanche Release` 更合理；`Capillary-Driven Droplet Coalescence` 比 `Droplet Coalescence` 更像知识点；`Bistable Snap-Trap Closure` 比 `Venus Flytrap Closure` 更符合 VDCR。

## 当前分层判断

| 层级 | 数量 | 结论 |
|---|---:|---|
| `core_main` | 52 | 可作为 v1 主集骨架。名字一般已编码清晰的时序机制。 |
| `strict_main_candidate` | 142 | 可以继续检索，但必须逐条过视频 gate。公开视频很容易出现静态捷径、标题泄漏或来源依赖。 |
| `stress_slice` | 16 | 只建议作为附录或 stress set，不计入主 benchmark 主统计。 |
| `extension` | 15 | 名字有科学性，但公开视频证据、标注依赖或领域垂直性较强，暂不主推。 |
| `defer_or_remove` | 23 | 不进入 v1。主要是球类战术/技巧、长时标地貌、强仪器语境概念。 |

## 一级 Domain 合理性

| 一级 Domain | 判断 | 处理建议 |
|---|---|---|
| 自然物理规律 | 最稳。大量概念天然由时序动力学定义。 | 主生产优先。注意把液滴、波动、振动类名字机制化。 |
| 物质变化机制 | 很稳。反应、相变、结晶、燃烧、流变都适合 VDCR。 | 严格防标题/字幕/实验标签泄漏；视频必须能看到变化过程。 |
| 生命过程机制 | 可用，但最容易混入动作识别。 | 植物、细胞、微生物、发育过程优先；动物生态策略只收有正式策略名和阶段结构的概念。 |
| 地球环境过程 | 可用，属于 video knowledge，不是普通 understanding。 | 名字要避免“事件化”；优先选失稳、前沿、流、旋转、迁移等机制词。 |
| 人体专项动作与运动技术 | 可以保留为 stress slice。 | 不进主统计。必须跨多运动体系，避免变成体育动作 benchmark。 |
| 球类专项动作与战术序列 | 不适合 v1 主线。 | 继续 `defer_or_remove`。即使有专名，也容易退化为 play/action recognition。 |

## 强保留名字

这些名字非常符合 VDCR，因为单帧通常不足以定性，且标签本身就是机制/过程：

| Domain | 强保留示例 |
|---|---|
| 自然物理规律 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Rayleigh-Plateau Breakup`, `Faraday Waves`, `Gyroscopic Precession`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect`, `Vortex Ring Formation`, `Cavitation Bubble Growth and Collapse` |
| 物质变化机制 | `Shear Thickening`, `Weissenberg Rod-Climbing Effect`, `Dendritic Crystal Growth`, `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Chemical Garden Growth`, `Liesegang Ring Formation`, `Spinodal Decomposition`, `Thin-Film Dewetting` |
| 生命过程机制 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Nyctinasty`, `Cytoplasmic Streaming`, `Mitotic Chromosome Segregation`, `Calcium Wave Propagation`, `Microtubule Dynamic Instability`, `Bacterial Chemotaxis`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | `Downburst / Microburst Outflow`, `Supercell Mesocyclone Rotation`, `Tornadogenesis`, `Meander Neck Cutoff`, `Sediment Saltation`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Slab Avalanche Release`, `Tidal Bore`, `Gully Headcut Retreat` |

## 需要机制化改名的名字

这些不是错误，但当前表述偏“现象名”或“过程名”，建议最终答案使用更机制化的推荐名。

| 当前名 | 推荐答案名 | 理由 |
|---|---|---|
| `Droplet Coalescence` | `Capillary-Driven Droplet Coalescence` | 强调表面张力/毛细驱动，而不是“两个水滴合并”。 |
| `Droplet Rebound` | `Inertia-Capillarity Droplet Rebound` | 强调惯性和毛细回缩竞争。 |
| `Droplet Impact Spreading` | `Inertia-Driven Droplet Impact Spreading` | 避免退化为“水滴撞上去摊开”。 |
| `Standing Wave Formation` | `Standing-Wave Mode Formation` | 强调驻波模态，而非静态波纹图案。 |
| `Crystal Nucleation` | `Crystal Nucleation-and-Growth Dynamics` | 单独“成核”常常不可见，需连同生长动力学。 |
| `Precipitation Front Propagation` | `Reaction-Precipitation Front Propagation` | 强调反应-扩散/沉淀前沿，而非普通沉淀。 |
| `Flame Front Propagation` | `Reactive Flame-Front Propagation` | 强调反应前沿推进。 |
| `Diffusion Flame` | `Diffusion-Limited Flame Stabilization` | 单帧火焰形态可能可猜，需体现扩散受限和稳定结构。 |
| `Gel Swelling` | `Solvent-Driven Gel Swelling Dynamics` | 强调溶剂进入导致体积变化。 |
| `Stomatal Opening and Closing` | `Guard-Cell Turgor-Driven Stomatal Aperture Dynamics` | 强调保卫细胞膨压机制。 |
| `Ciliary Beating` | `Coordinated Ciliary Beating Dynamics` | 强调节律和相位协调。 |
| `Lamellipodium Extension` | `Actin-Driven Lamellipodium Extension` | 强调肌动蛋白驱动。 |
| `Filopodium Protrusion` | `Actin-Driven Filopodium Protrusion` | 强调肌动蛋白束探伸。 |
| `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` | 强调浮力驱动，而不是烟往上飘。 |
| `Dune Slip-Face Avalanche` | `Dune Slip-Face Grain Avalanche` | 强调颗粒雪崩，而不是沙丘表面滑动事件。 |

## 仍需严格 gate 的边界名字

| 名字 | 可用性 | 必须看到的证据 |
|---|---|---|
| `Magnus Effect` | 可用，但严格 | 旋转物体、弯曲轨迹、流体偏转/升力后果三者至少要清楚。只看到香蕉球不够。 |
| `Medusan Bell-Contraction Jet Propulsion` | 可用，但严格 | 伞体收缩、排水、反作用位移的连续序列。只看到水母游动不够。 |
| `Murmuration` | 可用，但严格 | 群体形态波、同步转向、整体流场式重组。静态鸟群不够。 |
| `Ice Cliff Calving` | 可用，但严格 | 裂缝/失稳、冰体脱离、坠落入水的连续过程。只看到冰块掉落不够。 |
| `Lava Dome Collapse` | 可用，但严格 | 穹丘失稳、崩塌、碎屑流/重力流后续。只看到火山喷烟不够。 |
| `Storm Surge Propagation` | 可用，但严格 | 风暴驱动水位/海水入侵的空间推进。普通洪水画面不够。 |
| `Barchan Dune Migration` | 可用，但严格 | 新月形沙丘整体迁移或沙粒越脊输运。静态沙丘形态不够。 |
| `Pyrocumulus Development` | 可用，但严格 | 火源热羽流触发的云体垂直发展。普通云发展不够。 |

## 建议从主集排除或只保留附录

| 组别/名字 | 建议 | 原因 |
|---|---|---|
| 球类技巧和战术序列 | v1 删除或延期 | 太容易变成体育动作/战术识别，不支撑“科学视频知识”的主叙事。 |
| `Elastico`, `Marseille Turn`, `Cruyff Turn`, `Rainbow Flick` | 删除/延期 | 有专名，但知识门槛主要是球类动作记忆。 |
| `Spain Action`, `Elevator Screen`, `Hammer Action`, `Iverson Cut` 等 | 删除/延期 | 更像比赛战术识别，强依赖队形语境。 |
| 人体专项运动技术 | stress slice only | 有正式命名体系，但主线会偏体育动作。可小比例保留，用于证明边界。 |
| 临床运动体征与步态 | v1 不收 | 患者隐私、同意、伦理和数据来源风险高。 |
| `Anguilliform Undulation` | 暂放 extension | 是正式术语，但容易被看成“鱼在摆动”。需要强对照和机制说明。 |
| `Peristaltic Locomotion`, `Sidewinding Locomotion` | 不收 | 太接近“看着蠕动/侧向移动”的普通动作识别。 |
| `Glacier Creep`, `Basal Sliding` | 不收主集 | 长时标且公开视频通常无法单凭画面判断机制。 |
| `Sea-Cliff Retreat`, `Spit Progradation` | 不收主集 | 多依赖航拍对比/地图/时间跨度说明，来源文本权重过大。 |
| `Fault Rupture Propagation` | 延期 | 往往需要仪器、模拟或标注图像才能准确识别。 |

## 对“视频知识”边界的判定

一个名字是否合理，不看它是否“高大上”，而看它是否满足以下四点：

1. **命名稳定**：在学科、工程、生态行为或正式技术体系中有稳定英文名/中文名。
2. **时序唯一性**：单帧不足以唯一判断，必须看阶段顺序、轨迹、传播、振荡、失稳或形态演化。
3. **机制承载**：答案名能指向机制或策略，不只是把事件命名为一个 noun phrase。
4. **视觉可验证**：公开视频本身能支持概念，网页文字只能 double-check，不能替视频补知识。

## 最终建议

当前概念池可以继续用于生产，但 v1 主 benchmark 应只使用两类：

1. `core_main`：直接进入主生产优先队列。
2. `strict_main_candidate`：只有视频证据强、无文本泄漏、无静态捷径时才进入。

`stress_slice`、`extension`、`defer_or_remove` 不应进入主统计。尤其是人体专项和球类术语，要保持克制：VDCR 可以包含“专有动态动作概念”，但 v1 的主叙事仍应由物理、化学/材料、生物细胞/植物/生态策略、地球环境机制支撑。
