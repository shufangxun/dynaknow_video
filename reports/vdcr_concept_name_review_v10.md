# VDCR v1 Concept Name Review v10

Date: 2026-06-06

## Verdict

当前 246 个概念名适合作为 VDCR 的检索候选池，但还不能全部作为主 benchmark 的答案池。

我建议主集答案池遵循更硬的命名原则：

> 答案名必须指向一个由连续时序结构定义的专有动态概念，而不是可被普通视频理解描述覆盖的动作、事件或对象。

换句话说，`视频里是什么` 不够，答案必须是 `这个连续过程在专家知识体系里叫什么`。

## Current Structure

| 项目 | 判断 |
|---|---|
| 一级 domain | 合理。当前四个主域比加入工程、人类临床、球类竞技更稳。 |
| 二级术语族 | 大体合理，但 biology 中的动物运动、人类运动、球类战术需要严控。 |
| 当前 246 个概念 | 可做检索池；主集应只取 `core_main` + 严格通过 gate 的 `strict_main_candidate`。 |
| 人造系统与操作 | 继续延期，作为工程 vertical extension 更合适。 |
| 临床运动体征与步态 | 不进 v1，隐私和伦理成本高。 |
| 球类专项动作与战术 | 不进 v1 主集，容易把 story 拉向 sports/action recognition。 |
| 人体专项运动术语 | 只做 stress slice，不进入主统计。 |

## Hard Naming Rule

一个概念名进入主集前必须同时满足：

1. **专有名词性**：它是学科、技术、生态策略或实验体系中的正式/准正式术语。
2. **时序必要性**：随机单帧无法唯一判别，必须看阶段、轨迹、相位、传播、增长、反馈或失稳。
3. **机制承载性**：名字里最好包含 `instability`、`propagation`、`collapse`、`front`、`wave`、`transport`、`segregation`、`nucleation`、`coarsening`、`chemotaxis` 等动态机制语义。
4. **非泛动作性**：不能只是“动物在游”“人在跳”“冰掉下来”“火在烧”。
5. **视频证据可验证**：网页文字只能 double-check 命名，不能替代视频里的动态证据。

## Strong Main Pool

这些名字本身比较干净，适合作为 v1 主集优先生产对象。

| Domain | 强主集概念类型 | 代表概念 |
|---|---|---|
| 自然物理规律 | 流体/界面/颗粒/非线性动力学 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Faraday Waves`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect`, `Cavitation Bubble Growth and Collapse` |
| 物质变化机制 | 反应动力学、相分离、晶体生长、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Dendritic Crystal Growth`, `Spinodal Decomposition`, `Liesegang Ring Formation`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | 植物响应、细胞动态、发育序列、机制化生态策略 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `C-Start Escape Response`, `Metachronal Wave Locomotion`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | 风暴、密度流、河流改道、熔岩、雪板/颗粒失稳 | `Supercell Mesocyclone Rotation`, `Downburst / Microburst Outflow`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `Debris-Flow Surge Propagation`, `Slab Avalanche Release`, `Gully Headcut Retreat` |

## Rename Before Use

这些名字不是错，但太像表象描述。建议改成更有机制感的答案名。

| Current | Recommended | Reason |
|---|---|---|
| `Stomatal Opening and Closing` | `Guard-Cell Turgor-Driven Stomatal Aperture Dynamics` | “气孔开闭”像动作；推荐名把保卫细胞膨压机制写进去。 |
| `Medusan Bell-Contraction Jet Propulsion` | `Medusan Jet Propulsion by Bell Contraction` | 更自然，突出伞体收缩和喷射推进。 |
| `Embryonic Cleavage Division Sequence` | `Early Embryonic Cleavage Sequence` | 更像标准发育生物学术语。 |
| `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` | “烟上升”太泛；推荐名强调热浮力驱动。 |
| `Dune Slip-Face Avalanche` | `Dune Slip-Face Grain Avalanche` | 明确是滑移面颗粒失稳，不是普通沙丘事件。 |
| `Droplet Rebound` | `Inertia-Capillarity Droplet Rebound` | 强调撞击变形后的毛细恢复与反弹。 |
| `Droplet Impact Spreading` | `Inertia-Driven Droplet Impact Spreading` | 强调撞击后的动力学铺展。 |
| `Gel Swelling` | `Osmotic Gel Swelling Dynamics` | 强调渗透压/溶剂驱动。 |
| `Biofilm Expansion` | `Biofilm Colony Expansion Dynamics` | 避免变成普通“扩张”描述。 |
| `Standing Wave Formation` | `Standing-Wave Mode Formation` | 避免单帧识别“驻波图样”；强调模式建立过程。 |
| `Coherent Wave Interference` | `Coherent Interference Pattern Formation` | 强调干涉图样的动态形成，而不是静态条纹。 |
| `Droplet Coalescence` | `Capillary-Driven Droplet Coalescence` | 增加机制语义。 |
| `Capillary Breakup` | `Capillary-Driven Jet/Thread Breakup` | 避免过宽。具体样本应按液丝或射流命名。 |
| `Crystal Nucleation` | `Crystal Nucleation-and-Growth Dynamics` | 单纯“成核”往往视频不可见；需要同时看到增长。 |
| `Precipitation Front Propagation` | `Reaction-Precipitation Front Propagation` | 明确是反应/扩散耦合沉淀前沿。 |
| `Flame Front Propagation` | `Reactive Flame-Front Propagation` | 避免普通火焰移动。 |
| `Ciliary Beating` | `Coordinated Ciliary Beating Dynamics` | 避免单根纤毛摆动的泛动作化。 |
| `Filopodium Protrusion` | `Actin-Driven Filopodium Protrusion` | 增加细胞骨架机制。 |
| `Lamellipodium Extension` | `Actin-Driven Lamellipodium Extension` | 增加机制语义。 |

## Strict Candidates

这些概念名可以保留，但视频 gate 必须很硬。否则会退化成普通视频理解。

| Concept | Risk | Required Video Evidence |
|---|---|---|
| `Magnus Effect` | 看到旋转球和弯曲轨迹可能被体育/常识捷径猜中。 | 必须同时看到旋转、弯曲轨迹、流体偏转/力学后果；不能只看球路。 |
| `Capillary Rise / Wicking` | 可能只是“液体往上爬”。 | 必须看到液面/湿润前沿沿细通道或多孔介质连续上升。 |
| `Liquid Bridge Pinch-Off` | 单帧颈缩也可能猜到。 | 必须看到液桥拉伸、颈缩、断裂全过程。 |
| `Leidenfrost Droplet Motion` | 可能依赖热板语境。 | 必须看到液滴悬浮滑动、快速运动/寿命异常；无文字泄漏。 |
| `Damped Oscillation` | 太基础，容易像高中物理描述。 | 只在视频能显示振幅逐周期衰减时收；不适合大量生产。 |
| `Shock Wave Propagation` | 常依赖 schlieren 或实验语境。 | 必须有清楚前沿传播，不可只靠标题。 |
| `Blue Bottle Reaction` | 颜色变化容易被实验名称泄漏。 | 必须去掉文字/音频，且展示摇动-还原-氧化循环。 |
| `Benedict Positive Reducing-Sugar Reaction` | 视频本身可能只能看到颜色变化。 | 必须有试剂加热、颜色/沉淀渐变，网页只做 double-check。 |
| `Coffee-Ring Formation` | 最终环形沉积可被单帧识别。 | 必须看到蒸发期间沉积前沿形成，而不是只给干后的环。 |
| `Endocytosis` / `Exocytosis` | 显微图像常需标注。 | 必须看到膜内陷/囊泡形成或囊泡融合/释放的连续阶段。 |
| `FRAP Recovery` | 强依赖实验操作语境。 | 只能在视频显示漂白区荧光恢复且无文字提示时作为 extension。 |
| `Murmuration` | 鸟群外观捷径强。 | 必须看到群体形态波、同步转向、流场式重组。 |
| `Ice Cliff Calving` | 可能只是“冰掉下来”。 | 必须看到裂缝/失稳、冰崖脱离、坠落入水序列。 |
| `Lava Dome Collapse` | 很多公开视频只是卫星图或烟。 | 必须看到穹丘局部失稳、崩落、碎屑流/喷发响应。 |
| `Storm Surge Propagation` | 常需地图/注释。 | 必须有水位/海水推进的连续证据，不能只靠路径图。 |
| `Aeolian Saltation` | 沙粒小，很多素材不可见。 | 必须能看出近地跳跃输沙，不是普通沙尘。 |

## Downgrade Or Remove From Main

这些概念不一定没有价值，但不适合 v1 主集。

| Group / Concept | Decision | Reason |
|---|---|---|
| `Elastico / Flip Flap`, `Marseille Turn`, `Cruyff Turn`, `Rainbow Flick` | `defer_or_remove` | 虽有专名，但强烈拉向球类动作识别。 |
| `Spain Action`, `Elevator Screen`, `Hammer Action`, `Floppy Action`, `Iverson Cut`, `UCLA Cut`, `Ram Screen`, `Spain Back Screen` | `defer_or_remove` | 战术序列依赖比赛语境、队形和规则知识，主线不够科学动态知识。 |
| `Axel Jump`, `Salchow Jump`, `Yurchenko Vault`, `Fouette Turn`, judo throws 等 | `stress_slice` only | 有正式动作分类和时序规则，但主集过多会像体育动作 benchmark。 |
| `Anguilliform Undulation` | `extension` | 术语正式，但容易被看成“鱼/蛇在游”。需要强对照才可用。 |
| `Glacier Creep`, `Basal Sliding`, `Glacier Surge` | `defer/extension` | 时间尺度长，视觉证据往往依赖标注或来源文本。 |
| `Longshore Drift`, `Sea-Cliff Retreat`, `Spit Progradation` | `defer_or_remove` | 静态地貌/地图捷径强，纯视频证据难。 |
| `Fault Rupture Propagation` | `defer_or_remove` | 公开视频多为模拟/仪器图，难以作为自然视频证据。 |
| `Convergent Extension`, `Neural Tube Closure`, `Epithelial-Mesenchymal Transition` | `defer_or_remove` | 生物显微证据依赖标注、荧光通道和专业上下文。 |
| `Magnetic Reconnection`, `Coronal Mass Ejection`, `Solar Prominence Eruption` | `extension` | 科学性强，但常依赖卫星仪器和伪彩/注释；可做天文扩展。 |

## Domain-Level Review

### 自然物理规律

整体最稳。建议主集优先从流体不稳定性、界面断裂、液滴冲击、颗粒分离、非线性振动中取。需要注意的是，`Standing Wave Formation`、`Coherent Wave Interference`、`Damped Oscillation` 这些名字比较基础，必须用视频 gate 证明它不是单帧图样或普通物理描述。

### 物质变化机制

整体稳，但化学实验类必须防标题/网页泄漏。`Iodine Clock Reaction`、`Belousov-Zhabotinsky Reaction`、`Briggs-Rauscher Reaction` 很适合主集；`Benedict Positive Reducing-Sugar Reaction` 只有在视频能看出加热和沉淀/颜色演化时才收。相分离、结晶、枝晶、电沉积是非常好的 VDCR 主线。

### 生命过程机制

需要最严格。植物趋性、细胞动态、发育序列是主集核心；动物生态策略可以收，但只收有命名策略和阶段结构的，例如 `Bubble-Net Feeding`、`Mud-Ring Feeding`、`C-Start Escape Response`。动物运动模式和人体运动术语要控制比例，球类战术不进主集。

### 地球环境过程

可以进入 video knowledge，但必须避免“自然灾害事件识别”。`Slab Avalanche Release` 比 `Snow Avalanche Release` 更好；`Pyroclastic Density Current` 比 `volcano eruption` 更好；`Meander Neck Cutoff` 比 `river changes course` 更好。地球类样本必须写清楚动态证据，避免只靠卫星图、标题或地图动画。

## Practical Production Policy

1. 主集只从 `core_main` 和严格通过视频 gate 的 `strict_main_candidate` 中生产。
2. 每个答案概念只保留一条主集样本，概念级去重。
3. 每条样本必须记录：
   - video temporal evidence
   - why single frame is insufficient
   - why this is not generic video understanding
   - source page double-check result
   - whether the source page contains useful knowledge or only broad description
4. 如果视频只能支持表象描述，拒绝；不能靠网页补出答案。
5. 如果网页直接泄漏答案，必须裁剪/清洗视频和元数据；否则拒绝。
6. 体育、人类动作、动物普通运动都不得用来凑主集数量。

## Bottom Line

当前名字体系的方向是对的，但需要更“机制化命名”和更硬的 tier gate。

最适合 v1 主集的不是所有有术语的动态动作，而是那些名字本身已经编码了动态机制的概念：不稳定性、前沿传播、相变/成核、生长/粗化、趋性/感性、细胞运输、群体策略、地貌/灾害过程的失稳和推进。
