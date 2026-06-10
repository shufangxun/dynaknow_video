#!/usr/bin/env python3
"""Add production tiers and video gates to the VDCR concept inventory."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


DEFER_CONCEPTS = {
    "Glacier Creep": "too_long_timescale_visual_evidence_likely_source_dependent",
    "Basal Sliding": "too_long_timescale_visual_evidence_likely_source_dependent",
    "Longshore Drift": "high_static_scene_shortcut_and_often_requires_annotation",
    "Sea-Cliff Retreat": "too_long_timescale_visual_evidence_likely_source_dependent",
    "Spit Progradation": "too_long_timescale_visual_evidence_likely_source_dependent",
    "Stratified Sediment Gravity Flow": "often_requires_instrumented_or_cross_section_evidence",
    "Prandtl-Meyer Expansion Fan": "typically_requires_schlieren_or_simulation_context",
    "Fault Rupture Propagation": "typically_requires_instrumented_or_simulation_context",
    "Convergent Extension": "often_requires_labeled_microscopy_or_developmental_context",
    "Neural Tube Closure": "often_requires_labeled_microscopy_or_developmental_context",
    "Epithelial-Mesenchymal Transition": "often_requires_labeled_microscopy_or_marker_context",
}

EXTENSION_CONCEPTS = {
    "Anguilliform Undulation": "formal_term_but_close_to_animal_motion_recognition",
    "Wave Refraction": "often_clean_only_as_teaching_animation_or_simulation",
    "FRAP Recovery": "valid_experimental_concept_but_depends_on_operation_context",
    "Glacier Surge": "long_timescale_and_source_context_heavy",
}

STRICT_NAME_GATES = {
    "Magnus Effect": (
        "must_show_object_spin_curved_trajectory_and_fluid_deflection_or_lift_effect_not_just_ball_motion"
    ),
    "Medusan Bell-Contraction Jet Propulsion": (
        "must_show_bell_contraction_water_expelled_or_implied_reaction_and_forward_motion_sequence"
    ),
    "Murmuration": "must_show_collective_shape_wave_synchronous_turning_or_flow_like_flock_reorganization",
    "Capillary Rise / Wicking": "must_show_liquid_or_wetting_front_rising_through_capillary_or_porous_path_over_time",
    "Liquid Bridge Pinch-Off": "must_show_bridge_stretching_necking_and_final_breakup_sequence",
    "Leidenfrost Droplet Motion": "must_show_hot_surface_vapor_cushion_behavior_sustained_sliding_or_lifetime_change_without_text_leakage",
    "Damped Oscillation": "must_show_repeated_oscillation_cycles_with_visibly_decaying_amplitude",
    "Shock Wave Propagation": "must_show_clear_shock_front_or_compression_front_propagating_not_static_schlieren_frame",
    "Stokes Flow Kinematic Reversibility": (
        "must_show_forward_laminar_deformation_or_mixing_followed_by_reverse_motion_restoring_the_pattern_not_only_static_colored_fluid"
    ),
    "Blue Bottle Reaction": "must_show_shaking_or_oxygenation_cycle_and_reversible_color_recovery_without_title_leakage",
    "Benedict Positive Reducing-Sugar Reaction": (
        "must_show_reagent_heating_and_progressive_color_or_precipitate_evolution_without_text_leakage"
    ),
    "Electrodeposition Dendrite Growth": (
        "must_show_branching_metal_dendrite_or_crystal_growth_from_an_electrode_over_time_not_only_existing_crystals"
    ),
    "Coffee-Ring Formation": "must_show_evaporation_period_and_particle_deposition_front_forming_not_only_final_ring",
    "Diffusion Flame": "must_show_nonpremixed_fuel_oxidizer_interface_or_flame_establishment_not_just_fire",
    "Flame Front Propagation": "must_show_reactive_flame_front_advancing_through_fuel_or_mixture_not_generic_fire_motion",
    "Convective Smoke Plume Rise": "must_show_buoyancy_driven_plume_generation_rise_and_expansion_not_just_smoke",
    "Ice Cliff Calving": "must_show_crack_or_instability_then_ice_cliff_detachment_and_fall_sequence",
    "Lava Dome Collapse": "must_show_dome_instability_collapse_and_pyroclastic_or_plume_response_sequence",
    "Storm Surge Propagation": "must_show_water_level_or_inundation_front_progression_not_only_path_map_or_warning_overlay",
    "Aeolian Saltation": "must_show_near_ground_grain_hopping_transport_not_generic_dust_or_wind",
    "Seismic Wave Propagation": "must_show_wavefront_or_ground_motion_propagating_outward_over_time_not_only_static_map_or_epicenter_marker",
    "Cutbank Erosion / Point-Bar Deposition": (
        "must_show_channel_boundary_retreat_and_opposite_bar_or_inner_bank_accretion_over_time_not_static_meander_geometry"
    ),
    "Plunging Breaker": "must_show_crest_steepening_overturning_entrainment_and_breaking_sequence",
    "Barchan Dune Migration": "must_show_real_time_lapse_dune_translation_not_static_aerial_flyover",
    "Marangoni-Driven Flow": (
        "must_show_surface_tension_gradient_driven_directed_transport_with_source_double_check"
    ),
    "Endocytosis": "must_show_membrane_invagination_and_vesicle_formation_not_static_cell_image",
    "Exocytosis": "must_show_vesicle_motion_fusion_or_release_not_static_cell_image",
    "Droplet Rebound": "must_show_impact_deformation_capillary_retraction_and_liftoff_sequence",
    "Droplet Impact Spreading": "must_show_impact_then_radial_spreading_sequence",
    "Gel Swelling": "must_show_osmotic_or_solvent_driven_volume_increase_over_time",
    "Biofilm Expansion": "must_show_colony_front_expansion_or_collective_growth_dynamics_over_time",
    "Ciliary Beating": "must_show_coordinated_repeated_ciliary_motion_or_metachronal_pattern_not_static_cell_structure",
    "Lamellipodium Extension": "must_show_actin_driven_sheetlike_cell_edge_protrusion_over_time",
    "Filopodium Protrusion": "must_show_thin_actin_rich_protrusion_extension_and_retraction_or_exploration_over_time",
}

BETTER_NAMES = {
    "Stomatal Opening and Closing": (
        "Guard-Cell Turgor-Driven Stomatal Aperture Dynamics",
        "保卫细胞膨压驱动气孔孔径动态",
    ),
    "Medusan Bell-Contraction Jet Propulsion": (
        "Medusan Jet Propulsion by Bell Contraction",
        "水母伞体收缩喷射推进",
    ),
    "Embryonic Cleavage Division Sequence": (
        "Early Embryonic Cleavage Sequence",
        "早期胚胎卵裂序列",
    ),
    "Convective Smoke Plume Rise": (
        "Buoyancy-Driven Smoke Plume Rise",
        "浮力驱动烟羽上升",
    ),
    "Dune Slip-Face Avalanche": (
        "Dune Slip-Face Grain Avalanche",
        "沙丘滑移面颗粒雪崩",
    ),
    "Droplet Rebound": (
        "Inertia-Capillarity Droplet Rebound",
        "惯性-毛细液滴反弹",
    ),
    "Droplet Impact Spreading": (
        "Inertia-Driven Droplet Impact Spreading",
        "惯性驱动液滴撞击铺展",
    ),
    "Gel Swelling": (
        "Osmotic Gel Swelling Dynamics",
        "渗透压驱动凝胶溶胀动态",
    ),
    "Biofilm Expansion": (
        "Biofilm Colony Expansion Dynamics",
        "生物膜群落扩张动态",
    ),
    "Standing Wave Formation": (
        "Standing-Wave Mode Formation",
        "驻波模态形成",
    ),
    "Coherent Wave Interference": (
        "Coherent Interference Pattern Formation",
        "相干干涉图样形成",
    ),
    "Droplet Coalescence": (
        "Capillary-Driven Droplet Coalescence",
        "毛细驱动液滴并合",
    ),
    "Capillary Breakup": (
        "Capillary-Driven Jet/Thread Breakup",
        "毛细驱动射流/液丝断裂",
    ),
    "Crystal Nucleation": (
        "Crystal Nucleation-and-Growth Dynamics",
        "晶体成核-生长动态",
    ),
    "Precipitation Front Propagation": (
        "Reaction-Precipitation Front Propagation",
        "反应-沉淀前沿推进",
    ),
    "Flame Front Propagation": (
        "Reactive Flame-Front Propagation",
        "反应性火焰前沿传播",
    ),
    "Ciliary Beating": (
        "Coordinated Ciliary Beating Dynamics",
        "协同纤毛摆动动态",
    ),
    "Filopodium Protrusion": (
        "Actin-Driven Filopodium Protrusion",
        "肌动蛋白驱动丝状伪足探伸",
    ),
    "Lamellipodium Extension": (
        "Actin-Driven Lamellipodium Extension",
        "肌动蛋白驱动片状伪足延伸",
    ),
}


def base_gate(row: dict[str, str]) -> str:
    text = row["concept_en"]
    if text in STRICT_NAME_GATES:
        return STRICT_NAME_GATES[text]
    if row["domain"] == "physics_physical_systems":
        return "video_must_show_named_dynamic_mechanism_sequence_without_title_or_source_leakage"
    if row["domain"] == "chemistry_materials_change":
        return "video_must_show_material_or_reaction_state_evolution; source_text_may_only_double_check_not_supply_answer"
    if row["domain"] == "biology_living_systems":
        return "video_must_show_biological_dynamic_sequence_or_strategy_not_species_or_generic_action"
    if row["domain"] == "earth_environmental_systems":
        return "video_must_show_process_evolution_or_instability_sequence_not_static_landform_or_event_label"
    return "video_must_show_temporal_process_required_for_named_dynamic_concept"


def classify(row: dict[str, str]) -> tuple[str, str]:
    concept = row["concept_en"]
    subdomain = row["subdomain_zh"]
    priority = row["priority"]

    if subdomain == "球类专项动作与战术序列":
        return "defer_or_remove", "ball_sport_terms_shift_story_toward_action_or_play_recognition"
    if subdomain == "人体专项动作与运动技术":
        return "stress_slice", "formal_movement_taxonomy_but_not_main_scientific_dynamic_knowledge"
    if concept in DEFER_CONCEPTS:
        return "defer_or_remove", DEFER_CONCEPTS[concept]
    if concept in EXTENSION_CONCEPTS:
        return "extension", EXTENSION_CONCEPTS[concept]
    if concept in STRICT_NAME_GATES:
        return "strict_main_candidate", "valid_name_but_requires_extra_visual_gate"
    if priority == "A":
        return "core_main", "strong_named_temporal_signature"
    if priority == "B":
        return "strict_main_candidate", "usable_only_after_video_specific_gate"
    return "extension", "candidate_is_source_or_availability_heavy"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_concept_inventory_tiered_v1.csv"))
    parser.add_argument("--report", type=Path, default=Path("reports/vdcr_concept_inventory_tier_summary_v1.md"))
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(handle.readline() for _ in [])

    original_fields = list(rows[0].keys()) if rows else []
    new_fields = original_fields + [
        "concept_validity_tier",
        "tier_reason",
        "recommended_answer_en",
        "recommended_answer_zh",
        "production_gate",
    ]

    output_rows: list[dict[str, str]] = []
    for row in rows:
        tier, reason = classify(row)
        better_en, better_zh = BETTER_NAMES.get(row["concept_en"], (row["concept_en"], row["concept_zh"]))
        out = dict(row)
        out.update(
            {
                "concept_validity_tier": tier,
                "tier_reason": reason,
                "recommended_answer_en": better_en,
                "recommended_answer_zh": better_zh,
                "production_gate": base_gate(row),
            }
        )
        output_rows.append(out)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    tier_counts = Counter(row["concept_validity_tier"] for row in output_rows)
    domain_tier_counts = Counter((row["domain_zh"], row["concept_validity_tier"]) for row in output_rows)
    rename_rows = [row for row in output_rows if row["recommended_answer_en"] != row["concept_en"]]

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8") as handle:
        handle.write("# VDCR Tiered Concept Inventory Summary\n\n")
        handle.write("Generated from `data/vdcr_concept_inventory_v1.csv` using `scripts/build_vdcr_tiered_inventory.py`.\n\n")
        handle.write("## Tier Counts\n\n")
        handle.write("| Tier | Count |\n|---|---:|\n")
        for tier, count in sorted(tier_counts.items()):
            handle.write(f"| `{tier}` | {count} |\n")
        handle.write("\n## Domain x Tier Counts\n\n")
        handle.write("| Domain | Tier | Count |\n|---|---|---:|\n")
        for (domain, tier), count in sorted(domain_tier_counts.items()):
            handle.write(f"| {domain} | `{tier}` | {count} |\n")
        handle.write("\n## Recommended Renames\n\n")
        handle.write("| Current | Recommended | Reason |\n|---|---|---|\n")
        for row in rename_rows:
            handle.write(
                f"| `{row['concept_en']}` | `{row['recommended_answer_en']}` | make the answer name more mechanism-bearing |\n"
            )

    print(f"rows={len(output_rows)} wrote {args.output}")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
