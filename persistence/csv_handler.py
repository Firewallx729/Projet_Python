"""
Export CSV des emprunts en retard et des statistiques.
"""

from __future__ import annotations

import csv
import logging
from datetime import date
from pathlib import Path
from typing import List, Tuple

from models.adherent import Adherent
from models.emprunt import Emprunt
from services.bibliotheque import Bibliotheque

logger = logging.getLogger(__name__)


def exporter_emprunts_en_retard(
    bibliotheque: Bibliotheque,
    chemin: str,
    date_reference: date | None = None,
) -> int:
    """
    Exporte les emprunts en retard dans un fichier CSV.

    Args:
        bibliotheque: Instance de la bibliothèque.
        chemin: Chemin du fichier CSV de sortie.
        date_reference: Date de référence pour le calcul du retard.

    Returns:
        Nombre de lignes exportées.

    Raises:
        OSError: Si l'écriture du fichier échoue.
    """
    ref = date_reference or date.today()
    retards: List[Tuple[Adherent, Emprunt]] = bibliotheque.emprunts_en_retard(ref)

    chemin_path = Path(chemin)
    chemin_path.parent.mkdir(parents=True, exist_ok=True)

    entetes = [
        "id_emprunt",
        "adherent_id",
        "adherent_nom",
        "adherent_categorie",
        "reference_document",
        "titre_document",
        "date_emprunt",
        "date_retour_prevue",
        "jours_retard",
        "amende_estimee_fcfa",
    ]

    with open(chemin_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=entetes)
        writer.writeheader()

        for adherent, emprunt in retards:
            jours = emprunt.jours_retard(ref)
            doc = bibliotheque.get_document(emprunt.reference_document)
            amende = doc.calculer_amende(jours)

            writer.writerow({
                "id_emprunt": emprunt.id_emprunt,
                "adherent_id": adherent.identifiant,
                "adherent_nom": adherent.nom_complet,
                "adherent_categorie": adherent.categorie.value,
                "reference_document": emprunt.reference_document,
                "titre_document": emprunt.titre_document,
                "date_emprunt": emprunt.date_emprunt.strftime("%d/%m/%Y"),
                "date_retour_prevue": emprunt.date_retour_prevue.strftime("%d/%m/%Y"),
                "jours_retard": jours,
                "amende_estimee_fcfa": f"{amende:.0f}",
            })

    logger.info(
        "Export CSV retards : %d ligne(s) → %s (référence : %s)",
        len(retards),
        chemin,
        ref,
    )
    return len(retards)


def exporter_tous_emprunts(
    bibliotheque: Bibliotheque,
    chemin: str,
) -> int:
    """
    Exporte tous les emprunts en cours dans un fichier CSV.

    Args:
        bibliotheque: Instance de la bibliothèque.
        chemin: Chemin du fichier CSV de sortie.

    Returns:
        Nombre de lignes exportées.
    """
    emprunts_actifs = bibliotheque.tous_les_emprunts_en_cours()
    chemin_path = Path(chemin)
    chemin_path.parent.mkdir(parents=True, exist_ok=True)

    entetes = [
        "id_emprunt",
        "reference_document",
        "titre_document",
        "date_emprunt",
        "date_retour_prevue",
        "jours_restants",
        "en_retard",
    ]

    today = date.today()

    with open(chemin_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=entetes)
        writer.writeheader()

        for emprunt in emprunts_actifs:
            jours_restants = (emprunt.date_retour_prevue - today).days
            writer.writerow({
                "id_emprunt": emprunt.id_emprunt,
                "reference_document": emprunt.reference_document,
                "titre_document": emprunt.titre_document,
                "date_emprunt": emprunt.date_emprunt.strftime("%d/%m/%Y"),
                "date_retour_prevue": emprunt.date_retour_prevue.strftime("%d/%m/%Y"),
                "jours_restants": max(0, jours_restants),
                "en_retard": "OUI" if jours_restants < 0 else "NON",
            })

    logger.info("Export CSV emprunts actifs : %d ligne(s) → %s", len(emprunts_actifs), chemin)
    return len(emprunts_actifs)
