"""
Classe concrète Memoire, héritant de DocumentBase.
"""

from __future__ import annotations

import logging

from models.document_base import DocumentBase
from models.enums import StatutDocument, TypeDocument
from exceptions.custom_exceptions import DocumentNonDisponibleError, ValeurInvalideError

logger = logging.getLogger(__name__)

AMENDE_PAR_JOUR: float = 75.0
DUREE_MAX_JOURS: int = 14


class Memoire(DocumentBase):
    """
    Représente un mémoire ou une thèse universitaire.

    Règles d'emprunt :
        - Durée maximale : 14 jours.
        - Amende en cas de retard : 75 FCFA / jour.

    Attributes:
        auteur (str): Auteur du mémoire.
        domaine (str): Domaine ou filière (ex. Réseaux, Informatique).
        niveau (str): Niveau académique (Licence, Master, Doctorat).
        directeur (str): Directeur de recherche.
    """

    def __init__(
        self,
        titre: str,
        reference: str,
        annee_publication: int,
        auteur: str,
        domaine: str,
        niveau: str,
        directeur: str,
    ) -> None:
        super().__init__(titre, reference, annee_publication)

        if not auteur or not auteur.strip():
            raise ValeurInvalideError("auteur", "ne peut pas être vide")
        if not domaine or not domaine.strip():
            raise ValeurInvalideError("domaine", "ne peut pas être vide")
        if not niveau or not niveau.strip():
            raise ValeurInvalideError("niveau", "ne peut pas être vide")
        if not directeur or not directeur.strip():
            raise ValeurInvalideError("directeur", "ne peut pas être vide")

        self._auteur: str = auteur.strip()
        self._domaine: str = domaine.strip()
        self._niveau: str = niveau.strip()
        self._directeur: str = directeur.strip()

    @property
    def auteur(self) -> str:
        return self._auteur

    @property
    def domaine(self) -> str:
        return self._domaine

    @property
    def niveau(self) -> str:
        return self._niveau

    @property
    def directeur(self) -> str:
        return self._directeur

    @property
    def type_document(self) -> TypeDocument:
        return TypeDocument.MEMOIRE

    @property
    def duree_emprunt_max(self) -> int:
        return DUREE_MAX_JOURS

    def emprunter(self) -> None:
        """
        Passe le statut du mémoire à EMPRUNTE.

        Raises:
            DocumentNonDisponibleError: Si le mémoire n'est pas DISPONIBLE.
        """
        if self._statut != StatutDocument.DISPONIBLE:
            raise DocumentNonDisponibleError(self._titre, self._statut.value)
        self._statut = StatutDocument.EMPRUNTE
        logger.info("Mémoire '%s' emprunté.", self._reference)

    def calculer_amende(self, jours_retard: int) -> float:
        """
        Calcule l'amende pour retard sur un mémoire.

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
            "auteur": self._auteur,
            "domaine": self._domaine,
            "niveau": self._niveau,
            "directeur": self._directeur,
        })
        return data
