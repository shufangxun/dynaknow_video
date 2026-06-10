# VDCR v1 Concept Name Review v5

Date: 2026-06-06

## Review Conclusion

当前概念命名体系已经基本避开了普通视频理解，但仍需要把 `strict_gate` 当作真实门控，而不是候补主池。v1 主 benchmark 应优先使用“名称本身编码动态机制”的概念；事件名、动作名、场景名即使是专业词，也只能在具体视频证明时序必要性后进入。

核心判断句：

> VDCR 的答案标签应当是“连续时序过程对齐到的专家概念”，不是“视频里看见的动作或事件”。

## Strong Main-Pool Name Types

这些类型合理，可作为 v1 主生产方向：

| Domain | 强类型 | 例子 |
|---|---|---|
| 自然物理规律 | 不稳定性、涡动力学、界面断裂、非线性刚体/颗粒动力学 | `Kelvin-Helmholtz Instability`, `Rayleigh-Taylor Instability`, `Vortex Shedding / Karman Vortex Street`, `Liquid Bridge Pinch-Off`, `Dzhanibekov Effect / Tennis Racket Theorem`, `Brazil Nut Effect` |
| 物质变化机制 | 振荡反应、自组织沉淀、晶体生长、相分离、非牛顿响应 | `Iodine Clock Reaction`, `Belousov-Zhabotinsky Reaction`, `Dendritic Crystal Growth`, `Liesegang Ring Formation`, `Spinodal Decomposition`, `Shear Thickening` |
| 生命过程机制 | 植物趋性/感性、细胞运输、细胞骨架、显微动态波 | `Phototropism`, `Thigmonasty`, `Cytoplasmic Streaming`, `Mitotic Chromosome Segregation`, `Microtubule Dynamic Instability`, `Calcium Wave Propagation` |
| 地球环境过程 | 机制化灾变、风暴旋转/出流、熔岩/火山密度流、河流裁弯 | `Supercell Mesocyclone Rotation`, `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `Slab Avalanche Release` |

## Names That Are Valid But Need Tight Video Gates

这些名字不是错，但不能凭术语直接收。必须在视频级别证明时序证据足够强。

| Concept | Decision | Gate Requirement |
|---|---|---|
| `Hydraulic Jump` | keep as `strict_gate` | 必须看到超临界流到亚临界流的滚水区形成，不能只是静态水面形态。 |
| `Tidal Bore` | keep as `strict_gate` | 必须看到波前逆河推进，不能只是普通海浪或河面浪。 |
| `Plunging Breaker` | keep as `strict_gate` | 必须看到波唇前翻、卷入、破碎序列，单帧浪花不够。 |
| `Ice Cliff Calving` | keep as `strict_gate` | 必须看到裂缝扩展、冰崖失稳、坠落/入水序列；普通“冰块掉落”不够。 |
| `Fire Whirl` | rename preferred | 建议生产标签写成 `Fire-Whirl Vortex Formation`，强调旋涡形成而不是火柱外观。 |
| `Downburst / Microburst Outflow` | keep but difficult | 必须看到冷池/雨幕下沉后的地面径向扩散，普通暴雨风暴不够。 |
| `Tornadogenesis` | keep but difficult | 必须看到旋转云底到漏斗/地面涡旋的发展过程，已有漏斗单帧不够。 |
| `Barchan Dune Migration` | keep as strict/extension only | 需要延时看到迎风坡侵蚀和背风坡滑移导致整体迁移；静态新月沙丘不够。 |
| `Rip Current Formation` | keep as strict | 必须看到离岸通道建立与水流方向，单帧海岸色带不够。 |

## Names To Downgrade, Rename, Or Avoid

| Current Name | Problem | Suggested Handling |
|---|---|---|
| `Jet Propulsion Swimming` | 名称过宽，容易变成“水母/头足类在游”。 | 不作为主标签；若用，改成具体机制型标签，如 `Medusan Bell-Contraction Jet Propulsion` 或 `Cephalopod Mantle-Jet Propulsion`。 |
| `Undulatory Locomotion` | 太泛，看到蛇/鱼摆动就能猜，接近动作识别。 | 删除或拆成正式模式，如 `Anguilliform Swimming`, `Carangiform Swimming`，并要求对比负例。 |
| `Droplet Coalescence`, `Droplet Rebound`, `Droplet Impact Spreading` | 是动态过程，但过基础，专家命名 gap 较弱。 | 保留 strict；只收高速/近邻负例明确的视频，不进主目标优先级。 |
| `Benedict Positive Reducing-Sugar Reaction` | 反应名依赖试剂和样品身份，视频画面本身可能只显示颜色/沉淀。 | 高风险 strict；若无可见实验上下文或无强近邻负例，拒绝。 |
| `Cleavage` | 名字太宽，容易只是“细胞分裂”。 | 改成更机制化子标签，或只收显微延时中阶段清晰的视频。 |
| `Glacier Creep`, `Basal Sliding`, `Longshore Drift`, `Sea-Cliff Retreat` | 长时标或需测量/仪器，单视频短片难唯一识别。 | 保持 `extension`，不用于 v1 主补量。 |
| 球类个人技巧 | 即使有正式名称，也容易被质疑为 sport action recognition。 | 继续排除 v1 主目标。 |
| 球类多人战术 | 有时序结构，但评审故事容易偏向比赛理解。 | 只作为未来 extension，不参与主 BMK。 |

## Biology-Specific Verdict

生命过程机制里最稳的是细胞、植物、微生物显微过程；动物/人体动作最容易越界。

保留主方向：

- `C-Start Escape Response`: 合理，因为标签对应神经肌肉逃逸反应的 C 形弯曲与快速推进序列。
- `Metachronal Wave Locomotion`: 合理，因为核心是相位错开的节律波，不是“很多腿在动”。
- `Bubble-Net Feeding`, `Mud-Ring Feeding`: 合理但必须完整展示策略阶段，不能只看到鲸/海豚在水面活动。
- `Murmuration`: 合理，属于群体动力学/生态行为策略，但要避免只用静态鸟群形状。

需要收紧：

- `Jet Propulsion Swimming` 和 `Undulatory Locomotion` 不应作为 v1 主标签。
- `Bistable Snap-Trap Closure` 比 `Venus Flytrap Closure` 合理，因为它命名的是双稳态快速闭合机制，而不是物种动作。
- `Thigmonasty`, `Nyctinasty`, `Phototropism`, `Gravitropism` 合理，因为它们是植物响应机制，不是“植物在动”。

## Earth/Environment-Specific Verdict

地球环境 domain 是合理的，但必须避免“灾害事件识别”。合格形式应是机制化事件名：

- `Snow Avalanche Release` 不合格，`Slab Avalanche Release` 合格。
- `Glacier Calving` 过宽，`Ice Cliff Calving` 更好，但仍需视频级门控。
- `Iceberg Rollover` 不合格，太像可见事件。
- `Pyroclastic Density Current` 合格，因为它指向密度流机制，不只是“火山烟尘”。
- `Debris-Flow Surge Propagation` 合格，因为它强调脉冲推进，不只是“泥石流”。

## Production Policy

后续生产建议：

1. v1 pass 样本只从 `main_pool` 和通过强门控的 `strict_gate` 来。
2. `extension` 不用于补数量；`stress_slice` 最多作为附录压力分析。
3. 每个样本必须记录四句话：为什么不是普通视频理解、为什么静帧不够、需要观察哪些时序阶段、同域近邻负例是什么。
4. 对宽泛名称优先改成机制化名称，再检索视频；不要用视频里的表面动作反推一个宽泛标签。

## Immediate Cleanup Recommendations

建议下一步改池子时执行：

- 将 `Fire Whirl` 的生产标签改为 `Fire-Whirl Vortex Formation`。
- 将 `Jet Propulsion Swimming` 从主生产候选移出，拆成具体机制子型。
- 将 `Undulatory Locomotion` 移出或拆成正式游动模式。
- 将 `Benedict Positive Reducing-Sugar Reaction` 标为高风险 strict，只在画面证据足够时使用。
- 保持球类和人体专项概念不参与主 benchmark 数量目标。
- 地球环境补量优先从 `Pyroclastic Density Current`, `Pahoehoe Lava Roping`, `Meander Neck Cutoff`, `Slab Avalanche Release`, `Debris-Flow Surge Propagation`, `Gust Front Propagation`, `Dust Storm Front Propagation` 这类机制化标签里采。
