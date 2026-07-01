"""
Classe concrète Livre, héritant de DocumentBase.
"""

from __future__ import annotations

import logging

from models.document_base import DocumentBase
from models.enums import StatutDocument, TypeDocument
from exceptions.custom_exceptions import DocumentNonDisponibleError, ValeurInvalideError

logger = logging.getLogger(__name__)

AMENDE_PAR_JOUR: float = 50.0   # francs CFA
DUREE_MAX_JOURS: int = 21


class Livre(DocumentBase):
    """
    Représente un livre dans la bibliothèque universitaire.

    Règles d'emprunt :
        - Durée maximale : 21 jours.
        - Amende en cas de retard : 50 FCFA / jour.

    Attributes:
        auteur (str): Auteur du livre.
        isbn (str): Numéro ISBN.
        genre (str): Genre littéraire ou disciplinaire.
        nombre_pages (int): Nombre de pages.
    """

    def __init__(
        self,
        titre: str,
        reference: str,
        annee_publication: int,
        auteur: str,
        isbn: str,
        genre: str,
        nombre_pages: int,
    ) -> None:
        """
        Initialise un Livre.

        Args:
            titre: Titre du livre.
            reference: Référence interne unique.
            annee_publication: Année de publication.
            auteur: Nom de l'auteur.
            isbn: Code ISBN.
            genre: Genre du livre.
            nombre_pages: Nombre de pages (> 0).

        Raises:
            ValeurInvalideError: Si auteur/isbn/genre sont vides
                                 ou si nombre_pages <= 0.
        """
        super().__init__(titre, reference, annee_publication)

        if not auteur or not auteur.strip():
            raise ValeurInvalideError("auteur", "ne peut pas être vide")
        if not isbn or not isbn.strip():
            raise ValeurInvalideError("isbn", "ne peut pas être vide")
        if not genre or not genre.strip():
            raise ValeurInvalideError("genre", "ne peut pas être vide")
        if nombre_pages <= 0:
            raise ValeurInvalideError("nombre_pages", "doit être supérieur à 0")

        self._auteur: str = auteur.strip()
        self._isbn: str = isbn.strip()
        self._genre: str = genre.strip()
        self._nombre_pages: int = nombre_pages

    # ── Propriétés ────────────────────────────────────────────────────────────

    @property
    def auteur(self) -> str:
        """Auteur du livre."""
        return self._auteur

    @property
    def isbn(self) -> str:
        """Numéro ISBN."""
        return self._isbn

    @property
    def genre(self) -> str:
        """Genre du livre."""
        return self._genre

    @property
    def nombre_pages(self) -> int:
        """Nombre de pages."""
        return self._nombre_pages

    @property
    def type_document(self) -> TypeDocument:
        """Type : LIVRE."""
        return TypeDocument.LIVRE

    @property
    def duree_emprunt_max(self) -> int:
        """Durée maximale d'emprunt : 21 jours."""
        return DUREE_MAX_JOURS

    # ── Méthodes abstraites implémentées ──────────────────────────────────────

    def emprunter(self) -> None:
        """
        Passe le statut du livre à EMPRUNTE.

        Raises:
            DocumentNonDisponibleError: Si le livre n'est pas DISPONIBLE.
        """
        if self._statut != StatutDocument.DISPONIBLE:
            raise DocumentNonDisponibleError(self._titre, self._statut.value)
        self._statut = StatutDocument.EMPRUNTE
        logger.info("Livre '%s' emprunté.", self._reference)

    def calculer_amende(self, jours_retard: int) -> float:
        """
        Calcule l'amende pour retard sur un livre.

        Args:
            jours_retard: Nombre de jours de retard (>= 0).

        Returns:
            Montant en FCFA (0.0 si pas de retard).
        """
        if jours_retard < 0:
            raise ValeurInvalideError("jours_retard", "ne peut pas être négatif")
        return jours_retard * AMENDE_PAR_JOUR

    # ── Sérialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Sérialise le livre pour la persistance JSON."""
        data = super().to_dict()
        data.update({
            "auteur": self._auteur,
            "isbn": self._isbn,
            "genre": self._genre,
            "nombre_pages": self._nombre_pages,
        })
        return data
