# VDCR v1 Concept Inventory

VDCR (Video Dynamic Concept Recognition) evaluates whether a multimodal model can recognize named, domain-specific dynamic concepts from continuous video evidence.

This inventory is a strict candidate pool for v1. It is not yet the final release list. Later passes should add priority labels such as `A/B/C`, video availability, source reliability, and static-shortcut risk.

For v1, the formal scope is limited to broad scientific dynamic concepts in natural physics, material change, living systems, and earth/environmental systems. `人造系统与操作` is intentionally deferred as a vertical extension because its concepts depend heavily on industrial context, instrumentation, and specialized manufacturing/robotics vocabularies. Patient-identifiable clinical motion signs are deferred from v1. Human specialized movement concepts are allowed only as a capped stress slice when the label has a formal movement taxonomy and a structured temporal signature. Ball-sport entries are deferred from v1 main production because they too easily shift the benchmark narrative toward sport action/play recognition.

## Core Definition

VDCR does not ask: **What visibly happens in this video?**

VDCR asks: **Which named dynamic concept does this temporally evolving process instantiate?**

In Chinese:

> VDCR 不评估模型是否能描述视频里发生了什么；它评估模型能否把连续时序证据对齐到一个由动态机制定义的专有概念标签。

This places VDCR under video-native knowledge rather than generic video understanding. Generic video understanding can often be solved by object, scene, action, or single-frame event cues. VDCR requires a model to map temporal evidence into a symbolic scientific or specialized concept.

The intended reasoning chain is:

1. **Temporal perception**: track motion, rhythm, phase order, propagation, instability, growth, feedback, or morphology change.
2. **Dynamic abstraction**: convert visible change into a dynamic structure such as oscillation, transport, instability, phase transition, tactic response, or named action sequence.
3. **Knowledge alignment**: match that structure to a named concept in a scientific, ecological, sport-technical, or specialized technical vocabulary.

## Admission Redlines

1. **Temporal Necessity**
   A random single frame must be insufficient for a domain expert to uniquely identify the concept. The answer must depend on trajectory, stage order, rhythm, morphology change, interaction, or feedback over time.

2. **Domain Specificity**
   The answer must be a scientific, technical, ecological, sport-technical, or otherwise formally named specialized concept. Generic everyday actions, object labels, species labels, and scene labels are excluded.

3. **Non-Generic Action Principle**
   VDCR may include actions, but it does not evaluate generic action recognition. Action-like concepts must have a formal naming system, static-frame insufficiency, structured temporal signature, and mechanism/strategy grounding.

4. **Mechanism-Bearing Label**
   Broad event names are insufficient when they only describe that something happened. The target label should encode a distinctive dynamic mechanism, phase sequence, instability, transport process, feedback loop, or named strategy.

5. **Expert Naming Gap**
   A layperson may be able to describe the visible surface event, but should not be expected to reliably name the target concept. This separates "snow is sliding" from `Slab Avalanche Release`, and "liquid changed color" from `Iodine Clock Reaction`.

6. **Distractor Viability**
   Multiple-choice distractors must be from nearby mechanisms or nearby concept families. The answer should not be solvable by eliminating obviously unrelated options.

## Rejection Patterns

Reject concepts when the label is mainly:

- a visible event: `iceberg rollover`, `snow avalanche`, `animal running`, `plant closing`;
- an object/species/scene label: `leopard`, `glacier`, `test tube`, `cloud`;
- a broad physical principle without a visually specific dynamic signature: `gravity`, `energy conservation`, `pressure`;
- a static pattern that can be named from one representative frame unless the video-specific task targets its formation sequence.

## Concept Types

| Type | Meaning |
|---|---|
| 自然动态机制 | Natural dynamic mechanism |
| 专有动态动作概念 | Dynamic specialized action concept |
| 实验动态图样 | Experimental dynamic pattern |
| 生态行为策略 | Ecological behavioral strategy |

## Candidate Concepts

| 一级 Domain | 二级术语族 | 中文专有动态概念 | 英文/别名 | 类型 |
|---|---|---|---|---|
| 自然物理规律 | 流体不稳定性与涡动力学 | 马格努斯效应 | Magnus Effect | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 周期涡脱落/卡门涡街 | Vortex Shedding / Karman Vortex Street | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 空化泡生长与塌缩 | Cavitation Bubble Growth and Collapse | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 开尔文-亥姆霍兹不稳定性 | Kelvin-Helmholtz Instability | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 瑞利-泰勒不稳定性 | Rayleigh-Taylor Instability | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 萨夫曼-泰勒黏性指进 | Saffman-Taylor Viscous Fingering | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 泰勒-库埃特涡 | Taylor-Couette Vortices | 自然动态机制 |
| 自然物理规律 | 流体不稳定性与涡动力学 | 水跃 | Hydraulic Jump | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 瑞利-普拉托断裂 | Rayleigh-Plateau Breakup | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 毛细上升/芯吸 | Capillary Rise / Wicking | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 液滴并合 | Droplet Coalescence | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 毛细断裂 | Capillary Breakup | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 液桥颈缩断裂 | Liquid Bridge Pinch-Off | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 莱顿弗罗斯特液滴运动 | Leidenfrost Droplet Motion | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 马兰戈尼驱动流 | Marangoni-Driven Flow | 自然动态机制 |
| 自然物理规律 | 表面张力与界面动力学 | 接触线钉扎-脱钉 | Contact-Line Pinning and Depinning | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 驻波形成 | Standing Wave Formation | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 波的相干干涉 | Coherent Wave Interference | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 法拉第波 | Faraday Waves | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 参数共振 | Parametric Resonance | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 耦合摆同步 | Coupled Pendulum Synchronization | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 阻尼振荡 | Damped Oscillation | 自然动态机制 |
| 自然物理规律 | 波动、振动与非线性动力学 | 双摆混沌 | Double Pendulum Chaos | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 陀螺进动 | Gyroscopic Precession | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 贾尼别科夫效应/网球拍定理 | Dzhanibekov Effect / Tennis Racket Theorem | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 欧拉圆盘运动 | Euler's Disk Motion | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 弹性摆运动 | Elastic Pendulum Motion | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 巴西坚果效应 | Brazil Nut Effect | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 颗粒对流 | Granular Convection | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 颗粒表面雪崩 | Granular Surface Avalanche | 自然动态机制 |
| 自然物理规律 | 刚体与颗粒动力学 | 黏滑运动 | Stick-Slip Motion | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 冠状飞溅 | Crown Splash | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 沃辛顿射流 | Worthington Jet | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 液滴反弹 | Droplet Rebound | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 液滴铺展-回缩 | Droplet Spreading and Retraction | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 液滴撞击铺展 | Droplet Impact Spreading | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 液丝破碎雾化 | Ligament-Mediated Atomization | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 气泡破裂射流 | Bubble-Bursting Jet | 自然动态机制 |
| 自然物理规律 | 液滴冲击、喷射与飞溅 | 涡环形成 | Vortex Ring Formation | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 激波传播 | Shock Wave Propagation | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 马赫锥形成 | Mach Cone Formation | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 弓形激波 | Bow Shock | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 普朗特-迈耶膨胀扇 | Prandtl-Meyer Expansion Fan | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 爆轰波前传播 | Detonation Front Propagation | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 瑞利-泰勒冲击混合 | Shock-Driven Rayleigh-Taylor Mixing | 自然动态机制 |
| 自然物理规律 | 压缩流与冲击波 | 激波-边界层相互作用 | Shock-Boundary-Layer Interaction | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 磁场重联 | Magnetic Reconnection | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 等离子体丝化 | Plasma Filamentation | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 辉光放电扩展 | Glow Discharge Propagation | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 电弧形成与弯曲 | Electric Arc Formation and Bending | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 介质阻挡放电流光 | Dielectric Barrier Discharge Streamers | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 太阳日珥喷发 | Solar Prominence Eruption | 自然动态机制 |
| 自然物理规律 | 电磁与等离子体动态 | 日冕物质抛射 | Coronal Mass Ejection | 自然动态机制 |
| 自然物理规律 | 热过程与浮力驱动流 | 自然对流羽流 | Natural Convection Plume | 自然动态机制 |
| 自然物理规律 | 热过程与浮力驱动流 | 瑞利-贝纳德对流 | Rayleigh-Benard Convection | 自然动态机制 |
| 自然物理规律 | 热过程与浮力驱动流 | 沸腾气泡成核与脱离 | Boiling Bubble Nucleation and Departure | 自然动态机制 |
| 自然物理规律 | 热过程与浮力驱动流 | 膜态沸腾 | Film Boiling | 自然动态机制 |
| 自然物理规律 | 热过程与浮力驱动流 | 热毛细对流 | Thermocapillary Convection | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 剪切增稠 | Shear Thickening | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 剪切变稀 | Shear Thinning | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 触变性 | Thixotropy | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 黏弹回弹 | Viscoelastic Recoil | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 宾汉屈服流动 | Bingham Yield Flow | 自然动态机制 |
| 物质变化机制 | 流变与非牛顿响应 | 魏森贝格爬杆效应 | Weissenberg Rod-Climbing Effect | 自然动态机制 |
| 物质变化机制 | 晶体生长与相变前沿 | 晶核形成 | Crystal Nucleation | 自然动态机制 |
| 物质变化机制 | 晶体生长与相变前沿 | 树枝状晶体生长 | Dendritic Crystal Growth | 自然动态机制 |
| 物质变化机制 | 晶体生长与相变前沿 | 球晶生长 | Spherulitic Growth | 自然动态机制 |
| 物质变化机制 | 晶体生长与相变前沿 | 结晶前沿推进 | Crystallization Front Propagation | 自然动态机制 |
| 物质变化机制 | 晶体生长与相变前沿 | 过冷液体瞬时结晶 | Supercooled Liquid Rapid Crystallization | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 碘钟反应 | Iodine Clock Reaction | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 蓝瓶反应 | Blue Bottle Reaction | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 化学交通灯反应 | Chemical Traffic Light Reaction | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 别洛乌索夫-扎鲍廷斯基振荡反应 | Belousov-Zhabotinsky Reaction | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 布里格斯-劳舍尔振荡反应 | Briggs-Rauscher Reaction | 实验动态图样 |
| 物质变化机制 | 反应动力学与振荡反应 | 本尼迪克特阳性还原反应 | Benedict Positive Reducing-Sugar Reaction | 实验动态图样 |
| 物质变化机制 | 沉淀、自组织与扩散前沿 | 化学花园生长 | Chemical Garden Growth | 实验动态图样 |
| 物质变化机制 | 沉淀、自组织与扩散前沿 | 沉淀前沿推进 | Precipitation Front Propagation | 自然动态机制 |
| 物质变化机制 | 沉淀、自组织与扩散前沿 | 利塞冈环形成 | Liesegang Ring Formation | 实验动态图样 |
| 物质变化机制 | 沉淀、自组织与扩散前沿 | 反应-扩散波 | Reaction-Diffusion Wave | 自然动态机制 |
| 物质变化机制 | 界面输运与沉积 | 表面活性剂驱动液滴运动 | Surfactant-Driven Droplet Motion | 自然动态机制 |
| 物质变化机制 | 界面输运与沉积 | 咖啡环形成 | Coffee-Ring Formation | 自然动态机制 |
| 物质变化机制 | 界面输运与沉积 | 蒸发诱导沉积前沿 | Evaporation-Induced Deposition Front | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 旋节线分解 | Spinodal Decomposition | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 奥斯特瓦尔德熟化 | Ostwald Ripening | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 液滴聚并粗化 | Coalescence-Driven Coarsening | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 液膜退润湿 | Thin-Film Dewetting | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 成核与生长相分离 | Nucleation-and-Growth Phase Separation | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 冻结诱导相分离 | Freeze-Induced Phase Separation | 自然动态机制 |
| 物质变化机制 | 相分离与粗化动力学 | 相界面迁移 | Phase Boundary Migration | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 火焰前沿传播 | Flame Front Propagation | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 扩散火焰 | Diffusion Flame | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 预混火焰传播 | Premixed Flame Propagation | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 火焰胞状不稳定性 | Cellular Flame Instability | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 火焰闪回 | Flame Flashback | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 火焰吹熄 | Flame Blowoff | 自然动态机制 |
| 物质变化机制 | 燃烧与反应前沿 | 振荡火焰 | Oscillating Flame | 自然动态机制 |
| 物质变化机制 | 电化学与腐蚀动态 | 电沉积枝晶生长 | Electrodeposition Dendrite Growth | 自然动态机制 |
| 物质变化机制 | 电化学与腐蚀动态 | 金属置换枝晶生长 | Metal Displacement Dendrite Growth | 实验动态图样 |
| 物质变化机制 | 电化学与腐蚀动态 | 电解气泡成核与脱离 | Electrolysis Bubble Nucleation and Detachment | 自然动态机制 |
| 物质变化机制 | 电化学与腐蚀动态 | 腐蚀坑扩展 | Corrosion Pit Growth | 自然动态机制 |
| 物质变化机制 | 电化学与腐蚀动态 | 阳极氧化膜生长 | Anodic Oxide Film Growth | 自然动态机制 |
| 物质变化机制 | 电化学与腐蚀动态 | 锂枝晶生长 | Lithium Dendrite Growth | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 凝胶化前沿推进 | Gelation Front Propagation | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 聚合收缩前沿 | Polymerization Shrinkage Front | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 凝胶溶胀 | Gel Swelling | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 凝胶去溶胀塌缩 | Gel Deswelling Collapse | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 液晶相畴演化 | Liquid Crystal Domain Evolution | 自然动态机制 |
| 物质变化机制 | 凝胶、聚合物与软物质 | 液晶缺陷湮灭 | Liquid Crystal Defect Annihilation | 自然动态机制 |
| 生命过程机制 | 动物运动机制与生态策略 | C 型快速逃逸反应 | C-Start Escape Response | 专有动态动作概念 |
| 生命过程机制 | 动物运动机制与生态策略 | 水母伞体收缩喷射推进 | Medusan Bell-Contraction Jet Propulsion | 自然动态机制 |
| 生命过程机制 | 动物运动机制与生态策略 | 鳗鲡式波状推进 | Anguilliform Undulation | 自然动态机制 |
| 生命过程机制 | 动物运动机制与生态策略 | 节律相位波推进 | Metachronal Wave Locomotion | 自然动态机制 |
| 生命过程机制 | 动物运动机制与生态策略 | 泡泡网捕食 | Bubble-Net Feeding | 生态行为策略 |
| 生命过程机制 | 动物运动机制与生态策略 | 泥环捕食 | Mud-Ring Feeding | 生态行为策略 |
| 生命过程机制 | 动物运动机制与生态策略 | 鸟群群舞 | Murmuration | 生态行为策略 |
| 生命过程机制 | 人体专项动作与运动技术 | 阿克塞尔跳 | Axel Jump | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 后内结环跳 | Salchow Jump | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 后外点冰跳 | Toe Loop Jump | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 尤尔琴科跳马 | Yurchenko Vault | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 月面空翻 | Tsukahara Vault | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 科瓦奇腾越 | Kovacs Release | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 背越式跳高 | Fosbury Flop | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 芭蕾挥鞭转 | Fouette Turn | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 一本背负投 | Ippon Seoi Nage | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 内股投 | Uchi Mata | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 大外刈 | Osoto Gari | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 巴投 | Tomoe Nage | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 爱斯基摩翻滚 | Eskimo Roll / Kayak Roll | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 踩水蛋打腿 | Eggbeater Kick | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 冲浪底转 | Surfing Bottom Turn | 专有动态动作概念 |
| 生命过程机制 | 人体专项动作与运动技术 | 滑雪刻滑转弯 | Carving Turn | 专有动态动作概念 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 向光性 | Phototropism | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 向重性 | Gravitropism | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 向水性 | Hydrotropism | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 感触性运动 | Thigmonasty | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 感震性运动 | Seismonasty | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 昼夜感性运动 | Nyctinasty | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 卷须旋转探寻 | Tendril Circumnutation | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 卷须缠绕 | Tendril Coiling | 自然动态机制 |
| 生命过程机制 | 植物趋性、感性与快速运动 | 双稳态捕虫夹闭合 | Bistable Snap-Trap Closure | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 变形虫式趋化爬行 | Amoeboid Chemotactic Crawling | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 细胞质流动 | Cytoplasmic Streaming | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 有丝分裂染色体分离 | Mitotic Chromosome Segregation | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 胞质分裂沟收缩 | Cytokinetic Furrow Ingression | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 中性粒细胞趋化 | Neutrophil Chemotaxis | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 轴突运输 | Axonal Transport | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 纤毛节律摆动 | Ciliary Beating | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 钙波传播 | Calcium Wave Propagation | 自然动态机制 |
| 生命过程机制 | 细胞运动与显微动态 | 光漂白后荧光恢复 | FRAP Recovery | 实验动态图样 |
| 生命过程机制 | 细胞运动与显微动态 | 线粒体分裂-融合动态 | Mitochondrial Fission-Fusion Dynamics | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 胞吞作用 | Endocytosis | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 胞吐作用 | Exocytosis | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 吞噬作用 | Phagocytosis | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 囊泡出芽 | Vesicle Budding | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 囊泡融合 | Vesicle Fusion | 自然动态机制 |
| 生命过程机制 | 细胞膜与囊泡运输 | 胞饮作用 | Pinocytosis | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 微管动态不稳定性 | Microtubule Dynamic Instability | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 肌动蛋白波 | Actin Wave | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 片状伪足延伸 | Lamellipodium Extension | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 丝状伪足探伸 | Filopodium Protrusion | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 细胞收缩环收缩 | Actomyosin Contractile Ring Constriction | 自然动态机制 |
| 生命过程机制 | 细胞骨架与细胞形变 | 细胞膜起泡 | Membrane Blebbing | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 胚胎卵裂分裂序列 | Embryonic Cleavage Division Sequence | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 原肠胚形成 | Gastrulation | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 汇聚延伸运动 | Convergent Extension | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 神经管闭合 | Neural Tube Closure | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 上皮-间质转化 | Epithelial-Mesenchymal Transition | 自然动态机制 |
| 生命过程机制 | 发育与形态发生动态 | 组织内陷 | Tissue Invagination | 自然动态机制 |
| 生命过程机制 | 植物细胞与器官动态响应 | 气孔开闭 | Stomatal Opening and Closing | 自然动态机制 |
| 生命过程机制 | 植物细胞与器官动态响应 | 叶绿体光定位运动 | Chloroplast Photorelocation Movement | 自然动态机制 |
| 生命过程机制 | 植物细胞与器官动态响应 | 花粉管趋化生长 | Pollen Tube Chemotropic Growth | 自然动态机制 |
| 生命过程机制 | 植物细胞与器官动态响应 | 根毛极性生长 | Root Hair Tip Growth | 自然动态机制 |
| 生命过程机制 | 植物细胞与器官动态响应 | 质壁分离与复原 | Plasmolysis and Deplasmolysis | 自然动态机制 |
| 生命过程机制 | 微生物与群体动力学 | 细菌趋化游动 | Bacterial Chemotaxis | 自然动态机制 |
| 生命过程机制 | 微生物与群体动力学 | 细菌集群运动 | Bacterial Swarming Motility | 自然动态机制 |
| 生命过程机制 | 微生物与群体动力学 | 生物膜扩张 | Biofilm Expansion | 自然动态机制 |
| 生命过程机制 | 微生物与群体动力学 | 群体感应波 | Quorum-Sensing Wave | 自然动态机制 |
| 生命过程机制 | 微生物与群体动力学 | 黏菌聚集 | Slime Mold Aggregation | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 下击暴流出流扩散 | Downburst / Microburst Outflow | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 超级单体中气旋旋转 | Supercell Mesocyclone Rotation | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 龙卷生成 | Tornadogenesis | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 墙云旋转 | Wall Cloud Rotation | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 阵风锋推进 | Gust Front Propagation | 自然动态机制 |
| 地球环境过程 | 大气风暴动力学 | 陆龙卷发展 | Landspout Development | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 曲流河裁弯取直 | Meander Neck Cutoff | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 凹岸侵蚀与凸岸沉积 | Cutbank Erosion / Point-Bar Deposition | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 河流决口改道 | River Avulsion | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 辫状河道迁移 | Braided Channel Migration | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 泥沙跃移 | Sediment Saltation | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 浊流推进 | Turbidity Current Propagation | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 裂流出海通道形成 | Rip Current Channel Formation | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 沿岸漂移 | Longshore Drift | 自然动态机制 |
| 地球环境过程 | 水文、河流与海岸动力学 | 内波传播 | Internal Wave Propagation | 自然动态机制 |
| 地球环境过程 | 地质变形与质量流失稳 | 断层破裂传播 | Fault Rupture Propagation | 自然动态机制 |
| 地球环境过程 | 地质变形与质量流失稳 | 旋转滑塌 | Rotational Slump Failure | 自然动态机制 |
| 地球环境过程 | 地质变形与质量流失稳 | 土壤液化 | Seismic Soil Liquefaction | 自然动态机制 |
| 地球环境过程 | 地质变形与质量流失稳 | 后退式滑塌 | Retrogressive Slump Failure | 自然动态机制 |
| 地球环境过程 | 地质变形与质量流失稳 | 泥石流脉冲推进 | Debris-Flow Surge Propagation | 自然动态机制 |
| 地球环境过程 | 火山与熔岩动力学 | 火山碎屑密度流 | Pyroclastic Density Current | 自然动态机制 |
| 地球环境过程 | 火山与熔岩动力学 | 绳状熔岩形成 | Pahoehoe Lava Roping | 自然动态机制 |
| 地球环境过程 | 火山与熔岩动力学 | 阿阿熔岩前缘推进 | Aa Lava Front Advance | 自然动态机制 |
| 地球环境过程 | 火山与熔岩动力学 | 熔岩穹丘崩塌 | Lava Dome Collapse | 自然动态机制 |
| 地球环境过程 | 火山与熔岩动力学 | 喷发柱坍塌 | Eruption Column Collapse | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 冰川塑性蠕变 | Glacier Creep | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 冰川基底滑动 | Basal Sliding | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 冰裂隙扩展 | Crevasse Propagation | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 冰崖崩解 | Ice Cliff Calving | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 板状雪崩释放 | Slab Avalanche Release | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 雪板冠状裂缝传播 | Snow Slab Crown Crack Propagation | 自然动态机制 |
| 地球环境过程 | 冰冻圈与冰川动力学 | 冰川跃动 | Glacier Surge | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 火旋风涡旋形成 | Fire-Whirl Vortex Formation | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 树冠火转变 | Crown Fire Transition | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 飞火传播 | Spot Fire Propagation | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 烟羽对流上升 | Convective Smoke Plume Rise | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 阵风驱动火线推进 | Wind-Driven Fire-Front Propagation | 自然动态机制 |
| 地球环境过程 | 野火与烟羽动力学 | 火积云发展 | Pyrocumulus Development | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 沙粒跃移 | Aeolian Saltation | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 风成波纹形成 | Aeolian Ripple Formation | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 新月形沙丘迁移 | Barchan Dune Migration | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 沙丘雪崩面滑移 | Dune Slip-Face Avalanche | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 尘暴锋面推进 | Dust Storm Front Propagation | 自然动态机制 |
| 地球环境过程 | 风沙与沙丘动力学 | 风沙流分选 | Aeolian Granular Sorting | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 卷破波 | Plunging Breaker | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 潮汐涌浪 | Tidal Bore | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 风暴潮推进 | Storm Surge Propagation | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 近岸裂流形成 | Rip Current Formation | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 波浪折射 | Wave Refraction | 自然动态机制 |
| 地球环境过程 | 海洋波浪与海岸过程 | 海蚀崖后退 | Sea-Cliff Retreat | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 沟蚀扩展 | Gully Headcut Retreat | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 溯源侵蚀 | Headward Erosion | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 三角洲分流改道 | Delta Lobe Avulsion | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 海岸沙嘴延伸 | Spit Progradation | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 冲沟网络扩展 | Rill Network Expansion | 自然动态机制 |
| 地球环境过程 | 坡面侵蚀与地貌演化 | 泥沙重力流分层 | Stratified Sediment Gravity Flow | 自然动态机制 |

## Explicitly Deferred Or Removed

The following patterns are intentionally not part of the v1 candidate table:

- `人造系统与操作`: deferred to a future vertical engineering benchmark.
- `临床运动体征与步态`: deferred because patient-identifiable clinical video carries privacy, consent, and ethics risks.
- `球类专项动作与战术序列`: deferred from v1 main production because even named tricks and tactics are likely to be read as sport action/play recognition rather than video-native scientific knowledge.
- Narrow single-sport technique pools are deferred. Human specialized movement concepts are allowed only when they are spread across multiple formal systems such as skating, gymnastics, dance, martial arts, water sports, and board sports.
- Basic or shortcut-heavy ball-sport skills such as `Trivela`, `Dribble Handoff`, `Step-back Jumper`, `Pick and Roll`, `Pick and Pop`, `Rabona`, and `La Croqueta` are excluded from v1 because they are either too dependent on generic play recognition or do not require enough specialized dynamic knowledge.
- `冰山翻滚 / Iceberg Rollover`: too close to visible event recognition.
- `雪崩释放 / Snow Avalanche Release`: replaced by `板状雪崩释放 / Slab Avalanche Release`.
- `冰川流动 / Glacier Flow`: replaced by `冰川塑性蠕变` and `冰川基底滑动`.
- `冰川崩解 / Glacier Calving`: replaced by the more mechanism-bearing `冰崖崩解 / Ice Cliff Calving`.
- `侧向蛇行 / Sidewinding Locomotion`, `蠕动式运动 / Peristaltic Locomotion`, `翻正反射 / Righting Reflex`, `弹跳炫耀 / Stotting`: too close to visible action recognition unless a specific research-grade video and contrast set proves mechanism-level necessity.
- Object/species-plus-action labels such as `捕蝇草闭合`, `猎豹奔跑`, `螳螂虾击打`: rejected unless rewritten as a formal dynamic mechanism with a stable expert label.
- Broad or shortcut-prone movement labels such as `Dynamic Mimicry`, `Countermovement Jump`, `Stretch-Shortening Cycle`, `Pirouette`, `Grand Jete`, `Dolphin Kick`, `Spinning Back Kick`, and `Ollie`: removed from v1 unless a stricter formal contrast set is defined.
- Broad event labels such as `Spray Atomization`, `Landslide Initiation`, and `Wave Breaking`: replaced by more mechanism-bearing targets such as `Ligament-Mediated Atomization`, `Rotational Slump Failure`, and `Plunging Breaker`.
