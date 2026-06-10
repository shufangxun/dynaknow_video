# VDCR Concept Name Review v11

Date: 2026-06-06

## Verdict

当前 VDCR 术语池可以继续作为检索候选池，但主 benchmark 不能等价使用全部名字。主集答案名必须是由时序动力学结构定义的专家概念，而不是普通视频动作、事件或对象名称。

我建议后续生产继续执行当前三层策略：

| Layer | Use | Rule |
|---|---|---|
| `core_main` | v1 主生产池 | 名字本身已经编码动态机制，且随机单帧不能唯一判别。 |
| `strict_main_candidate` | 严格 gate 后可进主集 | 名字成立，但公开视频容易有静态捷径、标题泄漏、来源依赖或普通动作化风险。 |
| `stress_slice` / `extension` / `defer_or_remove` | 不进主统计 | 只用于边界分析、未来扩展或直接删除。 |

## Domain-Level Judgment

| 一级 Domain | 结论 | 主要风险 |
|---|---|---|
| 自然物理规律 | 最稳，适合作为主集骨架。 | 部分基础概念如 `Damped Oscillation`、`Coherent Wave Interference` 需要证明不是单帧图样识别。 |
| 物质变化机制 | 很稳，尤其是反应动力学、相分离、枝晶、非牛顿流变。 | 化学实验容易被标题/字幕/网页泄漏答案；视频必须自己支持概念。 |
| 生命过程机制 | 可用，但最需要克制。植物、细胞、发育过程适合主集；动物生态策略只收有命名策略和阶段结构的概念。 | 动物运动、人体专项、球类技巧容易退化成 action recognition。 |
| 地球环境过程 | 可以作为 video knowledge，但必须机制化命名。 | 长时标冰川/海岸地貌过程经常依赖标注、地图或来源文本。 |
| 人造系统与操作 | v1 继续延期。 | 太垂直，容易变成工程故障/操作识别 vertical benchmark。 |

## Strong Main Names

这些名字本身合理，适合优先生产：

| Domain | Examples |
|---|---|
| 自然物理规律 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Rayleigh-Plateau Breakup`, `Faraday Waves`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect`, `Cavitation Bubble Growth and Collapse`, `Vortex Ring Formation` |
| 物质变化机制 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Dendritic Crystal Growth`, `Spinodal Decomposition`, `Liesegang Ring Formation`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Nyctinasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `C-Start Escape Response`, `Metachronal Wave Locomotion`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | `Supercell Mesocyclone Rotation`, `Downburst / Microburst Outflow`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `Slab Avalanche Release`, `Dune Slip-Face Grain Avalanche`, `Gully Headcut Retreat` |

## Names That Need Mechanism Wording

这些概念不是错，但直接作为答案会偏表象，推荐使用机制化答案名：

| Current | Recommended |
|---|---|
| `Droplet Coalescence` | `Capillary-Driven Droplet Coalescence` |
| `Droplet Rebound` | `Inertia-Capillarity Droplet Rebound` |
| `Droplet Impact Spreading` | `Inertia-Driven Droplet Impact Spreading` |
| `Standing Wave Formation` | `Standing-Wave Mode Formation` |
| `Crystal Nucleation` | `Crystal Nucleation-and-Growth Dynamics` |
| `Precipitation Front Propagation` | `Reaction-Precipitation Front Propagation` |
| `Flame Front Propagation` | `Reactive Flame-Front Propagation` |
| `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` |
| `Dune Slip-Face Avalanche` | `Dune Slip-Face Grain Avalanche` |
| `Stomatal Opening and Closing` | `Guard-Cell Turgor-Driven Stomatal Aperture Dynamics` |
| `Ciliary Beating` | `Coordinated Ciliary Beating Dynamics` |
| `Lamellipodium Extension` | `Actin-Driven Lamellipodium Extension` |
| `Filopodium Protrusion` | `Actin-Driven Filopodium Protrusion` |

## Borderline But Usable With Hard Gate

| Concept | Keep? | Required evidence |
|---|---|---|
| `Magnus Effect` | Yes, strict | 必须看到旋转、弯曲轨迹和升力/偏转后果，不能只是球路。 |
| `Capillary Rise / Wicking` | Yes, strict | 必须看到湿润前沿沿毛细通道或多孔介质连续上升。 |
| `Medusan Jet Propulsion by Bell Contraction` | Yes, strict | 必须看到伞体收缩-排水/反作用-位移的序列；只看到水母游动不够。 |
| `Murmuration` | Yes, strict | 必须看到群体形态波、同步转向或流场式重组；静态鸟群不够。 |
| `Ice Cliff Calving` | Yes, strict | 必须看到裂缝/失稳、冰崖脱离、坠落入水的连续序列。 |
| `Plunging Breaker` | Yes, strict | 必须看到波峰陡化、翻卷、卷入空气和破碎，而不是普通海浪。 |
| `Fire-Whirl Vortex Formation` | Yes, strict | 必须看到火焰/烟羽形成旋转柱状涡，而不是普通火灾。 |

## Downgrade Or Remove

| Group / Concept | Decision | Reason |
|---|---|---|
| 球类专项动作与战术序列 | `defer_or_remove` | 即使有专名，也太容易变成 sports action/play recognition，不适合 v1 story。 |
| `Trivela`, `Dribble Handoff`, `Step-back Jumper`, `Pick and Roll`, `Pick and Pop` | remove | 用户已明确不希望保留；它们不需要足够强的动态专有知识。 |
| `Elastico / Flip Flap`, `Marseille Turn`, `Cruyff Turn`, `Rainbow Flick` | `defer_or_remove` | 有动作专名，但主线会偏足球技巧识别。 |
| 篮球战术如 `Spain Action`, `Elevator Screen`, `Hammer Action` | `defer_or_remove` | 需要比赛语境和队形规则，主线不是科学动态知识。 |
| 人体专项运动术语 | `stress_slice` only | 有正式技术体系，但只能做小比例边界测试，不能进入主统计。 |
| 临床运动体征与步态 | remove/defer | 患者隐私、同意和伦理成本过高。 |
| 普通动物运动如 `Peristaltic Locomotion`, `Sidewinding Locomotion` | remove/defer | 过于接近“看见蠕动/侧向移动”的动作识别，除非有研究级强对照视频。 |
| `Glacier Creep`, `Basal Sliding`, `Sea-Cliff Retreat`, `Spit Progradation` | remove/defer | 长时标过程，视频通常靠标注或来源文本才能判断。 |
| `Iceberg Rollover`, `Snow Avalanche Release`, `Glacier Flow`, `Glacier Calving` | remove/rewrite | 名字太像事件；需替换为 `Ice Cliff Calving`、`Slab Avalanche Release` 等机制化子型。 |

## Production Policy

1. 主集只允许 `core_main` 和严格通过视频 gate 的 `strict_main_candidate`。
2. `stress_slice` 不计入主集 domain 配额，只用于附录或 stress evaluation。
3. 每个答案概念主集只保留一条，做概念级去重。
4. 视频证据必须先成立；网页只能 double-check 概念名，不能替视频补知识。
5. 如果一个名字需要通过来源标题、字幕、讲解、论文图注才能识别，则拒绝。
6. 对动物/人体/体育相关条目，默认拒绝，除非它具有正式命名体系、阶段结构、机制解释和强静帧不可判别性。

## Bottom Line

当前术语体系已经可以支撑继续生产，但生产时要把“专有名词”再收紧成“时序机制专有名词”。最适合主集的不是所有有名字的动作，而是名字本身已经编码动态结构的概念：不稳定性、前沿传播、相变/成核、生长/粗化、趋性/感性、细胞运输、群体策略、地貌/灾害过程的失稳和推进。
