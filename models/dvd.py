"""
Classe concrète DVD, héritant de DocumentBase.
"""

from __future__ import annotations

import logging

from models.document_base import DocumentBase
from models.enums import StatutDocument, TypeDocument
from exceptions.custom_exceptions import DocumentNonDisponibleError, ValeurInvalideError

logger = logging.getLogger(__name__)

AMENDE_PAR_JOUR: float = 100.0
DUREE_MAX_JOURS: int = 3


class DVD(DocumentBase):
    """
    Représente un DVD (documentaire, cours enregistré, film pédagogique).

    Règles d'emprunt :
        - Durée maximale : 3 jours.
        - Amende en cas de retard : 100 FCFA / jour.

    Attributes:
        realisateur (str): Réalisateur ou producteur.
        duree_minutes (int): Durée du contenu en minutes.
        categorie (str): Catégorie (documentaire, cours, fiction…).
        langue (str): Langue principale du DVD.
    """

    def __init__(
        self,
        titre: str,
        reference: str,
        annee_publication: int,
        realisateur: str,
        duree_minutes: int,
        categorie: str,
        langue: str = "français",
    ) -> None:
        super().__init__(titre, reference, annee_publication)

        if not realisateur or not realisateur.strip():
            raise ValeurInvalideError("realisateur", "ne peut pas être vide")
        if duree_minutes <= 0:
            raise ValeurInvalideError("duree_minutes", "doit être supérieure à 0")
        if not categorie or not categorie.strip():
            raise ValeurInvalideError("categorie", "ne peut pas être vide")

        self._realisateur: str = realisateur.strip()
        self._duree_minutes: int = duree_minutes
        self._categorie: str = categorie.strip()
        self._langue: str = langue.strip()

    @property
    def realisateur(self) -> str:
        return self._realisateur

    @property
    def duree_minutes(self) -> int:
        return self._duree_minutes

    @property
    def categorie(self) -> str:
        return self._categorie

    @property
    def langue(self) -> str:
        return self._langue

    @property
    def type_document(self) -> TypeDocument:
        return TypeDocument.DVD

    @property
    def duree_emprunt_max(self) -> int:
        return DUREE_MAX_JOURS

    def emprunter(self) -> None:
        """
        Passe le statut du DVD à EMPRUNTE.

        Raises:
            DocumentNonDisponibleError: Si le DVD n'est pas DISPONIBLE.
        """
        if self._statut != StatutDocument.DISPONIBLE:
            raise DocumentNonDisponibleError(self._titre, self._statut.value)
        self._statut = StatutDocument.EMPRUNTE
        logger.info("DVD '%s' emprunté.", self._reference)

    def calculer_amende(self, jours_retard: int) -> float:
        """
        Calcule l'amende pour retard sur un DVD.

        Args:
            jours_retard: Nombre de jours de retard.

        Returns:
            Montant en FCFA.
        """
        if jours_retard < 0:
            raise ValeurInvalideError("jours_retard", "ne peut pas être négatif")
        return jours_retard * AMENDE_PAR_JOUR

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "realisateur": self._realisateur,
            "duree_minutes": self._duree_minutes,
            "categorie": self._categorie,
            "langue": self._langue,
        })
        return data
