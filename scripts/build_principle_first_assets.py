#!/usr/bin/env python3
"""Build principle-first assets for the dynamic video benchmark.

This script is intentionally offline and deterministic. It creates:
- a principle inventory that drives retrieval;
- Commons/search query rows derived from each principle;
- a rough coverage map from the current candidate release to principles;
- a review HTML page for discussing the new workflow.
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "principle_first_v1"

INVENTORY_OUT = DATA / "principle_inventory_v1.csv"
QUERY_OUT = DATA / "principle_search_queries_v1.csv"
SCHEMA_OUT = DATA / "principle_inventory_schema_v1.json"
MAPPING_OUT = DATA / "principle_existing_release_mapping_v1.csv"
REPORT_OUT = REPORT / "index.html"

CURRENT_RELEASE = ROOT / "release" / "v1_1_mechanism_principle_pass_only" / "eval.jsonl"

DOMAIN_ALIASES = {
    "engineering_operational_systems": "engineered_systems_and_operations",
}


FIELDS = [
    "principle_id",
    "domain",
    "subdomain",
    "principle",
    "required_dynamic_signature",
    "acceptable_video_types",
    "reject_conditions",
    "query_seed",
    "hard_negative_family",
    "priority",
]

QUERY_FIELDS = [
    "search_term",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "default_start_sec",
    "default_end_sec",
    "why_dynamic",
    "notes",
    "collector_notes",
]


def p(
    principle_id: str,
    domain: str,
    subdomain: str,
    principle: str,
    signature: str,
    video_types: str,
    reject: str,
    queries: str,
    negatives: str,
    priority: str = "core",
) -> dict[str, str]:
    return {
        "principle_id": principle_id,
        "domain": domain,
        "subdomain": subdomain,
        "principle": principle,
        "required_dynamic_signature": signature,
        "acceptable_video_types": video_types,
        "reject_conditions": reject,
        "query_seed": queries,
        "hard_negative_family": negatives,
        "priority": priority,
    }


INVENTORY: list[dict[str, str]] = [
    p("PHY_FOR_001", "physics_physical_systems", "motion_forces_and_energy", "Gravity produces downward acceleration when other forces are small.", "Frame-to-frame downward displacement increases or tracked velocity increases during fall.", "slow-motion free-fall experiments; tracked falling objects", "Reject static falling-object images, title-only gravity claims, and clips where the object is already moving without visible acceleration.", "free fall acceleration slow motion|falling object increasing speed video|gravity acceleration experiment video", "constant velocity; buoyant rise; projectile horizontal component"),
    p("PHY_FOR_002", "physics_physical_systems", "motion_forces_and_energy", "Projectile motion combines nearly constant horizontal velocity with vertical gravitational acceleration.", "The object follows a parabolic arc or tracked trajectory with independent horizontal and vertical components.", "projectile demonstrations; ball toss slow motion; tracked motion analysis", "Reject clips without visible trajectory or where propulsion continues after launch.", "projectile motion parabolic trajectory slow motion|projectile motion tracking video|ball projectile motion experiment", "free fall only; powered flight; rolling on ramp"),
    p("PHY_FOR_003", "physics_physical_systems", "motion_forces_and_energy", "Friction dissipates mechanical energy and reduces sliding speed.", "Sliding object decelerates until rest or thermal/frictional effects are visible.", "sliding block experiments; friction demos with tracked speed", "Reject clips that only show a stationary rough surface or a single final rest state.", "friction deceleration sliding block experiment|sliding object slows down due to friction video", "air drag; elastic collision; rolling without slip"),
    p("PHY_COL_001", "physics_physical_systems", "collisions_and_momentum", "Momentum transfer in contact collisions redistributes velocity and direction.", "Pre- and post-impact velocities/directions of colliding bodies visibly change.", "billiard balls; carts; Newton cradle with tracked motion", "Reject impacts without clear before/after motion or pure text diagrams.", "momentum transfer collision slow motion|two cart collision momentum video|Newton cradle momentum transfer video", "friction slowing; gravitational fall; fluid drag"),
    p("PHY_COL_002", "physics_physical_systems", "collisions_and_momentum", "Inelastic collisions dissipate kinetic energy through deformation, heat, sound, or sticking.", "Objects deform, stick, fragment, or rebound with lower speed after impact.", "clay cart collisions; crash slow motion; deformable impact videos", "Reject elastic rebounds with no visible energy loss.", "inelastic collision deformation slow motion|clay collision sticking video|crash kinetic energy deformation video", "elastic collision; fracture only; free fall"),
    p("PHY_OSC_001", "physics_physical_systems", "oscillation_rotation_and_vibration", "A pendulum exchanges gravitational potential energy and kinetic energy over each swing.", "Speed is highest near the bottom and lowest near the turning points over repeated cycles.", "pendulum slow motion; tracked pendulum motion", "Reject static pendulum images or clips without at least one full swing.", "pendulum energy transfer slow motion|pendulum kinetic potential energy video", "linear fall; rotating disk; fluid wave"),
    p("PHY_OSC_002", "physics_physical_systems", "oscillation_rotation_and_vibration", "Damping dissipates oscillator energy, causing amplitude decay over time.", "Oscillation amplitude shrinks across cycles.", "mass-spring damping; pendulum damping; torsion oscillator", "Reject clips where amplitude is externally held constant.", "damped oscillation amplitude decay video|damped pendulum time lapse|spring mass damping experiment", "resonance growth; chaotic pendulum; constant forced oscillation"),
    p("PHY_OSC_003", "physics_physical_systems", "oscillation_rotation_and_vibration", "Resonance amplifies motion when periodic forcing matches a natural frequency.", "Amplitude grows under a repeated external drive near the resonant frequency.", "driven pendulum; resonance table; vibrating structure experiments", "Reject videos that only show large vibration without a drive-frequency relation.", "resonance amplitude growth experiment video|driven oscillator resonance video|mechanical resonance slow motion", "damping decay; collision rebound; random vibration"),
    p("PHY_FLU_001", "physics_physical_systems", "fluids_pressure_and_buoyancy", "Bernoulli/Venturi flow couples higher speed through a constriction with lower static pressure.", "Manometer/liquid column or pressure indicator changes when flow starts or constriction speed increases.", "Venturi tube demos; transparent flow apparatus", "Reject videos showing only a pipe shape without flow or pressure response.", "Venturi effect manometer video|Bernoulli pressure drop constriction video", "capillary rise; buoyancy; siphon"),
    p("PHY_FLU_002", "physics_physical_systems", "fluids_pressure_and_buoyancy", "Buoyancy depends on displaced fluid weight relative to object weight.", "Object sinks, floats, or reaches neutral buoyancy as density/ballast changes.", "density columns; ballast demonstrations; float-sink experiments", "Reject generic boats moving without density or displacement change.", "buoyancy density float sink experiment video|ballast buoyancy demonstration video|neutral buoyancy video", "surface tension support; propulsion; pressure-driven flow"),
    p("PHY_FLU_003", "physics_physical_systems", "fluids_pressure_and_buoyancy", "Pressure gradients drive siphon or liquid-column flow after priming.", "Liquid continues moving through a tube across height differences with visible level changes.", "siphon demonstrations; transparent tube flow", "Reject source-only siphon claims where no flow path or level change is visible.", "siphon pressure gradient flow video|transparent siphon liquid level video", "capillary rise; pump-driven flow; diffusion"),
    p("PHY_SUR_001", "physics_physical_systems", "surface_and_capillary_processes", "Surface tension minimizes liquid surface area, driving droplets to retract and round.", "Elongated drops retract, oscillate, or relax toward rounder shapes.", "droplet relaxation slow motion; liquid bridge relaxation", "Reject still droplets or splash-only clips without relaxation dynamics.", "surface tension droplet relaxation slow motion|liquid bridge surface tension retraction video", "gravity fall; wetting spread; evaporation"),
    p("PHY_SUR_002", "physics_physical_systems", "surface_and_capillary_processes", "Capillary action draws wetting liquids through narrow pores or tubes.", "Liquid front rises or advances through a tube, paper, or porous medium.", "capillary rise; paper wicking; porous media wetting", "Reject non-porous droplet rolling or source-only capillary titles.", "capillary action liquid rise time lapse|paper wicking capillary action video|capillary rise tube experiment", "bulk pouring; diffusion only; surface beading"),
    p("PHY_SUR_003", "physics_physical_systems", "surface_and_capillary_processes", "Wetting transitions occur when adhesion overcomes nonwetting surface forces.", "Droplet contact angle decreases, spreads, or switches from rebound to wetting.", "contact-angle videos; droplet impact wetting; coating tests", "Reject clips showing a final wet surface without spreading over time.", "contact angle wetting droplet spreading video|droplet impact transition rebound wetting slow motion", "capillary rise; evaporation; precipitation"),
    p("PHY_THR_001", "physics_physical_systems", "thermal_physical_response", "Differential thermal expansion bends bonded materials when heated.", "Composite strip or bonded structure curves as temperature changes.", "bimetallic strip; thermal expansion demos", "Reject heating clips without visible deformation or temperature-linked response.", "bimetallic strip thermal expansion video|differential thermal expansion bending video", "plastic deformation by force; pendulum; melting"),
    p("PHY_THR_002", "physics_physical_systems", "thermal_physical_response", "The Leidenfrost effect forms a vapor layer that delays contact boiling and lets droplets glide.", "Droplet skitters or survives on a very hot surface while vapor supports it.", "Leidenfrost droplet slow motion; hot plate demos", "Reject ordinary boiling droplets without vapor-layer gliding.", "Leidenfrost droplet skittering slow motion|Leidenfrost effect hot plate video", "wetting spread; evaporation plume; capillary action"),
    p("PHY_EM_001", "physics_physical_systems", "electromagnetism_and_fields", "Magnetic dipoles experience torque that aligns them with an external magnetic field.", "Needles, particles, or domains rotate or align when field direction changes.", "magnetic alignment particles; compass field demos; ferrofluid field videos", "Reject clips with magnets touching objects directly without field-driven alignment.", "magnetic field alignment particles video|magnetic dipole torque alignment video|ferrofluid magnetic field motion video", "electric-field migration; gravity; fluid flow"),
    p("PHY_EM_002", "physics_physical_systems", "electromagnetism_and_fields", "Electric fields exert forces on charged droplets or particles, driving migration or deformation.", "Particles/droplets move along field lines or deform between electrodes.", "electrophoresis videos; charged droplet electric field demos", "Reject clips where electrodes are visible but no field-driven motion occurs.", "electric field charged droplet motion video|electrophoresis particle migration video", "magnetic alignment; diffusion; buoyancy"),
    p("CHM_PHA_001", "chemistry_materials_change", "phase_change_and_crystallization", "Supersaturation enables nucleation followed by crystal growth.", "Crystal nuclei appear and faces/fronts expand through solution.", "supersaturated solution crystallization; sodium acetate hand warmer; crystal garden videos", "Reject static crystals or source-only crystallization titles.", "supersaturated solution crystallization time lapse|crystal nucleation growth video|sodium acetate crystallization video", "precipitation cloud; dye diffusion; melting only"),
    p("CHM_PHA_002", "chemistry_materials_change", "phase_change_and_crystallization", "Solidification fronts propagate as liquid changes phase into ordered solid.", "A visible solid-liquid boundary advances or dendrites grow.", "freezing water; metal solidification; ice crystal growth", "Reject final frozen samples without front propagation.", "solidification front time lapse|ice crystal growth time lapse|freezing front propagation video", "precipitation; evaporation; gas evolution"),
    p("CHM_RED_001", "chemistry_materials_change", "redox_and_endpoint_reactions", "Iodine-clock kinetics delay starch-iodine color until reductant is depleted.", "A mixture remains light, then abruptly turns dark after a delay.", "iodine clock reaction videos", "Reject generic color changes without delayed endpoint.", "iodine clock reaction color change video|iodine clock delayed endpoint video", "precipitation; acid base indicator; diffusion"),
    p("CHM_RED_002", "chemistry_materials_change", "redox_and_endpoint_reactions", "Reducing sugars reduce copper(II) to copper(I) oxide during Benedict heating.", "Blue reagent changes toward orange-red and precipitate forms during heating.", "Benedict test videos; reducing sugar demos", "Reject if only final tube colors are shown or source text supplies all chemistry.", "Benedict test reducing sugar precipitate video|Benedict reagent color change heating video", "iodine clock; pH indicator; simple dye mixing"),
    p("CHM_RED_003", "chemistry_materials_change", "redox_and_endpoint_reactions", "Redox indicator systems can cycle between colored oxidation states.", "Shaking/resting or reagent changes produce reversible color transitions.", "chemical traffic light; blue bottle; chameleon reaction", "Reject one-way color changes without redox-cycle evidence.", "chemical traffic light reaction color cycle video|blue bottle reaction reversible color video|chemical chameleon reaction video", "precipitation; crystallization; combustion"),
    p("CHM_PRE_001", "chemistry_materials_change", "precipitation_and_solubility", "Ion mixing can exceed solubility product and produce an insoluble solid.", "Solutions become cloudy or solid particles appear after mixing.", "precipitation reaction demos; silver chloride; barium sulfate; lead iodide", "Reject if the solid is already present before mixing or the identity is only in source text.", "precipitation reaction insoluble solid forming video|silver chloride precipitate video|lead iodide precipitation video", "gas bubbles; dye diffusion; crystallization front"),
    p("CHM_PRE_002", "chemistry_materials_change", "precipitation_and_solubility", "Local supersaturation at a reaction interface creates precipitate bands or membranes.", "Solid appears where two liquids meet, often as rings, tubes, or membranes.", "chemical garden; Liesegang rings; diffusion precipitation", "Reject bulk turbidity without visible interface or local formation.", "diffusion precipitation band reaction video|chemical garden precipitation tube growth video|Liesegang ring precipitation time lapse", "homogeneous crystallization; pH color; gas evolution"),
    p("CHM_GAS_001", "chemistry_materials_change", "gas_evolution_and_combustion", "Gas-evolution reactions generate bubbles as products leave solution.", "Bubbles nucleate and rise, foam grows, or liquid volume changes after reactants meet.", "acid carbonate; metal acid hydrogen; decomposition gas", "Reject ordinary boiling or pre-existing bubbles.", "gas evolution reaction bubbles video|acid carbonate reaction bubbles video|hydrogen gas evolution reaction video", "boiling; precipitation; diffusion"),
    p("CHM_GAS_002", "chemistry_materials_change", "gas_evolution_and_combustion", "Combustion requires fuel, oxidizer, and heat; removing one extinguishes flame.", "Flame appears, propagates, or extinguishes after oxygen/fuel/temperature changes.", "flame extinction; combustion demos; hydrogen ignition", "Reject clips that only show a flame without causal change.", "flame extinction oxygen deprivation video|combustion reaction ignition video|hydrogen gas ignition bubbles video", "redox color; evaporation; glow without flame"),
    p("CHM_DIF_001", "chemistry_materials_change", "diffusion_mixing_and_transport", "Concentration gradients drive molecular diffusion and spreading.", "Dye or solute front broadens from high concentration to low concentration.", "dye diffusion; gel diffusion; microfluidic diffusion", "Reject turbulent stirring when diffusion cannot be separated.", "dye diffusion concentration gradient time lapse|diffusion in water dye time lapse|microfluidic diffusion video", "vortex mixing; precipitation; convection"),
    p("CHM_DIF_002", "chemistry_materials_change", "diffusion_mixing_and_transport", "Laminar shear stretches and folds fluids, increasing interface without turbulence.", "Colored bands elongate into thin layers and may reverse under reversed shear.", "Taylor-Couette; reversible laminar mixing; viscous mixing demos", "Reject fully turbulent mixing or simple shaking.", "laminar mixing stretching folding dye video|reversible laminar mixing video|Taylor Couette mixing dye video", "diffusion only; vortex turbulence; precipitation"),
    p("CHM_MAT_001", "chemistry_materials_change", "material_deformation_and_response", "Shear-thickening suspensions resist rapid stress while flowing under slow stress.", "Material behaves liquid under slow motion but solid-like under impact.", "cornstarch oobleck impact; shear thickening demos", "Reject generic thick liquids without rate-dependent contrast.", "shear thickening cornstarch impact slow motion|oobleck impact resistance video", "gelation; plastic deformation; surface tension"),
    p("CHM_MAT_002", "chemistry_materials_change", "material_deformation_and_response", "Heating can soften or melt material, reducing strength and enabling deformation.", "Material deforms, sags, flows, or breaks as temperature increases.", "polymer softening; metal melting; glass softening", "Reject post-heating final shape without thermal sequence.", "heat softening material deformation video|polymer melting deformation time lapse|glass softening heat shaping video", "mechanical cutting; crystallization; combustion"),
    p("BIO_CELL_001", "biology_living_systems", "germination_and_development", "Mitotic spindle dynamics separate chromosomes into daughter cells.", "Chromosomes align at the metaphase plate and move toward opposite poles.", "live-cell mitosis microscopy; chromosome segregation", "Reject static mitosis-stage diagrams and clips without chromosome movement.", "mitosis chromosome segregation time lapse microscopy|live cell mitosis spindle chromosome video", "cytokinesis only; cell migration; diffusion"),
    p("BIO_CELL_002", "biology_living_systems", "germination_and_development", "Cytokinesis completes division through progressive contractile-ring constriction.", "A cleavage furrow deepens until one cell becomes two.", "cytokinesis live-cell imaging; contractile ring videos", "Reject static two-cell images or pure animation without real dynamics.", "cytokinesis contractile ring time lapse|cell cleavage furrow live imaging", "mitosis chromosome motion; apoptosis; cell migration"),
    p("BIO_CELL_003", "biology_living_systems", "organism_behavior_and_taxis", "Actin polymerization and adhesion cycles drive crawling cell migration.", "Leading edge protrudes, adhesions shift, rear retracts, and the cell body translocates.", "immune cell migration; amoeboid motion; wound-healing migration", "Reject random cell shape changes without net displacement.", "cell migration pseudopod actin time lapse|amoeboid cell migration time lapse|immune cell crawling microscopy", "Brownian motion; ciliary swimming; mitosis"),
    p("BIO_TRA_001", "biology_living_systems", "plant_water_relations_and_turgor", "Osmosis changes plant-cell volume, causing plasmolysis and deplasmolysis.", "Protoplast shrinks away from cell wall in hypertonic solution and recovers in water.", "onion plasmolysis microscopy; Elodea plasmolysis", "Reject single final plasmolyzed images or label-only school videos.", "plasmolysis deplasmolysis time lapse microscopy|onion cell plasmolysis video|Elodea plasmolysis time lapse", "cytoplasmic streaming; stomata; diffusion in water"),
    p("BIO_TRA_002", "biology_living_systems", "plant_water_relations_and_turgor", "Guard-cell turgor changes open and close stomatal pores.", "Stomatal aperture increases or decreases as guard cells change shape.", "stomata opening time lapse; guard cell turgor videos", "Reject static stomata views or graphs without visible pore change.", "stomata opening closing guard cell turgor time lapse|stomatal aperture time lapse microscopy", "phototropism; plasmolysis; leaf folding"),
    p("BIO_TRA_003", "biology_living_systems", "plant_water_relations_and_turgor", "Cytoplasmic streaming moves organelles along cytoskeletal tracks inside plant cells.", "Chloroplasts or granules circulate along cell boundaries or strands.", "Elodea cytoplasmic streaming; chloroplast movement microscopy", "Reject if movement is only camera drift or Brownian jitter.", "Elodea cytoplasmic streaming chloroplast movement video|cytoplasmic streaming plant cell microscopy", "plasmolysis; diffusion; mitosis"),
    p("BIO_ENE_001", "biology_living_systems", "plant_growth_and_tropisms", "Photosynthetic light reactions release oxygen when illuminated.", "Oxygen bubbles increase after light exposure or light intensity changes.", "aquatic plant oxygen bubbles; photosynthesis light intensity demos", "Reject generic plant growth videos or final gas collection only.", "photosynthesis oxygen bubbles light intensity video|Elodea photosynthesis oxygen bubble video|photosynthesis rate bubbles light video", "respiration CO2; boiling; gas evolution chemistry"),
    p("BIO_ENE_002", "biology_living_systems", "germination_and_development", "Cellular respiration consumes oxygen and releases carbon dioxide during metabolism.", "CO2 indicator or sensor changes over time due to living tissue or microbes.", "respiration indicator experiments; yeast respiration CO2", "Reject simple fermentation foam unless respiration mechanism and control are visible.", "cellular respiration CO2 indicator color change video|yeast respiration CO2 indicator video|seed respiration carbon dioxide indicator video", "photosynthesis oxygen; acid-base demo; combustion"),
    p("BIO_DEV_001", "biology_living_systems", "germination_and_development", "Embryogenesis proceeds through repeated cell divisions and coordinated cell migration.", "Cleavage, gastrulation, or tissue formation is visible over time.", "zebrafish embryo time lapse; C elegans embryo development; frog embryo", "Reject final embryo stage slides or pure text overlays.", "zebrafish embryo development time lapse|embryogenesis cell division migration time lapse|C elegans embryo development time lapse", "plant germination; cell migration only; mitosis isolated"),
    p("BIO_DEV_002", "biology_living_systems", "germination_and_development", "Seed germination starts with water uptake and radicle emergence before shoot development.", "Seed swells, radicle emerges, shoot later elongates.", "seed germination time lapse; bean radicle emergence", "Reject generic seedling growth after germination if radicle emergence is absent.", "seed germination radicle emergence time lapse|bean germination root shoot time lapse", "phototropism; leaf unfurling; fungal growth"),
    p("BIO_TRO_001", "biology_living_systems", "plant_growth_and_tropisms", "Phototropism bends shoots through differential growth toward directional light.", "Shoot curvature gradually changes toward a visible or known light source.", "phototropism time lapse; directional light plant growth", "Reject normal vertical growth without directional stimulus.", "phototropism plant shoot bending time lapse|plant growing toward light time lapse", "circumnutation; germination; stomata"),
    p("BIO_TRO_002", "biology_living_systems", "plant_growth_and_tropisms", "Gravitropism redirects root or shoot growth relative to gravity after reorientation.", "Root tip curves downward or shoot curves upward after rotation.", "root gravitropism time lapse; shoot gravitropism", "Reject clips without reorientation or gravity-relative change.", "root gravitropism time lapse|plant gravitropism reorientation video|shoot gravitropism time lapse", "phototropism; hydrotropism; circumnutation"),
    p("BIO_TRO_003", "biology_living_systems", "plant_growth_and_tropisms", "Hydrotropism biases root growth toward water gradients.", "Root curvature changes toward wetter side over hours or days.", "root hydrotropism time lapse; water gradient root growth", "Reject source-only hydrotropism setups without root curvature.", "root hydrotropism water gradient time lapse|plant root growing toward water video", "gravitropism; halotropism; germination"),
    p("BIO_NAS_001", "biology_living_systems", "plant_nastic_movements", "Thigmonasty converts touch stimulation into rapid leaf or trap movement.", "Touch is followed by rapid closure or bending independent of stimulus direction.", "Mimosa folding; Venus flytrap closure; Drosera tentacle movement", "Reject closed-only/open-only frames or clips where touch is not visible.", "thigmonasty plant movement touch time lapse|Mimosa leaf folding touch video|Venus flytrap closure trigger hair video", "thigmotropism; phototropism; wilting"),
    p("BIO_NAS_002", "biology_living_systems", "plant_nastic_movements", "Nyctinasty changes leaf posture across light-dark cycles via turgor or growth rhythms.", "Leaves open/close or change angle over day-night transitions.", "Oxalis leaf sleep; bean leaf nyctinasty; circadian plant movement", "Reject generic wind movement or one-state leaf images.", "nyctinasty leaf movement time lapse|Oxalis leaf sleep movement video|circadian plant leaf movement time lapse", "phototropism; wilting; touch response"),
    p("BIO_LOC_001", "biology_living_systems", "animal_locomotion_and_biomechanics", "Jet propulsion follows momentum conservation: expelled fluid creates opposite reaction thrust.", "Body cavity or bell contracts, then the body translates in the opposite direction of expelled fluid.", "jellyfish propulsion; squid jet propulsion; scallop jet movement", "Reject swimming clips without contraction-pulse displacement.", "jellyfish jet propulsion bell contraction video|fluid jet propulsion animal locomotion video", "peristalsis; flapping lift; tail undulation"),
    p("BIO_LOC_002", "biology_living_systems", "animal_locomotion_and_biomechanics", "Peristaltic locomotion uses contraction waves plus alternating anchors to move soft bodies.", "Soft body shortens/extends in waves while contact points shift and the body advances.", "caterpillar crawling; earthworm peristalsis; soft robot peristalsis", "Reject legged walking where no contraction wave is visible.", "peristaltic locomotion caterpillar time lapse|earthworm peristaltic crawling video|soft body contraction wave locomotion", "jet propulsion; tripod gait; passive drift"),
    p("BIO_LOC_003", "biology_living_systems", "animal_locomotion_and_biomechanics", "Flapping wings generate lift and thrust by accelerating air downward/backward.", "Wingbeats begin or intensify before lift-off or sustained flight.", "insect takeoff slow motion; bird flapping lift; bee takeoff", "Reject gliding or leg-only jumps with passive wings.", "flapping wing takeoff lift slow motion|insect takeoff wingbeats slow motion|bee takeoff slow motion lift", "leg jump; passive gliding; swimming"),
    p("BIO_LOC_004", "biology_living_systems", "animal_locomotion_and_biomechanics", "Fast-start swimming converts body curvature into hydrodynamic reaction forces and acceleration.", "S- or C-shaped bend is followed by rapid forward acceleration.", "zebrafish fast start; fish escape response; larval strike", "Reject clips where swimming is slow cruising without rapid curvature-acceleration sequence.", "fish fast start S bend swimming video|zebrafish escape response slow motion|larval fish predatory strike video", "phototaxis; peristalsis; passive drift"),
    p("BIO_TAX_001", "biology_living_systems", "organism_behavior_and_taxis", "Chemotaxis biases movement direction along chemical concentration gradients.", "Trajectories accumulate toward/away from a chemical source or gradient.", "bacterial chemotaxis; neutrophil chemotaxis; microfluidic gradient", "Reject random wandering without gradient cue.", "chemotaxis cell migration gradient time lapse|bacterial chemotaxis microfluidic gradient video|neutrophil chemotaxis time lapse", "phototaxis; Brownian motion; thermotaxis"),
    p("BIO_TAX_002", "biology_living_systems", "organism_behavior_and_taxis", "Phototaxis biases movement relative to light direction or intensity.", "Organisms redistribute toward/away from a light source or stimulus marker.", "Euglena phototaxis; insect light trap; larval phototaxis", "Reject clips with a lamp but no moving organisms or no directional redistribution.", "phototaxis microorganism light stimulus video|Euglena phototaxis video|insect phototaxis light source video", "phototropism; random walk; chemotaxis"),
    p("BIO_TAX_003", "biology_living_systems", "organism_behavior_and_taxis", "Magnetotaxis aligns motile cells with a magnetic field through magnetic torque.", "Cell bands or trajectories reorganize when magnetic field direction changes.", "magnetotactic bacteria; magnetic field swimming; field reversal", "Reject source-only magnetotaxis where field marker or movement bias is absent.", "magnetotactic bacteria magnetic field direction video|magnetotaxis field reversal microscopy video", "chemotaxis; phototaxis; Brownian motion"),
    p("BIO_TAX_004", "biology_living_systems", "organism_behavior_and_taxis", "Run-and-tumble or Levy-like search alternates runs and turns to explore space.", "Tracked trajectories show long runs interrupted by reorientation turns.", "bacterial run and tumble; Levy walk microbes; trajectory overlay", "Reject smooth swimming or untracked crowd motion.", "bacteria run and tumble trajectory video|Levy walk bacteria tracking video|intermittent search trajectory time lapse", "diffusion; taxis gradient; ciliary beating"),
    p("EAR_WEA_001", "earth_environmental_systems", "weather_and_atmospheric_dynamics", "Moist convection lifts air, cools it, and forms growing cloud towers.", "Clouds initiate, rise, billow, and deepen vertically.", "cloud convection time lapse; cumulus growth; thunderstorm tower", "Reject scenic clouds drifting with no growth or vertical development.", "cloud formation convection time lapse|cumulus cloud tower growth time lapse|atmospheric convection cloud video", "fog advection; smoke plume; rain band"),
    p("EAR_WEA_002", "earth_environmental_systems", "weather_and_atmospheric_dynamics", "Rotating atmospheric flow organizes clouds and precipitation into vortices.", "Cloud bands rotate around a center or funnel-like structure develops.", "cyclone satellite timelapse; tornado cloud rotation; mesocyclone", "Reject static satellite images or non-rotating cloud drift.", "cloud vortex rotation time lapse|cyclone cloud bands rotation video|tornado formation cloud rotation video", "linear front motion; river flow; smoke"),
    p("EAR_HYD_001", "earth_environmental_systems", "hydrology_and_flow_processes", "Gravity and hydraulic slope drive surface runoff and channelized flow.", "Water gathers, accelerates downslope, and forms rills or channels.", "runoff flume; rainfall simulator; slope flow", "Reject standing water or generic rain without flow paths.", "surface runoff slope erosion experiment video|rainfall runoff flume video|water flowing downslope channel formation video", "capillary absorption; seepage only; wave motion"),
    p("EAR_HYD_002", "earth_environmental_systems", "hydrology_and_flow_processes", "Infiltration advances a wetting front through porous soil.", "Water level drops and a visible wetting boundary moves downward or laterally.", "soil infiltration; wetting front; porous media water flow", "Reject top-surface wetting without internal front movement.", "soil infiltration wetting front time lapse|porous soil water infiltration video", "surface runoff; capillary tube; sediment transport"),
    p("EAR_ERO_001", "earth_environmental_systems", "erosion_transport_and_deposition", "Sediment motion begins when fluid shear stress exceeds a transport threshold.", "Grains transition from rest to rolling, saltation, or suspension as flow increases.", "sediment transport flume; threshold of motion; bedload", "Reject sediment already moving without flow change or threshold evidence.", "sediment transport threshold flume video|bedload motion start flume experiment|grain entrainment by water flow video", "debris flow; diffusion; landslide"),
    p("EAR_ERO_002", "earth_environmental_systems", "erosion_transport_and_deposition", "Deposition and sorting occur because particle settling speed depends on size and density.", "Particles separate spatially or layers form as flow slows.", "sediment sorting flume; settling column; delta deposition", "Reject final sorted samples without movement/deposition sequence.", "sediment sorting flume experiment video|particle settling sorting time lapse|delta deposition flume video", "filtration; granular vibration; chemical precipitation"),
    p("EAR_GEO_001", "earth_environmental_systems", "geology_and_geophysical_change", "Slope failure occurs when driving stress exceeds material shear strength.", "Cracks, deformation, and mass movement develop downslope.", "landslide model; slope failure flume; soil collapse", "Reject post-landslide aftermath without failure sequence.", "landslide failure slope model video|slope instability landslide experiment video|soil slope collapse time lapse", "debris flow transport; erosion; glacier calving"),
    p("EAR_GEO_002", "earth_environmental_systems", "geology_and_geophysical_change", "Pyroclastic density currents move as ground-hugging particle-laden gravity currents.", "Dense current advances along the ground with a leading front and suspended particles.", "pyroclastic flow analog; density current flume; volcanic ash current", "Reject smoke plumes rising vertically without ground-hugging current.", "pyroclastic density current experiment video|pyroclastic flow analogue flume video|particle laden gravity current video", "lava flow; debris slide; steam convection"),
    p("EAR_GEO_003", "earth_environmental_systems", "geology_and_geophysical_change", "Lava flow forms a cooling crust while molten interior continues advancing.", "Surface crust wrinkles, breaks, or folds as the flow front moves.", "lava flow time lapse; pahoehoe crust; molten lava front", "Reject static lava images or glow-only clips.", "lava flow crust folding time lapse|pahoehoe lava flow time lapse|molten lava flow front video", "pyroclastic current; mudflow; glacier"),
    p("EAR_CRY_001", "earth_environmental_systems", "cryosphere_and_seasonal_change", "Glacier flow results from ice deformation and basal sliding.", "Ice features, crevasses, or markers move over time.", "glacier flow time lapse; ice motion markers", "Reject glacier scenery without measurable motion.", "glacier flow time lapse|ice deformation glacier motion video|glacier movement markers time lapse", "river flow; avalanche; calving only"),
    p("EAR_CRY_002", "earth_environmental_systems", "cryosphere_and_seasonal_change", "Glacier calving occurs when fractures propagate and unsupported ice detaches.", "Cracks widen and a block breaks from the glacier front into water.", "glacier calving slow motion; ice front fracture", "Reject clips that only show floating ice after detachment.", "glacier calving slow motion|iceberg calving fracture video|glacier front collapse video", "landslide; freeze-thaw; wave breaking"),
    p("EAR_ECO_001", "earth_environmental_systems", "ecosystem_interactions", "Predation is a dynamic interaction of pursuit, attack, and prey response.", "Predator approaches, accelerates or strikes, prey escapes or is captured.", "predator prey high speed; hunting behavior; strike capture", "Reject simple co-presence of organisms without interaction sequence.", "predator prey interaction high speed video|predator strike capture slow motion|hunting behavior prey escape video", "pollination; taxis; passive movement"),
    p("EAR_ECO_002", "earth_environmental_systems", "ecosystem_interactions", "Animal-mediated pollination transfers pollen through contact with reproductive structures.", "Visitor contacts anthers/stigma and then moves away or to another flower.", "pollination slow motion; bee flower contact; hummingbird pollination", "Reject flower visitor videos without contact to reproductive parts.", "pollination insect flower contact slow motion|bee pollination anther stigma contact video|flower visitor pollen transfer video", "feeding only; phototaxis; wind"),
    p("ENG_MCH_001", "engineered_systems_and_operations", "machines_control_and_failure_modes", "Linkage constraints convert input rotation into a designed output path.", "Input crank rotates while output point follows a bounded, straight, oscillating, or pick-and-place trajectory.", "four-bar linkage; crank-rocker; straight-line linkage", "Reject pure physics pendulums or animations without input-output transformation.", "four bar linkage motion conversion video|crank rocker linkage output path video|straight line linkage mechanism video", "gear train; cam follower; free rotation"),
    p("ENG_MCH_002", "engineered_systems_and_operations", "machines_control_and_failure_modes", "Cam profiles convert continuous rotation into programmed follower displacement.", "Rotating cam makes a follower rise, dwell, and fall.", "cam follower mechanism; valve train; cam dwell", "Reject rotating disks without follower contact.", "cam follower mechanism slow motion|cam profile follower rise dwell fall video|valve cam mechanism animation", "linkage; gear ratio; pendulum"),
    p("ENG_MCH_003", "engineered_systems_and_operations", "machines_control_and_failure_modes", "Escapements discretize energy release into stepwise gear advance.", "Oscillator motion locks/unlocks teeth and gear advances one step at a time.", "clock escapement; anchor escapement; watch escapement", "Reject clock face videos with no visible escapement action.", "clock escapement mechanism slow motion|anchor escapement gear step video|watch escapement slow motion", "gear train; ratchet; pendulum only"),
    p("ENG_MCH_004", "engineered_systems_and_operations", "machines_control_and_failure_modes", "Ratchets allow intermittent one-way motion while blocking reverse motion.", "Pawl engages teeth during one direction and slips/resets in the other.", "ratchet mechanism; pawl; one-way drive", "Reject tools using ratchets without visible pawl-tooth sequence.", "ratchet mechanism one way motion video|pawl ratchet intermittent motion slow motion", "escapement; gear train; clutch"),
    p("ENG_PRS_001", "engineered_systems_and_operations", "pressure_flow_and_process_control", "Valves regulate flow by changing flow area and pressure drop.", "Valve position changes are followed by flow-rate, jet, or level changes.", "transparent valve flow; flow control valve; ball valve", "Reject static valve cutaways without fluid response.", "valve flow control transparent video|flow control valve pressure drop video|transparent ball valve water flow", "Venturi physics only; pump; siphon"),
    p("ENG_PRS_002", "engineered_systems_and_operations", "pressure_flow_and_process_control", "Pumps use cyclic volume or pressure changes to impose one-way fluid transport.", "Piston, diaphragm, peristaltic rollers, or impeller motion drives visible one-way flow.", "peristaltic pump; diaphragm pump; piston pump visualization", "Reject source-only pump videos without visible fluid movement.", "peristaltic pump flow visualization video|diaphragm pump transparent flow video|piston pump one way valve video", "siphon; capillary action; open-channel flow"),
    p("ENG_PRS_003", "engineered_systems_and_operations", "pressure_flow_and_process_control", "Feedback control reduces deviation by sensing a variable and actuating a correction.", "A disturbance or setpoint change is followed by actuator response and variable stabilization.", "level control; PID valve; thermostat control demos", "Reject manually adjusted controls without closed-loop response.", "feedback control valve level system video|PID level control tank video|closed loop process control demonstration", "open-loop valve; pressure relief; natural flow"),
    p("ENG_SEP_001", "engineered_systems_and_operations", "filtration_and_separation", "Pressure-driven filtration separates solids by forcing fluid through porous media.", "Filtrate passes through while a solid cake accumulates upstream.", "vacuum filtration; filter cake formation; membrane filtration", "Reject final filtered beakers without cake formation or fluid passage.", "vacuum filtration filter cake formation video|pressure filtration porous media video|membrane filtration particle retention video", "sedimentation; sieving; diffusion"),
    p("ENG_SEP_002", "engineered_systems_and_operations", "filtration_and_separation", "Density-driven settling separates particles by gravitational settling velocity.", "Suspension clears from top while particles accumulate at bottom.", "sedimentation separation; settling column; clarification", "Reject shaking or centrifuge if gravity settling is not the mechanism.", "sedimentation separation time lapse|settling column particles time lapse|clarification suspension settling video", "precipitation; filtration; centrifugation"),
    p("ENG_SEP_003", "engineered_systems_and_operations", "filtration_and_separation", "Vibration can segregate granular mixtures when smaller grains percolate downward.", "Larger particles rise or appear at the top under repeated shaking.", "Brazil nut effect; granular segregation; vibration sorting", "Reject static layered bins or manual sorting.", "Brazil nut effect granular segregation video|vibrated granular mixture size segregation video", "sediment sorting; sieving; buoyancy"),
    p("ENG_MIX_001", "engineered_systems_and_operations", "mixing_dispersion_and_wetting", "Mechanical mixing disperses components by stretching, folding, and advecting interfaces.", "Colored fluids or particles are stretched into filaments and distributed through the volume.", "static mixer; impeller mixing; dye mixing visualization", "Reject final homogeneous mixtures without mixing trajectory.", "fluid mixing dye visualization video|static mixer dye stretching folding video|impeller mixing dispersion video", "molecular diffusion only; precipitation; laminar reversible mixing"),
    p("ENG_MIX_002", "engineered_systems_and_operations", "mixing_dispersion_and_wetting", "Coating/wetting processes rely on contact-angle reduction and droplet coalescence into a film.", "Droplets impact, spread, merge, and form a continuous layer.", "spray coating; dip coating; wetting surface treatment", "Reject isolated physics droplet demos unless process goal is coating or cleaning.", "spray coating droplet deposition slow motion|coating wetting contact angle video|droplet coalescence coating film video", "capillary rise; rain drops; diffusion"),
    p("ENG_THM_001", "engineered_systems_and_operations", "thermal_process_control", "Hot forging uses elevated temperature to lower flow stress for controlled plastic deformation.", "Heated workpiece deforms progressively under hammer/press blows.", "hot forging; blacksmithing; press forging", "Reject cold hammering or decorative final shapes without deformation sequence.", "hot forging plastic deformation video|heated metal hammer forging slow motion|press forging red hot steel video", "thermal expansion; cutting; welding"),
    p("ENG_THM_002", "engineered_systems_and_operations", "thermal_process_control", "Quenching rapidly extracts heat to change material state and properties.", "Hot part is immersed, vapor/boiling forms, and cooling progresses rapidly.", "steel quenching; heat treatment; vapor blanket quench", "Reject simple dunking with no thermal response or material context.", "quenching hot steel cooling video|heat treatment quench boiling video|steel quench vapor blanket video", "Leidenfrost droplet; forging; welding"),
    p("ENG_TOOL_001", "engineered_systems_and_operations", "tooling_force_and_precision", "Cutting forms chips when tool shear stress exceeds material strength along a shear plane.", "Tool advances and continuous or segmented chips form and evacuate.", "metal cutting slow motion; orthogonal cutting; chip formation", "Reject finished cuts without visible chip formation.", "metal cutting chip formation slow motion|orthogonal cutting shear plane video|lathe chip formation slow motion", "fracture impact; drilling; polishing"),
    p("ENG_TOOL_002", "engineered_systems_and_operations", "tooling_force_and_precision", "Drilling combines rotary cutting and axial feed to remove material as chips.", "Drill rotates, advances, and chips evacuate from the hole.", "drilling slow motion; chip evacuation; machining", "Reject hole already made or no visible chips.", "drilling chip evacuation slow motion|drill bit cutting chips video|machining drilling process slow motion", "sawing; cutting only; melting"),
    p("ENG_FAIL_001", "engineered_systems_and_operations", "machines_control_and_failure_modes", "Mechanical resonance can amplify vibration until structural instability or failure occurs.", "Vibration amplitude grows and structure deforms, loses control, or breaks.", "resonance failure; bridge vibration; rotating machinery instability", "Reject failures with no visible oscillation growth.", "mechanical resonance failure video|vibration amplitude growth structural failure video|rotating machinery resonance instability video", "impact fracture; damping; normal operation"),
    p("ENG_FAIL_002", "engineered_systems_and_operations", "pressure_flow_and_process_control", "Clogging creates positive feedback by reducing flow area and increasing upstream accumulation.", "Particles collect in a filter/channel, flow slows, and blockage worsens.", "filter clogging; channel blockage; fouling time lapse", "Reject final clogged filters without accumulation sequence.", "filter clogging flow rate time lapse|channel blockage particle accumulation video|fouling filter time lapse", "sedimentation; filtration normal; precipitation"),
]


STOPWORDS = {
    "the",
    "and",
    "with",
    "that",
    "from",
    "into",
    "when",
    "this",
    "over",
    "through",
    "video",
    "time",
    "lapse",
    "slow",
    "motion",
    "experiment",
    "demonstration",
    "visible",
    "process",
    "dynamic",
    "causing",
    "producing",
    "rather",
    "after",
    "before",
    "during",
}


def words(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower())
        if len(token) >= 4 and token not in STOPWORDS
    }


def canonical_domain(domain: str) -> str:
    return DOMAIN_ALIASES.get(domain, domain)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_queries(inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in inventory:
        for query in item["query_seed"].split("|"):
            query = query.strip()
            if not query:
                continue
            key = (item["principle_id"], query.lower())
            if key in seen:
                continue
            seen.add(key)
            notes = (
                f"principle_id={item['principle_id']}; priority={item['priority']}; "
                f"reject={item['reject_conditions']}; hard_negative_family={item['hard_negative_family']}"
            )
            rows.append(
                {
                    "search_term": query,
                    "initial_category": item["domain"],
                    "candidate_knowledge_point": "__construct_after_principle_video_gate__",
                    "domain_seed": item["domain"],
                    "subdomain_seed": item["subdomain"],
                    "default_start_sec": "0",
                    "default_end_sec": "60",
                    "why_dynamic": item["required_dynamic_signature"],
                    "notes": notes,
                    "collector_notes": notes,
                }
            )
    return rows


def build_mapping(inventory: list[dict[str, str]], release_rows: list[dict]) -> list[dict[str, str]]:
    principle_terms = {
        item["principle_id"]: words(
            " ".join(
                [
                    item["principle"],
                    item["required_dynamic_signature"],
                    item["query_seed"],
                    item["hard_negative_family"],
                ]
            )
        )
        for item in inventory
    }
    rows: list[dict[str, str]] = []
    by_pair: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for item in inventory:
        by_pair[(canonical_domain(item["domain"]), item["subdomain"])].append(item)

    for sample in release_rows:
        text = " ".join(
            [
                str(sample.get("knowledge_point", "")),
                " ".join(str(span.get("description", "")) for span in sample.get("dynamic_evidence", [])),
                str(sample.get("static_insufficient_reason", "")),
            ]
        )
        sample_terms = words(text)
        sample_domain = str(sample.get("domain", ""))
        sample_subdomain = str(sample.get("subdomain", ""))
        candidates = by_pair.get((canonical_domain(sample_domain), sample_subdomain), [])
        scored = []
        for item in candidates:
            overlap = sample_terms & principle_terms[item["principle_id"]]
            score = len(overlap)
            if score:
                scored.append((score, item, sorted(overlap)))
        scored.sort(key=lambda entry: (-entry[0], entry[1]["principle_id"]))
        if scored:
            score, item, overlap = scored[0]
            status = "strong_candidate" if score >= 4 else "weak_candidate"
            rows.append(
                {
                    "video_id": sample.get("video_id", ""),
                    "domain": sample.get("domain", ""),
                    "subdomain": sample.get("subdomain", ""),
                    "knowledge_point": sample.get("knowledge_point", ""),
                    "best_principle_id": item["principle_id"],
                    "best_principle": item["principle"],
                    "mapping_score": str(score),
                    "mapping_status": status,
                    "overlap_terms": ";".join(overlap),
                    "action": "review_keep_or_rewrite" if status == "strong_candidate" else "needs_principle_review_or_replacement",
                }
            )
        else:
            rows.append(
                {
                    "video_id": sample.get("video_id", ""),
                    "domain": sample.get("domain", ""),
                    "subdomain": sample.get("subdomain", ""),
                    "knowledge_point": sample.get("knowledge_point", ""),
                    "best_principle_id": "",
                    "best_principle": "",
                    "mapping_score": "0",
                    "mapping_status": "unmapped",
                    "overlap_terms": "",
                    "action": "needs_replacement_or_new_principle",
                }
            )
    return rows


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100.0 * value / total:.1f}%"


def label(value: str) -> str:
    return value.replace("_", " ")


def build_report(inventory: list[dict[str, str]], queries: list[dict[str, str]], mapping: list[dict[str, str]]) -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    domain_counts = Counter(row["domain"] for row in inventory)
    subdomain_counts = Counter((row["domain"], row["subdomain"]) for row in inventory)
    priority_counts = Counter(row["priority"] for row in inventory)
    mapping_counts = Counter(row["mapping_status"] for row in mapping)
    action_counts = Counter(row["action"] for row in mapping)

    metrics = [
        ("Principles", len(inventory), f"{len(subdomain_counts)} subdomains"),
        ("Query Seeds", len(queries), "principle-derived retrieval rows"),
        ("Current Samples Mapped", len(mapping), "from v1.1 candidate release"),
        ("Strong Candidate", mapping_counts.get("strong_candidate", 0), pct(mapping_counts.get("strong_candidate", 0), len(mapping))),
        ("Weak Candidate", mapping_counts.get("weak_candidate", 0), pct(mapping_counts.get("weak_candidate", 0), len(mapping))),
        ("Unmapped", mapping_counts.get("unmapped", 0), pct(mapping_counts.get("unmapped", 0), len(mapping))),
    ]
    metric_html = "".join(
        f'<div class="metric"><strong>{esc(value)}</strong><span>{esc(name)}</span><small>{esc(detail)}</small></div>'
        for name, value, detail in metrics
    )

    domain_rows = "".join(
        f"<tr><td>{esc(label(domain))}</td><td class=\"num\">{count}</td><td class=\"num\">{pct(count, len(inventory))}</td></tr>"
        for domain, count in sorted(domain_counts.items())
    )
    priority_rows = "".join(
        f"<tr><td>{esc(priority)}</td><td class=\"num\">{count}</td><td class=\"num\">{pct(count, len(inventory))}</td></tr>"
        for priority, count in sorted(priority_counts.items())
    )
    action_rows = "".join(
        f"<tr><td>{esc(action)}</td><td class=\"num\">{count}</td><td class=\"num\">{pct(count, len(mapping))}</td></tr>"
        for action, count in sorted(action_counts.items())
    )
    subdomain_rows = "".join(
        f"<tr><td>{esc(label(domain))}</td><td>{esc(label(subdomain))}</td><td class=\"num\">{count}</td></tr>"
        for (domain, subdomain), count in sorted(subdomain_counts.items())
    )
    inventory_rows = "".join(
        "<tr>"
        f"<td>{esc(row['principle_id'])}</td>"
        f"<td>{esc(label(row['domain']))}</td>"
        f"<td>{esc(label(row['subdomain']))}</td>"
        f"<td>{esc(row['principle'])}</td>"
        f"<td>{esc(row['required_dynamic_signature'])}</td>"
        f"<td>{esc(row['query_seed'])}</td>"
        f"<td>{esc(row['reject_conditions'])}</td>"
        "</tr>"
        for row in inventory
    )
    mapping_rows = "".join(
        "<tr>"
        f"<td>{esc(row['video_id'])}</td>"
        f"<td>{esc(label(row['subdomain']))}</td>"
        f"<td>{esc(row['knowledge_point'])}</td>"
        f"<td>{esc(row['best_principle_id'])}</td>"
        f"<td>{esc(row['best_principle'])}</td>"
        f"<td class=\"num\">{esc(row['mapping_score'])}</td>"
        f"<td>{esc(row['mapping_status'])}</td>"
        f"<td>{esc(row['action'])}</td>"
        "</tr>"
        for row in mapping
    )
    latest_rows = "".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f'<td><a href="{esc(path)}">{esc(path)}</a></td>'
        f"<td>{esc(note)}</td>"
        "</tr>"
        for name, path, note in [
            ("Archive Candidate Pool", "latest_archive_candidate_pool.html", "Strictly rescored Internet Archive fallback candidates."),
            ("Archive Principle Gate", "latest_archive_gate_review.html", "Video-first dynamic signature gate with source double-check fields."),
            ("Archive Media Review", "latest_archive_media_review.html", "Downloaded videos/contact sheets for the strict archive queue."),
            ("Existing Pass Audit", "existing_pass_principle_audit_20260605.html", "Principle-first audit of the current 248 pass-only release; audit only, not automatic acceptance."),
            ("Replacement Gaps", "replacement_gaps_20260605.html", "Subdomain task list: strong principle keep candidates, replacement rows, source gaps, and new-needed counts against the 8/pass target."),
            ("Capability Labels + DCR Inventory", "capability_labels_dcr_inventory_v1.html", "Two-dimensional capability design: DMR for Why/How, DCR for named dynamic concept recognition."),
            ("DCR Concept CSV", "../../data/dynamic_concept_inventory_v1.csv", "Named dynamic concepts that require temporal evidence, linked to domains and principles."),
            ("DCR Query CSV", "../../data/dynamic_concept_search_queries_v1.csv", "Search queue seeds for Dynamic Concept Recognition candidates."),
            ("Capability Schema", "../../data/capability_label_schema_v1.json", "Formal contract for DMR/DCR labels and DCR exclusions."),
            ("Capability-Mixed Query Queue", "capability_mixed_query_queue_20260605.html", "2:1 interleaved DMR/DCR retrieval queue for the capability-label benchmark design."),
            ("Capability-Mixed Query CSV", "../../data/capability_mixed_search_queries_v1_20260605.csv", "Background-retrieval-ready queue containing both DMR and DCR query seeds."),
            ("Capability-Mixed Gate Preview", "capability_mixed_gate_preview_20260605.html", "Schema preview showing DMR/DCR gate fields before video download; not final acceptance."),
            ("Gap-Aware Query Queue", "gap_aware_query_queue_20260605.html", "Principle-derived retrieval queries sorted by replacement gap and source/stretch risk."),
            ("Gap-Aware Query CSV", "../../data/principle_gap_aware_search_queries_v1_20260605.csv", "Same query queue for background Commons/Archive retrieval via QUERY_CSV override."),
            ("Principle Inventory CSV", "../../data/principle_inventory_v1.csv", "Mechanism inventory used to drive retrieval."),
            ("Principle Query CSV", "../../data/principle_search_queries_v1.csv", "Principle-derived retrieval queries."),
        ]
    )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DynaKnow Principle-First v1</title>
  <style>
    :root {{ --bg:#f5f6f4; --panel:#fff; --ink:#202124; --muted:#5f675f; --line:#d9ddd7; --accent:#2f6f9f; --soft:#eef3f1; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Arial, Helvetica, sans-serif; line-height:1.42; }}
    header {{ background:#fff; border-bottom:1px solid var(--line); }}
    .wrap {{ max-width:1480px; margin:0 auto; padding:18px 22px; }}
    h1 {{ margin:0 0 6px; font-size:24px; }}
    h2 {{ margin:0 0 12px; font-size:18px; }}
    .note {{ color:var(--muted); margin:0; }}
    .metrics {{ display:grid; grid-template-columns:repeat(6,minmax(140px,1fr)); gap:10px; margin-top:14px; }}
    .metric {{ background:var(--soft); border:1px solid var(--line); border-radius:8px; padding:12px; min-height:86px; }}
    .metric strong {{ display:block; font-size:24px; margin-bottom:4px; }}
    .metric span,.metric small {{ display:block; color:var(--muted); }}
    .grid3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }}
    .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; margin:16px 0; overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th,td {{ border-bottom:1px solid var(--line); padding:8px; text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); white-space:nowrap; }}
    .num {{ text-align:right; white-space:nowrap; }}
    code {{ background:#eef3f1; padding:1px 4px; border-radius:4px; }}
    @media (max-width:1100px) {{ .metrics,.grid3 {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header><div class="wrap">
    <h1>DynaKnow Principle-First v1</h1>
    <p class="note">Principle inventory drives retrieval. Existing release mapping is only a review aid, not final acceptance.</p>
    {metric_html}
  </div></header>
  <main class="wrap">
    <section class="grid3">
      <div class="panel"><h2>Domains</h2><table><thead><tr><th>Domain</th><th class="num">Principles</th><th class="num">Share</th></tr></thead><tbody>{domain_rows}</tbody></table></div>
      <div class="panel"><h2>Priorities</h2><table><thead><tr><th>Priority</th><th class="num">Principles</th><th class="num">Share</th></tr></thead><tbody>{priority_rows}</tbody></table></div>
      <div class="panel"><h2>Current Release Mapping Actions</h2><table><thead><tr><th>Action</th><th class="num">Samples</th><th class="num">Share</th></tr></thead><tbody>{action_rows}</tbody></table></div>
    </section>
    <section class="panel"><h2>Latest Review Runs</h2><table><thead><tr><th>View</th><th>Link</th><th>Note</th></tr></thead><tbody>{latest_rows}</tbody></table></section>
    <section class="panel"><h2>Subdomain Principle Counts</h2><table><thead><tr><th>Domain</th><th>Subdomain</th><th class="num">Principles</th></tr></thead><tbody>{subdomain_rows}</tbody></table></section>
    <section class="panel"><h2>Principle Inventory</h2><table><thead><tr><th>ID</th><th>Domain</th><th>Subdomain</th><th>Principle</th><th>Required Dynamic Signature</th><th>Query Seeds</th><th>Reject Conditions</th></tr></thead><tbody>{inventory_rows}</tbody></table></section>
    <section class="panel"><h2>Existing v1.1 Release Mapping</h2><table><thead><tr><th>Video</th><th>Subdomain</th><th>Current KP</th><th>Best Principle</th><th>Principle Text</th><th class="num">Score</th><th>Status</th><th>Action</th></tr></thead><tbody>{mapping_rows}</tbody></table></section>
  </main>
</body>
</html>
"""
    REPORT_OUT.write_text(html_text, encoding="utf-8")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    schema = {
        "fields": FIELDS,
        "contract": {
            "principle": "transferable mechanism, not a video caption",
            "required_dynamic_signature": "observable temporal evidence needed before a video can pass",
            "reject_conditions": "conditions that block source-only, static, OCR, or shallow visual matches",
            "query_seed": "pipe-separated retrieval strings derived from the principle",
        },
        "domains": sorted({row["domain"] for row in INVENTORY}),
        "domain_aliases": DOMAIN_ALIASES,
    }
    SCHEMA_OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(INVENTORY_OUT, INVENTORY, FIELDS)
    queries = build_queries(INVENTORY)
    write_csv(QUERY_OUT, queries, QUERY_FIELDS)
    release_rows = read_jsonl(CURRENT_RELEASE)
    mapping = build_mapping(INVENTORY, release_rows)
    write_csv(
        MAPPING_OUT,
        mapping,
        [
            "video_id",
            "domain",
            "subdomain",
            "knowledge_point",
            "best_principle_id",
            "best_principle",
            "mapping_score",
            "mapping_status",
            "overlap_terms",
            "action",
        ],
    )
    build_report(INVENTORY, queries, mapping)
    print(f"wrote {len(INVENTORY)} principles -> {INVENTORY_OUT}")
    print(f"wrote {len(queries)} search queries -> {QUERY_OUT}")
    print(f"wrote {len(mapping)} existing-release mappings -> {MAPPING_OUT}")
    print(f"wrote report -> {REPORT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
