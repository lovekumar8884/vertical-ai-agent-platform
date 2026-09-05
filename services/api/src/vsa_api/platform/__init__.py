"""Cross-cutting platform layer.

Contains no domain logic. Bounded-context modules under ``vsa_api.modules`` may
import from here; this package must never import from them (enforced by the
repository-root ``.importlinter``).
"""
