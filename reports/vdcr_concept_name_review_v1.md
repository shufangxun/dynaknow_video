# VDCR v1 Concept Name Review

Date: 2026-06-06

## Review Standard

This review checks whether each candidate name is a valid VDCR target concept rather than generic video understanding.

A strong VDCR concept should satisfy all of the following:

- The label is a recognized specialized term, not a surface action or event description.
- The visual evidence must be temporal: stage order, trajectory, rhythm, propagation, morphology change, instability, or feedback matters.
- The label carries a mechanism, strategy, or formal technique boundary.
- A nearby hard-negative concept can be constructed.
- Static object, scene, or one-frame posture cues should not be sufficient.

## Overall Verdict

The current inventory is directionally sound. Most physics, chemistry/materials, plant/cell biology, storm, volcanic, sediment, and geomorphology concepts fit VDCR well.

The remaining risk is not the first-level domain design. The risk is concept granularity. Some entries still look like named but broad visible events, some human/sport entries are too close to action recognition, and some earth-system entries require long-timescale or instrumented evidence that may be hard to turn into clean 3-10 second clips.

Current generated inventory stats after the 2026-06-06 cleanup:

| Field | Count |
|---|---:|
| Total concepts | 245 |
| Natural dynamic mechanisms | 202 |
| Specialized dynamic action concepts | 29 |
| Experimental dynamic patterns | 11 |
| Ecological behavior strategies | 3 |
| Heuristic priority A | 66 |
| Heuristic priority B | 156 |
| Heuristic priority C | 23 |

## Strong Concept Families

These families are conceptually strong and should form the backbone of v1:

| Domain | Family | Reason |
|---|---|---|
| 自然物理规律 | 流体不稳定性与涡动力学 | Names such as Kelvin-Helmholtz instability, Rayleigh-Taylor instability, Karman vortex street encode specific temporal instabilities. |
| 自然物理规律 | 表面张力与界面动力学 | Breakup, pinch-off, coalescence, Leidenfrost motion, Marangoni flow are video-native and mechanism-bearing. |
| 自然物理规律 | 波动、振动与非线性动力学 | Faraday waves, parametric resonance, coupled synchronization, double pendulum chaos require temporal phase/trajectory evidence. |
| 自然物理规律 | 刚体与颗粒动力学 | Dzhanibekov effect, gyroscopic precession, Brazil nut effect, granular convection are strong named dynamic concepts. |
| 物质变化机制 | 反应动力学与振荡反应 | Iodine clock, BZ reaction, Briggs-Rauscher reaction, Benedict positive reaction are named experimental dynamics, not just color change. |
| 物质变化机制 | 晶体、沉淀、电化学生长 | Dendritic growth, Liesegang rings, chemical garden growth, electrodeposition dendrites are good temporal formation concepts. |
| 生命过程机制 | 植物趋性、感性与快速运动 | Phototropism, gravitropism, thigmonasty, nyctinasty, tendril coiling are proper biological dynamic mechanisms. |
| 生命过程机制 | 细胞运动、细胞骨架、囊泡运输 | Chemotaxis, cytoplasmic streaming, mitotic segregation, axonal transport, microtubule dynamic instability are strong video knowledge terms. |
| 地球环境过程 | 大气风暴动力学 | Downburst outflow, mesocyclone rotation, tornadogenesis, gust front propagation require temporal evolution and domain knowledge. |
| 地球环境过程 | 火山、风沙、坡面侵蚀 | Pyroclastic density current, lava front advance, aeolian saltation, dune migration, gully headcut retreat are good named process labels. |

## Entries To Keep But Gate Strictly

These are acceptable only if the video and question construction enforce the temporal and expert-name requirements.

| Concept | Recommendation |
|---|---|
| Droplet Rebound | Keep as B. Must contrast against spreading, splash, coalescence, and impact spreading; otherwise it becomes "a drop bounced." |
| Spray Atomization | Keep only if the visible process is a named atomization mode; otherwise revise to a more specific breakup mechanism. |
| Wave Breaking | Revise to subtypes such as plunging breaker, spilling breaker, or surging breaker if used as a final answer. |
| Longshore Drift | Keep only with tracer/sediment motion evidence; a coastline still or oblique wave angle is too shortcut-heavy. |
| Fire Whirl | Keep as A/B depending on clip. Avoid clips where a single frame already clearly shows a fire tornado-like column. |
| Ice Cliff Calving | Keep as B. Use clips where fracture propagation and detachment are visible; avoid generic "ice falls into water" naming. |
| Wall Cloud Rotation / Tornadogenesis / Landspout Development | Keep, but require meteorological evidence and nearby storm distractors. |
| Cutbank Erosion / Point-Bar Deposition | Keep for time-lapse, model, or tracer clips only; static aerial imagery is insufficient. |

## Entries That Need Renaming Or Reframing

| Current concept | Issue | Suggested handling |
|---|---|---|
| Dynamic Mimicry | Too broad and not stable enough as a direct-answer label. | Replace with a specific named behavior or defer until a stable contrast set is defined. |
| Spray Atomization | Too broad as a final answer. | Split into Rayleigh breakup, air-blast atomization, sheet breakup, or ligament breakup if video sources exist. |
| Wave Breaking | Too generic. | Split into plunging breaker, spilling breaker, surging breaker. |
| Landslide Initiation | Broad event label. | Prefer retrogressive slump failure, rotational slide, debris-flow surge propagation, or progressive slope failure. |
| Stretch-Shortening Cycle | Mechanism is real, but hard to identify from ordinary video alone. | Move to "human movement biomechanics mechanisms" and require paired eccentric-to-concentric evidence. |
| Countermovement Jump | Formal sport-science term, but close to generic jumping. | Keep only with contrast against squat jump/drop jump, or defer. |
| Grand Jete | Formal dance term, but a peak-frame shortcut may be strong. | Downgrade or require full takeoff-flight-landing sequence with hard dance-technique distractors. |
| Pirouette | Formal dance term, but may be ordinary spin recognition. | Keep only with dance-technique contrast, lower priority than Fouette Turn. |
| Dolphin Kick | Too close to visible swimming action unless contrasted with flutter/breaststroke kick. | Downgrade; use only with underwater full-cycle footage. |
| Eggbeater Kick | More specialized than dolphin kick, but needs clear leg-cycle visibility. | Keep as B with strict clip requirement. |

## Human And Ball-Sport Concepts

Human specialized movement can stay in VDCR, but it should be a minority slice. It is valuable because it tests "dynamic specialized action concepts", but too much of it will make the benchmark look like sports action recognition.

Recommended rule:

- Cap human/sport specialized concepts at 10-15% of v1.
- Prefer concepts with formal scoring/coaching nomenclature and multi-stage temporal signatures.
- Avoid entries solvable by scene, object, uniform, or one iconic posture.
- Ball-sport team tactics are stronger than simple dribbles because they require multi-agent temporal structure.

Current ball-sport concepts that are strongest:

| Concept | Verdict |
|---|---|
| Spain Action | Strong if screen, roll/pop, and back-screen sequence is visible. |
| Elevator Screen | Strong multi-agent temporal gate structure. |
| Hammer Action | Strong if baseline drive, weak-side screen, and corner release are visible. |
| Floppy Action | Strong multi-screen off-ball route. |
| Iverson Cut | Strong if cross-court off-ball cut across high screens is visible. |
| UCLA Cut | Strong if entry pass and back-cut sequence is visible. |
| Ram Screen | Strong if pre-screen into ball-screen sequence is visible. |
| Spain Back Screen | Strong if the back-screen on the roller is visible. |

Current ball-sport concepts that are acceptable but lower priority and should remain capped:

| Concept | Verdict |
|---|---|
| Elastico / Flip Flap | Named technique; keep if foot-ball reversal sequence is visible. |
| Marseille Turn / Roulette | Named technique; keep if full turn and ball shield path are visible. |
| Cruyff Turn | Named technique; keep if fake-cross and behind-leg pullback are visible. |
| Rainbow Flick | Named technique; keep but may be easy from iconic posture. |

Current ball-sport concepts removed from the v1 main pool:

| Concept | Verdict |
|---|---|
| Trivela | Foot/body posture and ball curve make it prone to generic football-skill recognition; not enough temporal knowledge for v1. |
| Dribble Handoff | Too close to ordinary pass/ball exchange unless embedded in a richer named play. |
| Step-back Jumper | Too common and too close to ordinary basketball move recognition. |
| Pick and Roll / Pick and Pop | Foundational tactic, but too broad as a direct VDCR answer; use richer named variants such as Spain Action. |
| Rabona | Static crossed-leg posture is a strong shortcut. |
| La Croqueta | Often collapses into ordinary lateral dribble recognition. |

Current human movement concepts removed from the v1 main pool:

| Concept | Verdict |
|---|---|
| Spinning Back Kick | Named technique, but too close to visually obvious single-person action recognition for this benchmark. |
| Ollie | Formal skateboarding term, but often solvable from a familiar pop-jump pattern and board context. |

## Defer Or Low-Priority Families

The following are not necessarily wrong, but should not drive v1 collection before stronger concepts are saturated:

| Family | Reason |
|---|---|
| Long-timescale glacier mechanics | Glacier creep and basal sliding are scientifically valid but hard to verify in short raw video without labels, time-lapse, or instrumentation. |
| Instrumented microscopic/material processes | Corrosion pit growth, anodic oxide film growth, lithium dendrite growth, liquid crystal domain evolution may need lab microscopy or labeled demonstrations. |
| Highly specialized compressible-flow/EM plasma concepts | Prandtl-Meyer fans, shock-boundary-layer interaction, magnetic reconnection, plasma filamentation may depend on simulation or diagnostic visualization. |
| Broad developmental biology stages | Gastrulation and neural tube closure are valid, but direct-answer clips must avoid becoming labeled biological-animation recognition. |

## Recommended Release Policy

For v1 production, use a three-tier policy:

| Tier | Use |
|---|---|
| A | Main collection pool. Prioritize downloading, auditing, and final sample construction. |
| B | Collect opportunistically, then require stricter manual review. |
| C | Keep in inventory for future expansion; do not count toward v1 target unless high-quality videos are found. |

For final benchmark inclusion, each sample should carry these audit fields:

- `temporal_necessity_pass`
- `domain_specificity_pass`
- `static_shortcut_risk`
- `concept_granularity`
- `nearby_negative_family`
- `video_source_type`
- `text_or_overlay_leakage`
- `final_include`

## Practical Conclusion

The concept list is usable as a retrieval seed inventory, but not all 255 entries should be treated as equal final targets.

The strongest v1 core should be built from:

- physics instabilities, waves, droplets, particles;
- chemistry/materials reaction and pattern dynamics;
- plant/cell/micro biological mechanisms;
- storm, volcanic, sediment, wildfire, dune, and hydrology mechanisms;
- a small controlled slice of specialized human movement and team-tactic concepts.

The main cleanup before full-scale production is to demote or rewrite generic event names and keep sports/action concepts tightly bounded by formal temporal structure.
