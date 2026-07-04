"""
Classe Emprunt — représente un emprunt d'un document par un adhérent.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

from exceptions.custom_exceptions import ValeurInvalideError

logger = logging.getLogger(__name__)


class Emprunt:
    """
    Représente un emprunt d'un document par un adhérent.

    Un Emprunt est créé et possédé par un Adherent (relation de composition) :
    son cycle de vie est lié à celui de l'adhérent.

    Attributes:
        id_emprunt (str): Identifiant unique de l'emprunt.
        reference_document (str): Référence du document emprunté.
        titre_document (str): Titre du document (pour lisibilité).
        date_emprunt (date): Date d'emprunt.
        date_retour_prevue (date): Date de retour attendue.
        date_retour_effective (Optional[date]): Date réelle de retour (None si en cours).
        amende_payee (float): Montant de l'amende payée lors du retour.
    """

    def __init__(
        self,
        id_emprunt: str,
        reference_document: str,
        titre_document: str,
        date_emprunt: date,
        duree_jours: int,
    ) -> None:
        """
        Initialise un emprunt.

        Args:
            id_emprunt: Identifiant unique.
            reference_document: Référence du document.
            titre_document: Titre du document.
            date_emprunt: Date de début d'emprunt.
            duree_jours: Durée autorisée en jours.

        Raises:
            ValeurInvalideError: Si les paramètres sont invalides.
        """
        if not id_emprunt or not id_emprunt.strip():
            raise ValeurInvalideError("id_emprunt", "ne peut pas être vide")
        if not reference_document or not reference_document.strip():
            raise ValeurInvalideError("reference_document", "ne peut pas être vide")
        if duree_jours <= 0:
            raise ValeurInvalideError("duree_jours", "doit être supérieure à 0")

        self._id_emprunt: str = id_emprunt.strip()
        self._reference_document: str = reference_document.strip()
        self._titre_document: str = titre_document.strip()
        self._date_emprunt: date = date_emprunt
        self._date_retour_prevue: date = date_emprunt + timedelta(days=duree_jours)
        self._date_retour_effective: Optional[date] = None
        self._amende_payee: float = 0.0

        logger.info(
            "Emprunt créé : %s pour document '%s', retour prévu le %s",
            self._id_emprunt,
            self._reference_document,
            self._date_retour_prevue,
        )

    # ── Propriétés ────────────────────────────────────────────────────────────

    @property
    def id_emprunt(self) -> str:
        return self._id_emprunt

    @property
    def reference_document(self) -> str:
        return self._reference_document

    @property
    def titre_document(self) -> str:
        return self._titre_document

    @property
    def date_emprunt(self) -> date:
        return self._date_emprunt

    @property
    def date_retour_prevue(self) -> date:
        return self._date_retour_prevue

    @property
    def date_retour_effective(self) -> Optional[date]:
        return self._date_retour_effective

    @property
    def amende_payee(self) -> float:
        return self._amende_payee

    @property
    def est_en_cours(self) -> bool:
        """True si l'emprunt n'est pas encore clôturé."""
        return self._date_retour_effective is None

    # ── Méthodes ──────────────────────────────────────────────────────────────

    def jours_retard(self, date_reference: Optional[date] = None) -> int:
        """
        Calcule le nombre de jours de retard.

        Args:
            date_reference: Date de comparaison (aujourd'hui par défaut).

        Returns:
            Nombre de jours de retard (0 si pas de retard).
        """
        ref = date_reference or date.today()
        if not self.est_en_cours:
            ref = self._date_retour_effective
        delta = (ref - self._date_retour_prevue).days
        return max(0, delta)

    def cloture(self, date_retour: date, amende: float) -> None:
        """
        Clôture l'emprunt lors du retour du document.

        Args:
            date_retour: Date effective de retour.
            amende: Montant de l'amende calculée.

        Raises:
            ValeurInvalideError: Si l'emprunt est déjà clôturé ou la date invalide.
        """
        if not self.est_en_cours:
            raise ValeurInvalideError("emprunt", "déjà clôturé")
        if date_retour < self._date_emprunt:
            raise ValeurInvalideError(
                "date_retour", "ne peut pas être antérieure à la date d'emprunt"
            )
        self._date_retour_effective = date_retour
        self._amende_payee = amende
        logger.info(
            "Emprunt %s clôturé le %s — amende : %.0f FCFA",
            self._id_emprunt,
            date_retour,
            amende,
        )

    def to_dict(self) -> dict:
        """Sérialise l'emprunt pour la persistance JSON."""
        return {
            "id_emprunt": self._id_emprunt,
            "reference_document": self._reference_document,
            "titre_document": self._titre_document,
            "date_emprunt": self._date_emprunt.isoformat(),
            "date_retour_prevue": self._date_retour_prevue.isoformat(),
            "date_retour_effective": (
                self._date_retour_effective.isoformat()
                if self._date_retour_effective
                else None
            ),
            "amende_payee": self._amende_payee,
        }

    def __repr__(self) -> str:
        statut = "en cours" if self.est_en_cours else "clôturé"
        return (
            f"Emprunt(id='{self._id_emprunt}', "
            f"doc='{self._reference_document}', {statut})"
        )
