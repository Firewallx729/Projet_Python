"""
Classe abstraite de base pour tous les documents de la bibliothèque.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from models.enums import StatutDocument, TypeDocument
from exceptions.custom_exceptions import ValeurInvalideError

logger = logging.getLogger(__name__)


class DocumentBase(ABC):
    """
    Classe abstraite représentant un document de la bibliothèque universitaire.

    Tous les types de documents (Livre, Revue, DVD, Mémoire) héritent de cette
    classe et doivent implémenter les méthodes abstraites `emprunter` et
    `calculer_amende`.

    Attributes:
        titre (str): Titre du document.
        reference (str): Référence unique du document.
        statut (StatutDocument): Statut courant du document.
        annee_publication (int): Année de publication.
    """

    def __init__(
        self,
        titre: str,
        reference: str,
        annee_publication: int,
    ) -> None:
        """
        Initialise un document.

        Args:
            titre: Titre du document.
            reference: Référence unique (ex. ISBN, code interne).
            annee_publication: Année de publication.

        Raises:
            ValeurInvalideError: Si titre ou référence sont vides,
                                 ou si l'année est incohérente.
        """
        if not titre or not titre.strip():
            raise ValeurInvalideError("titre", "ne peut pas être vide")
        if not reference or not reference.strip():
            raise ValeurInvalideError("reference", "ne peut pas être vide")
        if not (1450 <= annee_publication <= date.today().year):
            raise ValeurInvalideError(
                "annee_publication",
                f"doit être comprise entre 1450 et {date.today().year}",
            )

        self._titre: str = titre.strip()
        self._reference: str = reference.strip()
        self._statut: StatutDocument = StatutDocument.DISPONIBLE
        self._annee_publication: int = annee_publication

        logger.debug("Document créé : [%s] %s", self._reference, self._titre)

    # ── Propriétés ────────────────────────────────────────────────────────────

    @property
    def titre(self) -> str:
        """Titre du document."""
        return self._titre

    @property
    def reference(self) -> str:
        """Référence unique du document."""
        return self._reference

    @property
    def statut(self) -> StatutDocument:
        """Statut courant du document."""
        return self._statut

    @statut.setter
    def statut(self, nouveau_statut: StatutDocument) -> None:
        """Met à jour le statut du document."""
        if not isinstance(nouveau_statut, StatutDocument):
            raise ValeurInvalideError("statut", "doit être une instance de StatutDocument")
        logger.info(
            "Statut du document '%s' : %s → %s",
            self._reference,
            self._statut.value,
            nouveau_statut.value,
        )
        self._statut = nouveau_statut

    @property
    def annee_publication(self) -> int:
        """Année de publication."""
        return self._annee_publication

    @property
    @abstractmethod
    def type_document(self) -> TypeDocument:
        """Type de document (Livre, Revue, DVD, Mémoire)."""

    @property
    @abstractmethod
    def duree_emprunt_max(self) -> int:
        """Durée maximale d'emprunt en jours."""

    # ── Méthodes abstraites ───────────────────────────────────────────────────

    @abstractmethod
    def emprunter(self) -> None:
        """
        Effectue le changement d'état nécessaire lors d'un emprunt.

        Raises:
            DocumentNonDisponibleError: Si le document n'est pas DISPONIBLE.
        """

    @abstractmethod
    def calculer_amende(self, jours_retard: int) -> float:
        """
        Calcule le montant de l'amende pour un retard donné.

        Args:
            jours_retard: Nombre de jours de retard (>= 0).

        Returns:
            Montant de l'amende en francs CFA.
        """

    # ── Méthodes concrètes ────────────────────────────────────────────────────

    def retourner(self) -> None:
        """Remet le document au statut DISPONIBLE après retour."""
        self._statut = StatutDocument.DISPONIBLE
        logger.info("Document '%s' retourné et disponible.", self._reference)

    def marquer_perdu(self) -> None:
        """Marque le document comme PERDU."""
        self._statut = StatutDocument.PERDU
        logger.warning("Document '%s' marqué comme PERDU.", self._reference)

    def reserver(self) -> None:
        """Met le document en RESERVE."""
        self._statut = StatutDocument.RESERVE
        logger.info("Document '%s' mis en réservation.", self._reference)

    def est_disponible(self) -> bool:
        """Retourne True si le document est disponible à l'emprunt."""
        return self._statut == StatutDocument.DISPONIBLE

    def to_dict(self) -> dict:
        """
        Sérialise le document en dictionnaire (pour persistance JSON).

        Returns:
            Dictionnaire représentant le document.
        """
        return {
            "type": self.type_document.value,
            "titre": self._titre,
            "reference": self._reference,
            "statut": self._statut.value,
            "annee_publication": self._annee_publication,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ref='{self._reference}', "
            f"titre='{self._titre}', "
            f"statut={self._statut.value})"
        )

    def __str__(self) -> str:
        return f"[{self.type_document.value}] {self._titre} ({self._reference}) — {self._statut.value}"
