# DynaKnow-Video v1 Taxonomy

Use this taxonomy to collect videos, assign labels, build answer choices, and audit benchmark coverage. The primary label must describe the knowledge mechanism demonstrated by the dynamic process, not the surface setting of the video.

## Label Structure

Each final item should have:

```text
domain
subdomain
visible_dynamic_phenomenon
knowledge_point
context_tags
dynamic_evidence_type
shortcut_risk_tags
```

Coverage statistics should be based on:

```text
domain + subdomain + canonical_knowledge_point
```

`context_tags` are secondary descriptors. For example, a household magnet demonstration is not an `everyday` domain item; it is `physics_physical_systems / electromagnetism_and_fields` with an `everyday_household_demo` context tag.

## Dynamic-Knowledge Gate

Accept a candidate only when the answer depends on visible temporal evidence:

- At least two time points or a continuous process are needed.
- A single frame cannot uniquely establish the knowledge point.
- The answer is a reusable mechanism, law, process, or phenomenon.
- The video evidence supports the mechanism without relying on title, source metadata, subtitles, or answer priors.

## Domain And Subdomain Principles

```text
domain = broad knowledge system
subdomain = mechanism family
knowledge_point = concrete mechanism instance
```

Subdomains must be mechanism families, not object types, video sources, or scene categories.

Good subdomains:

- `collisions_and_momentum`
- `redox_and_endpoint_reactions`
- `plant_growth_and_tropisms`

Bad subdomains:

- `apple_videos`
- `test_tube_videos`
- `household_demos`

Each subdomain should:

- support multiple distinct knowledge points,
- support hard negatives at the same specificity level,
- have visible dynamic signatures,
- be searchable through source categories or query terms,
- be stable enough for coverage statistics.

## Primary Domains

### 1. Physics and Physical Systems

Mechanisms involving motion, force, energy, fluids, pressure, fields, surfaces, heat transfer, waves, and physical stability.

Subdomains:

- `motion_forces_and_energy`: gravity, friction, drag, acceleration, mechanical energy, stability.
- `collisions_and_momentum`: contact-driven speed and direction changes, momentum transfer, rebound, energy loss.
- `oscillation_rotation_and_vibration`: pendula, torsion, coupled oscillators, rotation, vibration transfer.
- `fluids_pressure_and_buoyancy`: pressure gradients, siphons, buoyancy, displaced fluid, liquid columns.
- `surface_and_capillary_processes`: surface tension, capillary action, droplets, capillary breakup, wetting.
- `thermal_physical_response`: thermal expansion, thermal deformation, heat-transfer-driven physical response.
- `electromagnetism_and_fields`: magnetic/electric fields producing motion, alignment, attraction, or torque.

Example knowledge points:

- Gravity causes unsupported objects near Earth to accelerate downward.
- Momentum transfer in collisions causes objects to change speed and direction after contact.
- In an elastic pendulum, energy transfers among kinetic, gravitational potential, and elastic potential energy, producing coupled oscillations.
- A height difference in a continuous liquid column creates a pressure imbalance that drives flow.
- Surface tension drives capillary breakup of liquid filaments into droplets.
- Differential thermal expansion causes bonded materials to bend when heated.

### 2. Chemistry and Materials Change

Mechanisms involving chemical reactions, phase transitions, diffusion, precipitation, crystallization, combustion, and material response.

Subdomains:

- `phase_change_and_crystallization`: melting, freezing, evaporation, condensation, crystal nucleation and growth.
- `redox_and_endpoint_reactions`: iodine-clock reactions, Benedict tests, oxidation-reduction endpoints, reaction color endpoints.
- `precipitation_and_solubility`: ion mixing, insoluble solid formation, solubility-driven precipitation.
- `gas_evolution_and_combustion`: acid-carbonate gas generation, combustion, ignition, flame extinction.
- `diffusion_mixing_and_transport`: diffusion, concentration-gradient transport, mixing dynamics in materials.
- `material_deformation_and_response`: material changes under heat, stress, hydration, or other visible conditions.

Example knowledge points:

- Melting occurs when solid water absorbs heat and changes into liquid water.
- In iodine-clock reactions, thiosulfate reduces iodine back to iodide, delaying the dark starch-iodine complex until thiosulfate is depleted.
- In Benedict's test, reducing sugars reduce copper(II) ions during heating, producing orange-red copper(I) oxide precipitate.
- Precipitation reactions form insoluble solids when ions from mixed solutions exceed solubility.
- Blowing on a candle extinguishes combustion by cooling and disrupting the flame zone.
- Crystallization occurs when dissolved material nucleates and grows into ordered solid crystals.

Chemistry samples must not use generic labels such as "some reactions change color" or "some mixtures produce bubbles." If the reaction class or material mechanism cannot be grounded by visible anchors plus allowed source context, reject or revise the candidate.

### 3. Biology and Living Systems

Mechanisms involving growth, tropisms, nastic movements, development, water relations, physiology, organism behavior, locomotion, and biological system models.

Subdomains:

- `plant_growth_and_tropisms`: phototropism, gravitropism, directional growth responses.
- `plant_nastic_movements`: photonasty, thigmonasty, touch-triggered or light-triggered plant movements without directional growth.
- `germination_and_development`: visible developmental stages such as radicle emergence and shoot emergence.
- `plant_water_relations_and_turgor`: visible plant-tissue or plant-cell water-state changes, including capillary absorption into tissue, osmosis-driven water loss or gain, turgor-pressure change, plasmolysis, wilting, recovery after watering, and directly visible stomatal or tissue-water dynamics.
- `animal_locomotion_and_biomechanics`: gait, joint cycles, muscle-driven motion, body mechanics.
- `organism_behavior_and_taxis`: phototaxis, chemotaxis, magnetotaxis, stimulus-directed organism behavior.

Example knowledge points:

- Plant shoots exhibit phototropism by growing toward a light source.
- Gravitropism reorients plant shoots after inclination through differential growth.
- Photonasty changes leaf position in response to light without requiring directional growth.
- Thigmonasty causes carnivorous plant tentacles or leaves to bend after contact with prey.
- Loss or recovery of turgor pressure visibly changes plant tissue rigidity and posture.
- Animal movement often uses repeated joint cycles.

Seed-germination clips are accepted only when the target knowledge point names a visible developmental stage or mechanism. "Seeds sprout over time" is a dynamic event description, not a strong knowledge point.

Plant-water clips are accepted only when the video visibly shows plant tissue or plant cells changing water state over time, such as droplet absorption into porous tissue, wilting from turgor loss, recovery after rehydration, plasmolysis, or directly visible water movement in plant structures. Do not use `plant_water_relations_and_turgor` for generic droplets rolling on leaves, lotus-effect wetting, ordinary capillary rise in non-plant apparatus, or source-only claims about xylem/transpiration when the video itself does not show the plant-water process. Those candidates should be relabeled to a physics/engineering surface or capillary subdomain, or rejected if the mechanism is hidden.

Legacy label note: older intermediate files may contain `plant_water_transport`. Treat it only as an alias of `plant_water_relations_and_turgor` during reporting or validation; do not use it as a v1 target subdomain or as a new retrieval seed.

### 4. Earth and Environmental Systems

Mechanisms involving atmospheric, hydrologic, geologic, cryospheric, ecological, and environmental dynamics.

Subdomains:

- `weather_and_atmospheric_dynamics`: clouds, wind, convection, precipitation, atmospheric circulation.
- `hydrology_and_flow_processes`: runoff, streamflow, flooding, infiltration, surface-water movement.
- `erosion_transport_and_deposition`: sediment erosion, particle transport, deposition, landscape reshaping.
- `geology_and_geophysical_change`: landslides, volcanic processes, geophysical models, terrain deformation.
- `cryosphere_and_seasonal_change`: glacier motion, snow/ice melt, freeze-thaw, seasonal physical change.
- `ecosystem_interactions`: predator-prey, pollination, habitat interactions, ecological movement or feedback.

Example candidate knowledge points:

- Wind can transport particles and reshape surface patterns.
- Flowing water can erode, transport, and deposit sediment.
- Saturated slopes can fail and move downslope as landslides.
- Freeze-thaw cycles can fracture material over time.
- Seasonal phenology drives leaf emergence, canopy growth, and leaf loss in deciduous trees.
- Predator-prey or pollinator-plant interactions can change movement and behavior patterns.

### 5. Engineering and Operational Systems

Mechanisms involving tools, machines, control, separation, sorting, process sequencing, precision, and operational cause-effect. This is not a bucket for arbitrary procedure videos; the video must visibly demonstrate a transferable operational principle.

Subdomains:

- `filtration_and_separation`: filtration, settling, density separation, sorting, granular segregation.
- `mixing_dispersion_and_wetting`: mixing, dispersion, wetting, surface preparation.
- `pressure_flow_and_process_control`: pressure release, pumping, valve operation, flow regulation, pressure sequencing.
- `thermal_process_control`: heating, cooling, thermal shock prevention, controlled temperature operations.
- `tooling_force_and_precision`: clamping, cutting, drilling, tightening, force distribution, stabilization.
- `machines_control_and_failure_modes`: machine actuation, feedback, failure modes, controlled mechanical operation.

Example knowledge points:

- A pressure gradient across filter media drives liquid through pores while retained solids remain behind.
- In the Brazil nut effect, vibration opens gaps that let smaller grains percolate downward, leaving larger particles on top.
- Gradual heating can reduce thermal shock.
- Venting before sealing can reduce pressure buildup.
- Sequential tightening can distribute force evenly.
- Repeated small adjustments can stabilize a system better than one large adjustment.

## Secondary Context Tags

Use context tags for acquisition and bias analysis, not as primary domains:

- `demonstration_experiment`
- `real_world_natural_event`
- `everyday_household_demo`
- `industrial_or_engineering_process`
- `time_lapse_process`
- `microscopic_or_closeup_process`
- `procedural_operation`
- `simulation_or_animation_diagnostic`

## v1 Sampling Scale

Recommended v1 scale:

- Minimum clean v1: 250 samples.
- Target clean v1: 310 samples.
- Review pool needed to reach target: roughly 800-1,200 candidates, assuming 25-40% pass rate after leakage, shortcut, visual-grounding, and mechanism-expression filters.

The subdomain skeleton has 31 subdomains. The minimum target is about 8 clean items per subdomain; the preferred target is about 10 clean items per subdomain. This gives enough coverage for per-domain reporting without letting the benchmark collapse into whichever videos are easiest to crawl.

Domain-level target allocation:

| Domain | Minimum | Target |
| --- | ---: | ---: |
| `physics_physical_systems` | 56 | 70 |
| `chemistry_materials_change` | 48 | 60 |
| `biology_living_systems` | 48 | 60 |
| `earth_environmental_systems` | 48 | 60 |
| `engineering_operational_systems` | 48 | 60 |

The first public v1 can be released at 250 clean samples if every primary domain and most subdomains are covered. The stronger target is 310 clean samples because it supports roughly 10 clean items per mechanism family.
