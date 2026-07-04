"""
Classe Bibliotheque — gestionnaire principal (agrégation de documents).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Dict, List, Optional

from models.document_base import DocumentBase
from models.adherent import Adherent
from models.emprunt import Emprunt
from models.enums import CategorieAdherent, StatutDocument
from exceptions.custom_exceptions import (
    AdherentIntrouvableError,
    DocumentIntrouvableError,
    DocumentNonDisponibleError,
    ValeurInvalideError,
)

logger = logging.getLogger(__name__)


class Bibliotheque:
    """
    Gestionnaire central de la bibliothèque universitaire.

    Relation d'AGRÉGATION avec Document : les documents sont créés en dehors
    de la bibliothèque et ajoutés via ajouter_document(). Leur cycle de vie
    est indépendant de celui de la bibliothèque.

    Relation d'AGRÉGATION avec Adherent : même principe.

    Attributes:
        nom (str): Nom de la bibliothèque.
    """

    def __init__(self, nom: str) -> None:
        """
        Initialise la bibliothèque.

        Args:
            nom: Nom de l'établissement.

        Raises:
            ValeurInvalideError: Si le nom est vide.
        """
        if not nom or not nom.strip():
            raise ValeurInvalideError("nom", "ne peut pas être vide")

        self._nom: str = nom.strip()
        # AGRÉGATION : documents créés en dehors, ajoutés ici
        self._catalogue: Dict[str, DocumentBase] = {}
        # AGRÉGATION : adhérents créés en dehors, ajoutés ici
        self._adherents: Dict[str, Adherent] = {}

        logger.info("Bibliothèque '%s' initialisée.", self._nom)

    # ── Propriétés ────────────────────────────────────────────────────────────

    @property
    def nom(self) -> str:
        return self._nom

    @property
    def catalogue(self) -> Dict[str, DocumentBase]:
        """Vue en lecture seule du catalogue."""
        return dict(self._catalogue)

    @property
    def adherents(self) -> Dict[str, Adherent]:
        """Vue en lecture seule des adhérents."""
        return dict(self._adherents)

    # ── Gestion du catalogue (AGRÉGATION) ─────────────────────────────────────

    def ajouter_document(self, document: DocumentBase) -> None:
        """
        Ajoute un document au catalogue.

        Args:
            document: Document à ajouter (créé en dehors de la bibliothèque).

        Raises:
            ValeurInvalideError: Si la référence existe déjà.
        """
        if document.reference in self._catalogue:
            raise ValeurInvalideError(
                "reference", f"un document avec la référence '{document.reference}' existe déjà"
            )
        self._catalogue[document.reference] = document
        logger.info("Document ajouté au catalogue : %s", document.reference)

    def retirer_document(self, reference: str) -> DocumentBase:
        """
        Retire un document du catalogue.

        Args:
            reference: Référence du document.

        Returns:
            Le document retiré.

        Raises:
            DocumentIntrouvableError: Si la référence est introuvable.
        """
        if reference not in self._catalogue:
            raise DocumentIntrouvableError(reference)
        doc = self._catalogue.pop(reference)
        logger.info("Document retiré du catalogue : %s", reference)
        return doc

    def get_document(self, reference: str) -> DocumentBase:
        """
        Récupère un document par sa référence.

        Raises:
            DocumentIntrouvableError: Si introuvable.
        """
        if reference not in self._catalogue:
            raise DocumentIntrouvableError(reference)
        return self._catalogue[reference]

    # ── Gestion des adhérents ─────────────────────────────────────────────────

    def ajouter_adherent(self, adherent: Adherent) -> None:
        """
        Enregistre un adhérent.

        Args:
            adherent: Adhérent créé en dehors de la bibliothèque.

        Raises:
            ValeurInvalideError: Si l'identifiant existe déjà.
        """
        if adherent.identifiant in self._adherents:
            raise ValeurInvalideError(
                "identifiant", f"'{adherent.identifiant}' est déjà enregistré"
            )
        self._adherents[adherent.identifiant] = adherent
        logger.info("Adhérent enregistré : %s", adherent.identifiant)

    def get_adherent(self, identifiant: str) -> Adherent:
        """
        Récupère un adhérent par son identifiant.

        Raises:
            AdherentIntrouvableError: Si introuvable.
        """
        if identifiant not in self._adherents:
            raise AdherentIntrouvableError(identifiant)
        return self._adherents[identifiant]

    # ── Cycle d'emprunt ───────────────────────────────────────────────────────

    def emprunter_document(
        self,
        identifiant_adherent: str,
        reference_document: str,
        date_emprunt: Optional[date] = None,
    ) -> Emprunt:
        """
        Gère le cycle complet d'un emprunt.

        Args:
            identifiant_adherent: Identifiant de l'adhérent.
            reference_document: Référence du document.
            date_emprunt: Date d'emprunt (aujourd'hui par défaut).

        Returns:
            L'objet Emprunt créé.

        Raises:
            AdherentIntrouvableError: Si l'adhérent n'existe pas.
            DocumentIntrouvableError: Si le document n'existe pas.
            DocumentNonDisponibleError: Si le document n'est pas disponible.
            QuotaEmpruntDepasseError: Si l'adhérent a atteint son quota.
        """
        date_op = date_emprunt or date.today()
        adherent = self.get_adherent(identifiant_adherent)
        document = self.get_document(reference_document)

        # La méthode emprunter() lève DocumentNonDisponibleError si besoin
        document.emprunter()

        emprunt = adherent.creer_emprunt(
            reference_document=document.reference,
            titre_document=document.titre,
            date_emprunt=date_op,
            duree_jours=document.duree_emprunt_max,
        )

        logger.info(
            "Emprunt %s : adhérent '%s' — document '%s' — retour prévu %s",
            emprunt.id_emprunt,
            identifiant_adherent,
            reference_document,
            emprunt.date_retour_prevue,
        )
        return emprunt

    def retourner_document(
        self,
        identifiant_adherent: str,
        reference_document: str,
        date_retour: Optional[date] = None,
    ) -> float:
        """
        Gère le retour d'un document et calcule l'amende éventuelle.

        Args:
            identifiant_adherent: Identifiant de l'adhérent.
            reference_document: Référence du document.
            date_retour: Date de retour (aujourd'hui par défaut).

        Returns:
            Montant de l'amende en FCFA (0.0 si pas de retard).

        Raises:
            AdherentIntrouvableError: Si l'adhérent n'existe pas.
            DocumentIntrouvableError: Si le document n'existe pas.
            EmpruntIntrouvableError: Si aucun emprunt actif n'est trouvé.
        """
        date_op = date_retour or date.today()
        adherent = self.get_adherent(identifiant_adherent)
        document = self.get_document(reference_document)

        emprunt = adherent.get_emprunt_actif(reference_document)
        jours = emprunt.jours_retard(date_op)
        amende = document.calculer_amende(jours)

        emprunt.cloture(date_op, amende)
        document.retourner()

        if amende > 0:
            logger.warning(
                "Retour avec retard : %d jour(s) — amende %.0f FCFA — document '%s'",
                jours,
                amende,
                reference_document,
            )
        else:
            logger.info(
                "Retour sans retard : document '%s' par '%s'",
                reference_document,
                identifiant_adherent,
            )
        return amende

    def reserver_document(
        self,
        identifiant_adherent: str,
        reference_document: str,
    ) -> None:
        """
        Réserve un document qui est actuellement emprunté.

        Args:
            identifiant_adherent: Identifiant de l'adhérent.
            reference_document: Référence du document à réserver.

        Raises:
            DocumentIntrouvableError: Si le document n'existe pas.
            ValeurInvalideError: Si le document est déjà disponible ou perdu.
        """
        adherent = self.get_adherent(identifiant_adherent)
        document = self.get_document(reference_document)

        if document.statut == StatutDocument.DISPONIBLE:
            raise ValeurInvalideError(
                "statut", "le document est déjà disponible, empruntez-le directement"
            )
        if document.statut == StatutDocument.PERDU:
            raise ValeurInvalideError("statut", "le document est déclaré perdu")

        document.reserver()
        logger.info(
            "Document '%s' réservé par '%s'.",
            reference_document,
            adherent.identifiant,
        )

    # ── Statistiques / recherches ─────────────────────────────────────────────

    def documents_disponibles(self) -> List[DocumentBase]:
        """Retourne la liste des documents disponibles."""
        return [d for d in self._catalogue.values() if d.est_disponible()]

    def documents_empruntes(self) -> List[DocumentBase]:
        """Retourne la liste des documents actuellement empruntés."""
        return [
            d for d in self._catalogue.values()
            if d.statut == StatutDocument.EMPRUNTE
        ]

    def tous_les_emprunts_en_cours(self) -> List[Emprunt]:
        """Retourne tous les emprunts actifs, tous adhérents confondus."""
        emprunts = []
        for adherent in self._adherents.values():
            emprunts.extend(adherent.emprunts_en_cours)
        return emprunts

    def emprunts_en_retard(
        self, date_reference: Optional[date] = None
    ) -> List[tuple[Adherent, Emprunt]]:
        """
        Retourne les couples (adhérent, emprunt) pour tous les emprunts en retard.

        Args:
            date_reference: Date de référence (aujourd'hui par défaut).

        Returns:
            Liste de tuples (Adherent, Emprunt).
        """
        ref = date_reference or date.today()
        retards = []
        for adherent in self._adherents.values():
            for emprunt in adherent.emprunts_en_cours:
                if emprunt.jours_retard(ref) > 0:
                    retards.append((adherent, emprunt))
        return retards

    def statistiques(self) -> dict:
        """Retourne un résumé statistique de la bibliothèque."""
        return {
            "total_documents": len(self._catalogue),
            "documents_disponibles": len(self.documents_disponibles()),
            "documents_empruntes": len(self.documents_empruntes()),
            "total_adherents": len(self._adherents),
            "emprunts_en_cours": len(self.tous_les_emprunts_en_cours()),
            "emprunts_en_retard": len(self.emprunts_en_retard()),
        }

    def __str__(self) -> str:
        stats = self.statistiques()
        return (
            f"Bibliothèque '{self._nom}' — "
            f"{stats['total_documents']} doc(s), "
            f"{stats['total_adherents']} adhérent(s), "
            f"{stats['emprunts_en_cours']} emprunt(s) en cours"
        )
