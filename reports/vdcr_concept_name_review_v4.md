# VDCR v1 Concept Name Review v4

Date: 2026-06-06

## 结论

当前视频动态专有概念体系总体合理，但 v1 生产时必须把“主 benchmark 概念”和“边界压力概念”分开使用。

VDCR 的答案标签不应是视频里可直接描述的动作或事件，而应是连续动态过程在专家知识体系中对应的专有概念。判断边界是：

- 能否只靠单帧、场景或物体猜中；
- 名称是否有稳定学科、技术、生态或训练体系来源；
- 名称是否编码了阶段、轨迹、传播、反馈、失稳、前沿、相变、群体策略等动态结构；
- 能否构造同域近邻负例。

## 当前 Tier 决策

| Tier | 用途 | 数量 | 处理原则 |
|---|---:|---:|---|
| `main_pool` | v1 优先生产目标 | 50 | 强机制、强时序、弱静帧捷径 |
| `strict_gate` | 候补生产目标 | 143 | 概念名成立，但必须靠具体视频证明时序必要性 |
| `extension` | 不进入 v1 主目标 | 36 | 有术语价值，但存在版权、仪器、长时标、体育识别或语义过宽风险 |
| `stress_slice` | 小比例压力切片 | 16 | 跨项目人体专项技术，最多用于边界分析 |

## 保留为 v1 主池的强类型

| Domain | 合理性 |
|---|---|
| 自然物理规律 | 流体不稳定性、界面动力学、振动非线性、刚体/颗粒动力学通常具有明确动态图样和近邻负例。 |
| 物质变化机制 | 流变响应、振荡反应、自组织沉淀、晶体生长、相分离过程适合作为视频原生知识。 |
| 生命过程机制 | 植物趋性、细胞显微动态、囊泡运输、细胞骨架动态是强 VDCR 类型。 |
| 地球环境过程 | 风暴旋转/出流、火山碎屑流、熔岩前缘、河流裁弯、板状雪崩等在机制化命名后可以成立。 |

## 需要严格门控的名字

| 概念 | 当前处理 | 理由 |
|---|---|---|
| `Hydraulic Jump` | `strict_gate` | 单帧可能看到水跃形态；视频必须展示流态转换和滚水区形成。 |
| `Tidal Bore` | `strict_gate` | 需要看到逆河推进的长距离波前，不能只是普通浪。 |
| `Ice Cliff Calving` | `strict_gate` | 应强调裂缝扩展、失稳、坠落序列，否则像普通冰块掉落。 |
| `Fire Whirl` | `strict_gate` | 静态火柱捷径强，建议生产时改为 `Fire-Whirl Vortex Formation`。 |
| `Jet Propulsion Swimming` | `strict_gate` | 名字过宽，生产时应细化为水母伞体收缩喷射或头足类喷射推进。 |
| `Undulatory Locomotion` | `strict_gate` | 名字过宽，生产时应细化为 `Anguilliform`、`Carangiform` 等正式模式。 |
| `Bacterial Chemotaxis` | `strict_gate` | 必须展示梯度响应或定向迁移，不能只是细菌游动。 |

## 已降级或不用于 v1 主目标

| 类型 | 概念 | 处理 |
|---|---|---|
| 球类单人技巧 | `Elastico`, `Marseille Turn`, `Cruyff Turn`, `Rainbow Flick` | `extension`，不计入 v1 pass 目标。 |
| 球类多人战术 | `Spain Action`, `Elevator Screen`, `Hammer Action`, `Floppy Action`, `Iverson Cut`, `UCLA Cut`, `Ram Screen`, `Spain Back Screen` | `extension`，有多人时序结构，但容易被质疑为 sport play recognition。 |
| 临床步态/体征 | 全部 | 删除/延期，避免患者隐私与伦理风险。 |
| 人造系统与操作 | 全部 | 延期为工程垂直 benchmark，不参与 v1。 |
| 可见事件名 | `Iceberg Rollover`, `Snow Avalanche Release`, `Glacier Flow`, generic `Glacier Calving` | 删除或替换为机制化子型。 |
| 物种/对象加动作 | `捕蝇草闭合`, `猎豹奔跑`, `螳螂虾击打` | 删除或改写为稳定机制标签，如 `Bistable Snap-Trap Closure`。 |

## 对“专有动作概念”的保留边界

人体专项动作不是完全排除，但只能作为 `stress_slice`，且需要跨多个正式训练体系：花滑、体操、柔道、水上运动、滑雪/冲浪等。它们不能替代主池科学机制。

v1 生产时建议控制在 5% 以下；若主论文叙事要更硬，可以完全不放入主测试集，只在附录做 stress analysis。

## 生产规则

后续生产数据时只从 `main_pool` 和高质量 `strict_gate` 中补量。`extension` 不用于补数量，`stress_slice` 不用于平衡 domain，也不能用于填补科学概念不足。

每条 pass 样本必须记录：

- 为什么该答案不是普通视频理解；
- 为什么静帧不能唯一判断；
- 需要观察哪些时序阶段；
- 同域近邻负例应该是什么。
