"""
Module de génération de rapports textuels pour la bibliothèque.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import List

from models.adherent import Adherent
from models.emprunt import Emprunt
from services.bibliotheque import Bibliotheque

logger = logging.getLogger(__name__)


def rapport_emprunts_en_cours(bibliotheque: Bibliotheque) -> str:
    """
    Génère un rapport textuel de tous les emprunts en cours.

    Args:
        bibliotheque: Instance de la bibliothèque.

    Returns:
        Rapport formaté sous forme de chaîne de caractères.
    """
    emprunts = bibliotheque.tous_les_emprunts_en_cours()
    lignes = [
        "=" * 60,
        f"RAPPORT — EMPRUNTS EN COURS",
        f"Bibliothèque : {bibliotheque.nom}",
        f"Date : {date.today().strftime('%d/%m/%Y')}",
        "=" * 60,
    ]

    if not emprunts:
        lignes.append("Aucun emprunt en cours.")
    else:
        lignes.append(f"Nombre total d'emprunts actifs : {len(emprunts)}\n")
        for emp in emprunts:
            lignes.append(f"  • {emp.titre_document} (réf. {emp.reference_document})")
            lignes.append(f"    Emprunté le : {emp.date_emprunt.strftime('%d/%m/%Y')}")
            lignes.append(f"    Retour prévu : {emp.date_retour_prevue.strftime('%d/%m/%Y')}")
            lignes.append("")

    lignes.append("=" * 60)
    rapport = "\n".join(lignes)
    logger.info("Rapport emprunts en cours généré (%d emprunt(s)).", len(emprunts))
    return rapport


def rapport_retards(
    bibliotheque: Bibliotheque,
    date_reference: date | None = None,
) -> str:
    """
    Génère un rapport des emprunts en retard avec calcul des amendes.

    Args:
        bibliotheque: Instance de la bibliothèque.
        date_reference: Date de référence pour le calcul du retard.

    Returns:
        Rapport formaté.
    """
    ref = date_reference or date.today()
    retards = bibliotheque.emprunts_en_retard(ref)

    lignes = [
        "=" * 60,
        "RAPPORT — EMPRUNTS EN RETARD",
        f"Bibliothèque : {bibliotheque.nom}",
        f"Date de référence : {ref.strftime('%d/%m/%Y')}",
        "=" * 60,
    ]

    if not retards:
        lignes.append("Aucun emprunt en retard.")
    else:
        lignes.append(f"Nombre de retards : {len(retards)}\n")
        total_amendes = 0.0
        for adherent, emprunt in retards:
            jours = emprunt.jours_retard(ref)
            doc = bibliotheque.get_document(emprunt.reference_document)
            amende = doc.calculer_amende(jours)
            total_amendes += amende
            lignes.append(
                f"  • {adherent.nom_complet} ({adherent.categorie.value})"
            )
            lignes.append(
                f"    Document : {emprunt.titre_document} (réf. {emprunt.reference_document})"
            )
            lignes.append(
                f"    Retour prévu : {emprunt.date_retour_prevue.strftime('%d/%m/%Y')} "
                f"— Retard : {jours} jour(s)"
            )
            lignes.append(f"    Amende estimée : {amende:,.0f} FCFA")
            lignes.append("")
        lignes.append(f"Total amendes estimées : {total_amendes:,.0f} FCFA")

    lignes.append("=" * 60)
    rapport = "\n".join(lignes)
    logger.info("Rapport retards généré (%d retard(s)).", len(retards))
    return rapport


def rapport_catalogue(bibliotheque: Bibliotheque) -> str:
    """
    Génère un rapport complet du catalogue par type de document.

    Args:
        bibliotheque: Instance de la bibliothèque.

    Returns:
        Rapport formaté.
    """
    from collections import defaultdict
    par_type: dict = defaultdict(list)
    for doc in bibliotheque.catalogue.values():
        par_type[doc.type_document.value].append(doc)

    lignes = [
        "=" * 60,
        "RAPPORT — CATALOGUE",
        f"Bibliothèque : {bibliotheque.nom}",
        f"Date : {date.today().strftime('%d/%m/%Y')}",
        "=" * 60,
        f"Total : {len(bibliotheque.catalogue)} document(s)\n",
    ]

    for type_doc, docs in sorted(par_type.items()):
        lignes.append(f"--- {type_doc}s ({len(docs)}) ---")
        for doc in docs:
            lignes.append(
                f"  [{doc.statut.value:12}] {doc.titre} (réf. {doc.reference})"
            )
        lignes.append("")

    lignes.append("=" * 60)
    return "\n".join(lignes)


def rapport_adherent(bibliotheque: Bibliotheque, identifiant: str) -> str:
    """
    Génère le rapport détaillé d'un adhérent.

    Args:
        bibliotheque: Instance de la bibliothèque.
        identifiant: Identifiant de l'adhérent.

    Returns:
        Rapport formaté.
    """
    adherent = bibliotheque.get_adherent(identifiant)
    lignes = [
        "=" * 60,
        f"RAPPORT — ADHÉRENT",
        f"Nom : {adherent.nom_complet}",
        f"Catégorie : {adherent.categorie.value}",
        f"Email : {adherent.email}",
        f"Quota : {len(adherent.emprunts_en_cours)}/{adherent.quota_max}",
        "=" * 60,
        f"Historique ({len(adherent.historique_emprunts)} emprunt(s)) :\n",
    ]

    for emp in adherent.historique_emprunts:
        statut = "EN COURS" if emp.est_en_cours else "CLÔTURÉ"
        lignes.append(f"  [{statut}] {emp.titre_document}")
        lignes.append(f"    Emprunté : {emp.date_emprunt.strftime('%d/%m/%Y')} — "
                      f"Retour prévu : {emp.date_retour_prevue.strftime('%d/%m/%Y')}")
        if not emp.est_en_cours:
            lignes.append(
                f"    Retourné : {emp.date_retour_effective.strftime('%d/%m/%Y')} — "
                f"Amende : {emp.amende_payee:,.0f} FCFA"
            )
        lignes.append("")

    lignes.append("=" * 60)
    return "\n".join(lignes)
