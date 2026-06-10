# VDCR v1 Concept Name Review v9

Date: 2026-06-06

## Verdict

当前 `data/vdcr_concept_inventory_v1.csv` 里的 246 个名字适合作为“候选检索池”，但不能直接等价为 v1 benchmark 的主集答案池。

我建议把当前概念名重新分成四类：

| Tier | 用法 | 结论 |
|---|---|---|
| `core_main` | v1 主生产池 | 名字本身就是动态机制/过程专有名，且视频证据可独立支撑。 |
| `strict_main_candidate` | 条件主池 | 名字成立，但必须用视频 gate 证明不是普通动作、普通事件或来源文本泄漏。 |
| `stress_slice` | 压力切片 | 人体专项动作等可以存在，但不应撑主故事。 |
| `defer_or_remove` | 延期/删除 | 太像视频理解、太宽泛、伦理/隐私/版权风险高，或高度依赖仪器/来源描述。 |

核心判断不变：

> VDCR 的答案不是“视频里发生了什么”，而是“这个连续时序过程对应哪个专家知识体系里的专有动态概念”。

## Current Inventory Audit

| 项目 | 数量 |
|---|---:|
| 当前候选总数 | 246 |
| 自然物理规律 | 58 |
| 物质变化机制 | 50 |
| 生命过程机制 | 82 |
| 地球环境过程 | 56 |
| Priority A | 65 |
| Priority B | 158 |
| Priority C | 23 |

注意：`Priority A` 现在不等于一定能进主集。比如球类战术里有几个 A，但从 benchmark 叙事上仍然应该移出主集。

## Strong Main-Pool Names

这些概念名最符合 VDCR：名字本身编码了动态机制、阶段序列、传播、失稳、转运、反馈或自组织过程。

| Domain | 推荐主集概念类型 | 代表概念 |
|---|---|---|
| 自然物理规律 | 流体不稳定性、界面断裂、非线性波动、刚体/颗粒动力学 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Rayleigh-Plateau Breakup`, `Liquid Bridge Pinch-Off`, `Faraday Waves`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect`, `Boiling Bubble Nucleation and Departure` |
| 物质变化机制 | 振荡反应、反应前沿、枝晶/晶体生长、相分离、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Briggs-Rauscher Reaction`, `Dendritic Crystal Growth`, `Spinodal Decomposition`, `Liesegang Ring Formation`, `Shear Thickening`, `Weissenberg Rod-Climbing Effect` |
| 生命过程机制 | 植物趋性/感性、细胞转运、细胞骨架动态、显微信号波、机制化生态策略 | `Phototropism`, `Gravitropism`, `Thigmonasty`, `Cytoplasmic Streaming`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `C-Start Escape Response`, `Metachronal Wave Locomotion`, `Bubble-Net Feeding`, `Mud-Ring Feeding` |
| 地球环境过程 | 风暴旋转/出流、密度流、河流改道、熔岩流变、颗粒/雪板失稳 | `Supercell Mesocyclone Rotation`, `Downburst / Microburst Outflow`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `Debris-Flow Surge Propagation`, `Slab Avalanche Release`, `Gully Headcut Retreat` |

## Keep, But Tighten Names

这些概念可以保留，但当前名字有点像现象描述。建议改成更机制化的答案名。

| Current | Better | Reason |
|---|---|---|
| `Stomatal Opening and Closing` | `Guard-Cell Turgor-Driven Stomatal Aperture Dynamics` | “气孔开闭”太像动作；新名字把保卫细胞膨压机制写进标签。 |
| `Medusan Bell-Contraction Jet Propulsion` | `Medusan Jet Propulsion by Bell Contraction` | 更自然，也明确水母伞体收缩与喷射推进的机制关系。 |
| `Embryonic Cleavage Division Sequence` | `Early Embryonic Cleavage Sequence` | 更像标准发育生物学术语，避免重复的 “division sequence”。 |
| `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` | “烟上升”容易泛化；要强调热浮力驱动烟羽。 |
| `Dune Slip-Face Avalanche` | `Dune Slip-Face Grain Avalanche` | 明确是沙丘滑移面上的颗粒雪崩，不是普通沙丘事件。 |
| `Droplet Rebound` | `Inertia-Capillarity Droplet Rebound` | “液滴反弹”略宽；改名后强调惯性-毛细恢复。 |
| `Droplet Impact Spreading` | `Inertia-Driven Droplet Impact Spreading` | 强调撞击后铺展的动力学，而不是普通液滴变扁。 |
| `Gel Swelling` | `Osmotic Gel Swelling Dynamics` | “凝胶溶胀”容易变成状态变化；要体现渗透压/网络吸水过程。 |
| `Biofilm Expansion` | `Biofilm Colony Expansion Dynamics` | 比“扩张”更像微生物群体动力学概念。 |

## Move Out Of v1 Main

这些不是完全没价值，但不应进入主 benchmark 的主统计。

| Group | Decision | Reason |
|---|---|---|
| 人体专项动作与运动技术 | `stress_slice` only | 有正式命名体系，但容易被审稿人理解成 sport/action recognition；可以做附录压力切片。 |
| 球类专项动作与战术序列 | `defer_or_remove` | 即使有“牛尾巴、马赛回旋、西班牙战术”等专名，也太像比赛动作/战术识别，和主线科学动态知识有叙事冲突。 |
| 临床运动体征与步态 | 删除/延期 | 患者隐私、同意、伦理成本高，不适合 v1。 |
| 人造系统与操作 | 延期 | 术语很垂直，适合工程 vertical benchmark，不适合当前 v1 主故事。 |
| 宽泛动物运动模式 | 多数降级到 `extension` | `Anguilliform Undulation`, `Peristaltic Locomotion`, `Sidewinding Locomotion` 这类术语虽然正式，但很容易被看成“动物怎么动”。除非有强对照集，否则不进主集。 |

## Specific Risk Review

| Concept | My decision | Reason |
|---|---|---|
| `C-Start Escape Response` | keep main | 它不是“鱼在转身”，而是有明确神经行为学定义的快速逃逸相位序列。 |
| `Medusan Jet Propulsion by Bell Contraction` | strict candidate | 可以成立，但视频必须看到伞体收缩、排水反冲、位移推进的完整节律。 |
| `Anguilliform Undulation` | extension | 正式术语成立，但静态+常识捷径偏强，容易退化成动物运动识别。 |
| `Metachronal Wave Locomotion` | keep main | 重点是多纤毛/多附肢的相位波，不是普通爬行。 |
| `Murmuration` | strict candidate | 概念有专名，但鸟群外观捷径强；必须看到群体流场式形变和同步转向。 |
| `Bubble-Net Feeding` | keep main | 属于命名生态策略，必须看吐泡、围困、同步上冲等时序结构。 |
| `Mud-Ring Feeding` | keep main | 属于命名生态策略，必须看造泥环、驱赶猎物、捕食收束序列。 |
| `FRAP Recovery` | strict/possibly defer | 是实验知识，但答案依赖实验操作语境；只有无文字泄漏且视频显示漂白区恢复曲线/区域变化时才收。 |
| `Endocytosis` / `Exocytosis` | strict candidate | 专业性强，但显微视频必须清楚显示膜内陷/囊泡形成或囊泡融合/释放阶段。 |
| `Ice Cliff Calving` | strict candidate | 不能收“冰掉下来”；必须看到裂缝、失稳、崩解、坠落入水的序列。 |
| `Slab Avalanche Release` | keep main | 比 `Snow Avalanche Release` 更专业，视频需要看到冠状裂缝/板块启动/整体滑移。 |
| `Glacier Creep` / `Basal Sliding` | defer | 时间尺度和观测证据太依赖注释/模型，公开视频难以纯视觉验证。 |
| `Wave Refraction` | extension | 常见素材多为动画/教学演示，适合补充，不适合主集凑数。 |

## Production Rules After This Review

1. 主集只从 `core_main` 和少量通过严格 gate 的 `strict_main_candidate` 中出。
2. 人体专项动作只允许作为 `stress_slice`，不参与主统计。
3. 球类专项动作和战术序列当前从 v1 主生产中移出。
4. 每条样本必须写清楚：视频动态证据、网页 double-check 是否有效、单帧为什么不够、为什么不是普通动作/普通事件。
5. 如果网页只给宽泛描述，不能用网页补脑；网页只能用于验证命名和来源，不能替代视频证据。
6. 同一答案概念只保留一条样本，概念级去重继续强制执行。

## Recommended Next Edit

下一步应把 inventory 里的 `priority` 拆成两个字段：

| Field | Meaning |
|---|---|
| `concept_validity_tier` | `core_main`, `strict_main_candidate`, `stress_slice`, `extension`, `defer_or_remove` |
| `production_gate` | 针对视频审核时必须证明的动态证据 |

这样不会再出现“球类战术是 A，但又不该进主集”的混乱。
