"""Bounded-context modules — each is a candidate for future service extraction.

A module may import from ``platform`` and its own package, but must reach other
modules only through their ``ports`` (enforced by the root ``.importlinter``).
"""
