"""
Classe Adherent — membre de la bibliothèque universitaire.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date
from typing import List, Optional

from models.emprunt import Emprunt
from models.enums import CategorieAdherent
from exceptions.custom_exceptions import (
    EmpruntIntrouvableError,
    QuotaEmpruntDepasseError,
    ValeurInvalideError,
)

logger = logging.getLogger(__name__)

# Quotas d'emprunts simultanés par catégorie
QUOTAS: dict[CategorieAdherent, int] = {
    CategorieAdherent.ETUDIANT: 3,
    CategorieAdherent.ENSEIGNANT: 7,
    CategorieAdherent.EXTERNE: 1,
}


class Adherent:
    """
    Représente un adhérent de la bibliothèque universitaire.

    Relation de COMPOSITION avec Emprunt : l'adhérent crée et possède
    son historique d'emprunts. Les objets Emprunt ne peuvent exister
    indépendamment de l'adhérent qui les a initiés.

    Attributes:
        identifiant (str): Identifiant unique de l'adhérent.
        nom (str): Nom de l'adhérent.
        prenom (str): Prénom de l'adhérent.
        email (str): Adresse e-mail.
        categorie (CategorieAdherent): Catégorie (ETUDIANT, ENSEIGNANT, EXTERNE).
    """

    def __init__(
        self,
        identifiant: str,
        nom: str,
        prenom: str,
        email: str,
        categorie: CategorieAdherent,
    ) -> None:
        """
        Initialise un adhérent.

        Args:
            identifiant: Identifiant unique (ex. numéro étudiant).
            nom: Nom de famille.
            prenom: Prénom.
            email: Adresse e-mail valide.
            categorie: Catégorie de l'adhérent.

        Raises:
            ValeurInvalideError: Si un champ obligatoire est invalide.
        """
        if not identifiant or not identifiant.strip():
            raise ValeurInvalideError("identifiant", "ne peut pas être vide")
        if not nom or not nom.strip():
            raise ValeurInvalideError("nom", "ne peut pas être vide")
        if not prenom or not prenom.strip():
            raise ValeurInvalideError("prenom", "ne peut pas être vide")
        if not email or "@" not in email:
            raise ValeurInvalideError("email", "doit contenir un '@'")
        if not isinstance(categorie, CategorieAdherent):
            raise ValeurInvalideError("categorie", "doit être une CategorieAdherent")

        self._identifiant: str = identifiant.strip()
        self._nom: str = nom.strip()
        self._prenom: str = prenom.strip()
        self._email: str = email.strip()
        self._categorie: CategorieAdherent = categorie
        # COMPOSITION : l'adhérent crée et gère ses propres emprunts
        self._historique_emprunts: List[Emprunt] = []

        logger.info("Adhérent créé : %s %s (%s)", prenom, nom, identifiant)

    # ── Propriétés ────────────────────────────────────────────────────────────

    @property
    def identifiant(self) -> str:
        return self._identifiant

    @property
    def nom(self) -> str:
        return self._nom

    @property
    def prenom(self) -> str:
        return self._prenom

    @property
    def email(self) -> str:
        return self._email

    @property
    def categorie(self) -> CategorieAdherent:
        return self._categorie

    @property
    def quota_max(self) -> int:
        """Nombre maximum d'emprunts simultanés selon la catégorie."""
        return QUOTAS[self._categorie]

    @property
    def historique_emprunts(self) -> List[Emprunt]:
        """Liste complète des emprunts (en cours + clôturés)."""
        return list(self._historique_emprunts)

    @property
    def emprunts_en_cours(self) -> List[Emprunt]:
        """Liste des emprunts actuellement actifs."""
        return [e for e in self._historique_emprunts if e.est_en_cours]

    @property
    def nom_complet(self) -> str:
        return f"{self._prenom} {self._nom}"

    # ── Méthodes métier ───────────────────────────────────────────────────────

    def creer_emprunt(
        self,
        reference_document: str,
        titre_document: str,
        date_emprunt: date,
        duree_jours: int,
    ) -> Emprunt:
        """
        Crée un nouvel emprunt pour cet adhérent (COMPOSITION).

        Args:
            reference_document: Référence du document emprunté.
            titre_document: Titre du document.
            date_emprunt: Date de début d'emprunt.
            duree_jours: Durée d'emprunt autorisée.

        Returns:
            L'objet Emprunt créé.

        Raises:
            QuotaEmpruntDepasseError: Si le quota d'emprunts est atteint.
        """
        if len(self.emprunts_en_cours) >= self.quota_max:
            raise QuotaEmpruntDepasseError(self.nom_complet, self.quota_max)

        id_emprunt = str(uuid.uuid4())[:8].upper()
        emprunt = Emprunt(
            id_emprunt=id_emprunt,
            reference_document=reference_document,
            titre_document=titre_document,
            date_emprunt=date_emprunt,
            duree_jours=duree_jours,
        )
        self._historique_emprunts.append(emprunt)
        logger.info(
            "Nouvel emprunt %s créé pour %s — document '%s'",
            id_emprunt,
            self.nom_complet,
            reference_document,
        )
        return emprunt

    def get_emprunt_actif(self, reference_document: str) -> Emprunt:
        """
        Retourne l'emprunt actif pour un document donné.

        Args:
            reference_document: Référence du document recherché.

        Returns:
            L'objet Emprunt actif.

        Raises:
            EmpruntIntrouvableError: Si aucun emprunt actif n'est trouvé.
        """
        for emprunt in self._historique_emprunts:
            if emprunt.reference_document == reference_document and emprunt.est_en_cours:
                return emprunt
        raise EmpruntIntrouvableError(reference_document)

    def a_emprunte_document(self, reference_document: str) -> bool:
        """Vérifie si l'adhérent a un emprunt actif sur ce document."""
        return any(
            e.reference_document == reference_document and e.est_en_cours
            for e in self._historique_emprunts
        )

    def total_amendes_dues(self, date_reference: Optional[date] = None) -> float:
        """
        Calcule le total des amendes courantes (emprunts en retard non clôturés).

        Args:
            date_reference: Date de calcul (aujourd'hui par défaut).

        Returns:
            Total en FCFA.
        """
        ref = date_reference or date.today()
        total = sum(
            e.jours_retard(ref) for e in self.emprunts_en_cours
        )
        return float(total)

    def to_dict(self) -> dict:
        """Sérialise l'adhérent pour la persistance JSON."""
        return {
            "identifiant": self._identifiant,
            "nom": self._nom,
            "prenom": self._prenom,
            "email": self._email,
            "categorie": self._categorie.value,
            "historique_emprunts": [e.to_dict() for e in self._historique_emprunts],
        }

    def __repr__(self) -> str:
        return (
            f"Adherent(id='{self._identifiant}', "
            f"nom='{self.nom_complet}', "
            f"categorie={self._categorie.value})"
        )

    def __str__(self) -> str:
        return (
            f"{self.nom_complet} [{self._categorie.value}] "
            f"— {len(self.emprunts_en_cours)}/{self.quota_max} emprunt(s)"
        )
