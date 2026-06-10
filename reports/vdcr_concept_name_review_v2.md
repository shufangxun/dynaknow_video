# VDCR v1 Concept Name Review v2

Date: 2026-06-06

## 结论

当前 245 个概念的总体方向是合理的，但不能都按同等优先级进入 v1 主池。

VDCR 的核心不是“视频里有什么动作/事件”，而是“这个连续动力学过程对应哪个专有机制、技术、策略或实验动态图样”。按这个标准，物理、材料化学、细胞/植物生物、地球环境过程是主干；人体专项动作和球类战术可以作为少量扩展，但不应该成为主池支柱。

## 建议执行策略

| 层级 | 处理方式 | 说明 |
|---|---|---|
| 主池 A | 优先检索、下载、构造样本 | 动态机制明确，单帧难判别，专业名词稳定 |
| 严格 B | 可保留，但必须逐条视频 gate | 名字合理，但容易被场景/物体/常识动作 shortcut |
| 扩展 C | 暂不作为 v1 数量目标 | 需要仪器、长时标、仿真或专业上下文才可判别 |
| 删除/移出主池 | 不进入 v1 | 更像普通视频理解、泛动作识别或可由单帧猜中 |

## 各领域判断

### 自然物理规律

整体最强，适合作为 v1 backbone。

| 判断 | 概念族/概念 | 理由 |
|---|---|---|
| 主池 A | Kelvin-Helmholtz Instability, Rayleigh-Taylor Instability, Karman Vortex Street, Cavitation Bubble Growth and Collapse | 都是由时序形变、界面失稳、涡脱落或泡塌缩定义的机制，不是物体识别 |
| 主池 A | Rayleigh-Plateau Breakup, Liquid Bridge Pinch-Off, Marangoni-Driven Flow, Leidenfrost Droplet Motion | 需要观察断裂、颈缩、界面驱动或液滴运动轨迹 |
| 主池 A | Faraday Waves, Standing Wave Formation, Gyroscopic Precession, Dzhanibekov Effect, Brazil Nut Effect, Vortex Ring Formation | 具有清晰动态模式和专业命名 |
| 严格 B | Droplet Rebound, Droplet Spreading and Retraction, Damped Oscillation, Elastic Pendulum Motion | 名字合理，但容易变成“液滴弹起/摆在动”的表面描述，需要近邻负例 |
| 扩展 C | Prandtl-Meyer Expansion Fan, Shock-Boundary-Layer Interaction, Magnetic Reconnection, Plasma Filamentation | 专业性强，但视频常依赖仿真、诊断图或文字标注，release 前要严查泄漏 |

### 物质变化机制

总体合理，但要警惕“只看视频无法唯一知道试剂”的化学反应。

| 判断 | 概念族/概念 | 理由 |
|---|---|---|
| 主池 A | Shear Thickening, Weissenberg Rod-Climbing Effect, Dendritic Crystal Growth, Chemical Garden Growth, Liesegang Ring Formation | 动态外观和机制绑定强，视频原生性好 |
| 主池 A | Iodine Clock Reaction, Belousov-Zhabotinsky Reaction, Briggs-Rauscher Reaction | 有命名实验动态图样，颜色/振荡/延迟终点依赖时序 |
| 严格 B | Blue Bottle Reaction, Chemical Traffic Light Reaction, Benedict Positive Reducing-Sugar Reaction | 如果没有试剂上下文，单靠视频可能不可唯一判别；可用但必须依赖完整动态序列和 source double-check |
| 严格 B | Crystal Nucleation, Precipitation Front Propagation, Reaction-Diffusion Wave, Coffee-Ring Formation | 名字合理，但需要避免泛化成“结晶/沉淀/扩散/干了” |
| 扩展 C | Corrosion Pit Growth, Anodic Oxide Film Growth, Lithium Dendrite Growth, Liquid Crystal Domain Evolution, Liquid Crystal Defect Annihilation | 多数需要显微、仪器或标注背景，先不作为 v1 主力 |

### 生命过程机制

植物、细胞、微生物很强；动物和人体动作要克制。

| 判断 | 概念族/概念 | 理由 |
|---|---|---|
| 主池 A | Phototropism, Gravitropism, Thigmonasty, Nyctinasty, Bistable Snap-Trap Closure | 不是“植物动了”，而是有正式生理机制名称 |
| 主池 A | Cytoplasmic Streaming, Mitotic Chromosome Segregation, Calcium Wave Propagation, FRAP Recovery, Endocytosis, Exocytosis, Microtubule Dynamic Instability | 显微动态机制清晰，视频时序必要性强 |
| 主池 A | C-Start Escape Response, Metachronal Wave Locomotion, Bubble-Net Feeding, Mud-Ring Feeding, Murmuration | 有专有行为/生态策略或运动学模式，不是普通动物动作 |
| 严格 B | Jet Propulsion Swimming, Undulatory Locomotion | 容易被看成“水母喷水/身体波动”，需要机制级负例；不宜大量使用 |
| 严格 B | Figure skating jumps, gymnastics vaults, judo throws, Eskimo Roll, Eggbeater Kick, Surfing Bottom Turn, Carving Turn | 有正式命名体系，但容易滑向动作识别；应限制在 10-15% 以下 |
| 扩展 C | Gastrulation, Neural Tube Closure, Epithelial-Mesenchymal Transition, Convergent Extension | 概念有效，但常依赖显微标记、长时标或动画；先作为扩展 |
| 建议移出主池 | Elastico, Marseille Turn, Cruyff Turn, Rainbow Flick | 虽有术语，但更像足球技巧识别，容易由球场/脚法/单人动作猜中 |
| 保留为扩展 | Spain Action, Elevator Screen, Hammer Action, Floppy Action, Iverson Cut, UCLA Cut, Ram Screen, Spain Back Screen | 比单人技巧强，因为依赖多人时序结构；但素材版权和 broadcast overlay 风险高 |

### 地球环境过程

可以保留，但要把“事件名”改成“机制名/过程名”，并优先选择能在短视频中显现阶段变化的概念。

| 判断 | 概念族/概念 | 理由 |
|---|---|---|
| 主池 A | Downburst / Microburst Outflow, Supercell Mesocyclone Rotation, Tornadogenesis, Gust Front Propagation | 需要追踪扩散、旋转、生成或推进过程 |
| 主池 A | Pyroclastic Density Current, Pahoehoe Lava Roping, Aa Lava Front Advance, Slab Avalanche Release | 具有地学专有名词和动态过程边界 |
| 主池 A | Aeolian Saltation, Barchan Dune Migration, Gully Headcut Retreat, Tidal Bore, Plunging Breaker | 比“沙在动/水来了/浪碎了”更机制化 |
| 严格 B | Fire Whirl, Ice Cliff Calving, Wall Cloud Rotation, Landspout Development, Rip Current Formation | 名字合理，但单帧/场景 shortcut 风险较高；要看完整阶段和近邻负例 |
| 扩展 C | Glacier Creep, Basal Sliding, Sea-Cliff Retreat, Spit Progradation, Wave Refraction, Fault Rupture Propagation | 长时标或需要仪器/地图/模型，短视频难以无泄漏判别 |
| 已正确移除 | Iceberg Rollover, Snow Avalanche Release, Glacier Flow, Glacier Calving | 这些更像可见事件名，现已替换为更机制化的目标 |

## 需要进一步收紧的点

1. 球类单人技巧建议全部移出 v1 主池，只作为 future extension。它们有专业名词，但学术 story 容易被质疑为 sport action recognition。
2. 人体专项动作保留少量即可，优先选评分体系中必须看起跳、腾空、旋转、落地阶段的项目。
3. 化学反应类必须加“视觉可判别性”gate：如果视频不展示完整颜色序列、沉淀形成、振荡周期或反应前沿，仅靠网页标题才能知道答案，就不能入选。
4. 地球环境类必须避免纯事件名。`冰掉下来`、`火柱旋转`、`浪打碎`不够；要能对应到 `Ice Cliff Calving`、`Fire Whirl`、`Plunging Breaker` 这类机制标签。
5. 所有 C 类概念可以继续作为 retrieval seed，但不应该计入 v1 的 248 条 pass 目标，除非拿到极干净、无标注、时序必要性强的视频。

## 当前建议

保留 4 个一级 domain，不恢复工程域。v1 的实际采样应偏向：

- 物理：流体不稳定、液滴/界面、波动振动、颗粒/刚体；
- 化学材料：流变、振荡反应、晶体/沉淀/扩散图样、电化学生长；
- 生物：植物动态响应、细胞显微动态、微生物群体动态、少量生态策略；
- 地球环境：风暴、火山/熔岩、风沙/水文/坡面侵蚀、少量冰冻圈/野火；
- 人体/体育：只作为小比例 stress slice，不作为主干。

