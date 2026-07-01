"""Exceptions métier personnalisées."""
from exceptions.custom_exceptions import (
    BibliothèqueError,
    DocumentNonDisponibleError,
    QuotaEmpruntDepasseError,
    DocumentIntrouvableError,
    AdherentIntrouvableError,
    EmpruntIntrouvableError,
    ValeurInvalideError,
)

__all__ = [
    "BibliothèqueError",
    "DocumentNonDisponibleError",
    "QuotaEmpruntDepasseError",
    "DocumentIntrouvableError",
    "AdherentIntrouvableError",
    "EmpruntIntrouvableError",
    "ValeurInvalideError",
]
