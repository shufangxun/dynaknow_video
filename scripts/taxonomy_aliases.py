"""Small taxonomy compatibility helpers for v1 workflow scripts."""

from __future__ import annotations


SUBDOMAIN_ALIASES = {
    "plant_water_transport": "plant_water_relations_and_turgor",
}

DOMAIN_ALIASES = {
    "engineered_systems_and_operations": "engineering_operational_systems",
}


def normalize_domain(domain: str) -> str:
    value = (domain or "").strip()
    return DOMAIN_ALIASES.get(value, value)


def normalize_subdomain(subdomain: str) -> str:
    value = (subdomain or "").strip()
    return SUBDOMAIN_ALIASES.get(value, value)


def normalize_domain_subdomain(domain: str, subdomain: str) -> tuple[str, str]:
    return normalize_domain(domain), normalize_subdomain(subdomain)
