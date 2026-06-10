# VDCR v1 Concept Name Review v6

Date: 2026-06-06

## Verdict

当前 4 个一级 domain 合理：自然物理规律、物质变化机制、生命过程机制、地球环境过程。问题不在一级 domain，而在部分概念名的“标签粒度”仍不够稳定：有些名字是专家机制名，有些只是专业场景里的动作/事件名。

v1 主 benchmark 建议只使用“名称本身编码动态机制或专业时序结构”的概念。体育、人类动作、动物行为、灾害事件可以保留为扩展或压力切片，但不能用来补主集数量。

核心判定：

> 合格答案名不是“视频里发生了什么”，而是“这个连续时序过程在专家知识体系中叫什么”。

## Current Pool Health

| Pool | Count | Review |
|---|---:|---|
| main_pool | 50 | 主要可用，但仍建议人工视频级 gate。 |
| strict_gate | 143 | 数量很大，不能当主池补量；必须逐条证明时序必要性和非静帧捷径。 |
| extension | 36 | 概念本身可成立，但多依赖仪器、仿真、长时标或强元数据；不建议用于 v1 主目标。 |
| stress_slice | 16 | 仅适合附录压力测试，不建议进入主 benchmark 统计。 |

## Keep As Main Direction

这些名字最符合 VDCR 的“视频专有动态知识”定位。

| Domain | Strong Name Type | Examples |
|---|---|---|
| 自然物理规律 | 不稳定性、涡动力学、界面断裂、非线性刚体/颗粒动力学 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Vortex Shedding / Karman Vortex Street`, `Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect` |
| 物质变化机制 | 振荡反应、自组织沉淀、晶体生长、相分离、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Dendritic Crystal Growth`, `Liesegang Ring Formation`, `Spinodal Decomposition`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | 细胞运输、细胞骨架、植物趋性/感性、微观动态波 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Nyctinasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `Endocytosis`, `Exocytosis` |
| 地球环境过程 | 机制化灾变、风暴旋转/出流、河流改道、火山密度流、熔岩流变 | `Supercell Mesocyclone Rotation`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `River Avulsion`, `Debris-Flow Surge Propagation`, `Slab Avalanche Release` |

## Rename Or Tighten

这些概念不是一定要删，但当前名字容易被审稿人认为是普通视频理解。建议改成更机制化、阶段化的标签。

| Current Name | Problem | Suggested Handling |
|---|---|---|
| `Fire Whirl` | 像“火柱/火旋风外观识别”。 | 改为 `Fire-Whirl Vortex Formation`，要求看到旋涡建立与维持。 |
| `Jet Propulsion Swimming` | 太宽，容易变成“水母/头足类在游”。 | 不作为主标签；拆成 `Medusan Bell-Contraction Jet Propulsion` 或 `Cephalopod Mantle-Jet Propulsion`。 |
| `Undulatory Locomotion` | 过泛，看到蛇/鱼摆动即可猜。 | 从主池移除；若保留，必须拆成正式游动模式并提供近邻负例。 |
| `Cleavage` | 名字太宽，像普通“细胞分裂”。 | 改为 `Embryonic Cleavage Division Sequence` 或只收阶段清晰显微延时。 |
| `Crown Splash` | 名字专业但静态形态捷径强。 | strict only；必须看到撞击、冠状边缘形成、回落/破碎序列。 |
| `Worthington Jet` | 可用，但需高速过程；单帧射流可能可猜。 | strict only；要求看到空腔塌缩到中心射流形成。 |
| `Droplet Coalescence`, `Droplet Rebound`, `Droplet Impact Spreading` | 是动态过程，但专家知识门槛偏低。 | 作为备用 strict，不进入优先主目标。 |
| `Benedict Positive Reducing-Sugar Reaction` | 视频可能只展示颜色变化，答案依赖试剂/样品文本。 | 高风险 strict；无清晰实验上下文和无文本泄漏时才可收。 |
| `Precipitation Front Propagation` | 过泛，容易只是“出现沉淀”。 | 改为更具体的反应-扩散/凝胶前沿系统，或 strict backup。 |
| `Diffusion Flame` | 静态火焰外观可能猜中。 | strict only；需要区分扩散火焰、预混火焰、火焰前沿传播。 |
| `Convective Smoke Plume Rise` | 容易变成“烟往上飘”。 | 需要清楚的浮力羽流卷吸/上升结构；否则降级。 |
| `Ice Cliff Calving` | 比 Glacier Calving 好，但仍像事件识别。 | strict only；必须看到裂缝、失稳、崩落、入水序列。 |
| `Tornadogenesis` | 合格但难，成熟漏斗静帧捷径强。 | 只收形成过程，不收已有龙卷外观。 |
| `Downburst / Microburst Outflow` | 容易变成暴雨/大风识别。 | 必须看到下沉气流触地后的径向扩散或雨幕扩展。 |

## Remove From v1 Main Target

这些名字可以作为未来 extension 或 stress slice，但不应该进入主 benchmark 数量目标。

| Group | Names | Reason |
|---|---|---|
| 球类个人技巧 | `Elastico / Flip Flap`, `Marseille Turn / Roulette`, `Cruyff Turn`, `Rainbow Flick` | 虽有正式名称，但太容易被认为是 sport action recognition，学术故事会偏。 |
| 球类战术序列 | `Spain Action`, `Elevator Screen`, `Hammer Action`, `Floppy Action`, `Iverson Cut`, `UCLA Cut`, `Ram Screen`, `Spain Back Screen` | 有时序结构，但依赖比赛语境、站位规则和战术知识，不适合 v1 主科学知识叙事。 |
| 人体专项动作 | `Axel Jump`, `Salchow Jump`, `Yurchenko Vault`, `Kovacs Release`, `Fosbury Flop`, `Ippon Seoi Nage`, `Eskimo Roll / Kayak Roll` 等 | 可以保留为 stress slice；不用于主统计，否则容易被质疑为动作识别。 |
| 长时标/仪器强依赖地貌 | `Glacier Creep`, `Basal Sliding`, `Longshore Drift`, `Sea-Cliff Retreat`, `Spit Progradation` | 单个短视频难唯一判别，容易依赖标题/地点/时间标注。 |
| 过宽生态/动物动作 | `Jet Propulsion Swimming`, `Undulatory Locomotion` | 标签宽泛，缺少唯一阶段规则；需要拆成更具体机制名后再考虑。 |

## Biology Review

生命过程机制仍然是最需要收紧的 domain。

保留主方向：

- 细胞/显微过程：`Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `Axonal Transport`, `Endocytosis`, `Exocytosis`, `Phagocytosis`。
- 植物响应机制：`Phototropism`, `Gravitropism`, `Hydrotropism`, `Thigmonasty`, `Seismonasty`, `Nyctinasty`, `Tendril Circumnutation`, `Bistable Snap-Trap Closure`。
- 机制化生态策略：`Bubble-Net Feeding`, `Mud-Ring Feeding`, `Murmuration`, `C-Start Escape Response`, `Metachronal Wave Locomotion`。

需要降级：

- 动物运动泛标签：`Jet Propulsion Swimming`, `Undulatory Locomotion`。
- 人体专项和球类专项：全部不进入 v1 主目标，只保留 pressure/stress 用途。
- 发育类里的 `Cleavage` 过宽，建议改名或 strict。

## Earth Review

地球环境过程可以成立，但必须避免“灾害视频分类”。

保留主方向：

- `Supercell Mesocyclone Rotation`
- `Pyroclastic Density Current`
- `Pahoehoe Lava Roping`
- `Meander Neck Cutoff`
- `River Avulsion`
- `Debris-Flow Surge Propagation`
- `Slab Avalanche Release`
- `Gust Front Propagation`
- `Dust Storm Front Propagation`
- `Turbidity Current Propagation`

谨慎使用：

- `Ice Cliff Calving`, `Tornadogenesis`, `Downburst / Microburst Outflow`, `Plunging Breaker`, `Tidal Bore`, `Barchan Dune Migration`。

不建议主用：

- `Glacier Creep`, `Basal Sliding`, `Longshore Drift`, `Sea-Cliff Retreat`, `Spit Progradation`。

## Physics Review

自然物理规律整体最稳，但要避免过基础动作。

优先：

- 不稳定性：`Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Saffman-Taylor Viscous Fingering`, `Taylor-Couette Vortices`。
- 界面动力学：`Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Marangoni-Driven Flow`, `Leidenfrost Droplet Motion`。
- 刚体/颗粒：`Gyroscopic Precession`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect`, `Granular Convection`。

降级：

- `Damped Oscillation`, `Elastic Pendulum Motion`, `Standing Wave Formation`：过于课堂演示，strict only。
- 基础液滴动作：`Droplet Coalescence`, `Droplet Rebound`, `Droplet Impact Spreading`：strict backup。
- 电磁/等离子体和太阳活动：概念有效，但多依赖仪器/仿真/元数据，extension。

## Chemistry And Materials Review

物质变化机制整体合理，尤其适合 VDCR，因为很多标签天然是时序反应/相变/自组织图样。

优先：

- `Iodine Clock Reaction`
- `Belousov-Zhabotinsky Reaction`
- `Briggs-Rauscher Reaction`
- `Chemical Garden Growth`
- `Liesegang Ring Formation`
- `Dendritic Crystal Growth`
- `Spinodal Decomposition`
- `Thin-Film Dewetting`
- `Shear Thickening`
- `Weissenberg Rod-Climbing Effect`

谨慎：

- `Benedict Positive Reducing-Sugar Reaction`：容易依赖试剂身份。
- `Crystal Nucleation`：太宽，要有明确成核-生长过程。
- `Precipitation Front Propagation`：过泛，要改成更具体系统。
- `Coffee-Ring Formation`：最终环形沉积有静态捷径，必须显示蒸发输运过程。
- `Gel Swelling`, `Gel Deswelling Collapse`：可用但需要足够时序尺度。

## Recommended Next Cleanup

1. `data/vdcr_concept_pool_v1.csv` 中把球类个人技巧和球类战术全部改为 `extension` 或移出 v1 主池。
2. 把人体专项动作全部保留为 `stress_slice`，不计入主 benchmark 数量。
3. 把 `Jet Propulsion Swimming`、`Undulatory Locomotion` 从主目标移除，拆成具体机制子型后再检索。
4. 把 `Fire Whirl` 的生产标签改为 `Fire-Whirl Vortex Formation`。
5. 把 `Cleavage` 改成更具体的胚胎卵裂时序标签。
6. 主生产目标优先从 50 个 main_pool 和少量强证据 strict_gate 中取，不用 extension 补数。

