"""
Classe concrète Revue, héritant de DocumentBase.
"""

from __future__ import annotations

import logging

from models.document_base import DocumentBase
from models.enums import StatutDocument, TypeDocument
from exceptions.custom_exceptions import DocumentNonDisponibleError, ValeurInvalideError

logger = logging.getLogger(__name__)

AMENDE_PAR_JOUR: float = 25.0
DUREE_MAX_JOURS: int = 7


class Revue(DocumentBase):
    """
    Représente une revue scientifique ou périodique.

    Règles d'emprunt :
        - Durée maximale : 7 jours.
        - Amende en cas de retard : 25 FCFA / jour.

    Attributes:
        editeur (str): Maison d'édition.
        numero (str): Numéro de la revue.
        periodicite (str): Fréquence de parution (ex. mensuelle, trimestrielle).
        domaine (str): Domaine scientifique couvert.
    """

    def __init__(
        self,
        titre: str,
        reference: str,
        annee_publication: int,
        editeur: str,
        numero: str,
        periodicite: str,
        domaine: str,
    ) -> None:
        super().__init__(titre, reference, annee_publication)

        if not editeur or not editeur.strip():
            raise ValeurInvalideError("editeur", "ne peut pas être vide")
        if not numero or not numero.strip():
            raise ValeurInvalideError("numero", "ne peut pas être vide")
        if not periodicite or not periodicite.strip():
            raise ValeurInvalideError("periodicite", "ne peut pas être vide")
        if not domaine or not domaine.strip():
            raise ValeurInvalideError("domaine", "ne peut pas être vide")

        self._editeur: str = editeur.strip()
        self._numero: str = numero.strip()
        self._periodicite: str = periodicite.strip()
        self._domaine: str = domaine.strip()

    @property
    def editeur(self) -> str:
        return self._editeur

    @property
    def numero(self) -> str:
        return self._numero

    @property
    def periodicite(self) -> str:
        return self._periodicite

    @property
    def domaine(self) -> str:
        return self._domaine

    @property
    def type_document(self) -> TypeDocument:
        return TypeDocument.REVUE

    @property
    def duree_emprunt_max(self) -> int:
        return DUREE_MAX_JOURS

    def emprunter(self) -> None:
        """
        Passe le statut de la revue à EMPRUNTE.

        Raises:
            DocumentNonDisponibleError: Si la revue n'est pas DISPONIBLE.
        """
        if self._statut != StatutDocument.DISPONIBLE:
            raise DocumentNonDisponibleError(self._titre, self._statut.value)
        self._statut = StatutDocument.EMPRUNTE
        logger.info("Revue '%s' empruntée.", self._reference)

    def calculer_amende(self, jours_retard: int) -> float:
        """
        Calcule l'amende pour retard sur une revue.

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
            "editeur": self._editeur,
            "numero": self._numero,
            "periodicite": self._periodicite,
            "domaine": self._domaine,
        })
        return data
