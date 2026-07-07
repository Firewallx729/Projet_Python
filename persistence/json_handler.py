"""
Gestion de la persistance JSON pour le catalogue et les adhérents.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from models.document_base import DocumentBase
from models.livre import Livre
from models.revue import Revue
from models.dvd import DVD
from models.memoire import Memoire
from models.adherent import Adherent
from models.emprunt import Emprunt
from models.enums import CategorieAdherent, StatutDocument, TypeDocument
from exceptions.custom_exceptions import ValeurInvalideError

logger = logging.getLogger(__name__)


def exporter_catalogue(documents: List[DocumentBase], chemin: str) -> None:
    """
    Exporte la liste de documents dans un fichier JSON.

    Args:
        documents: Liste des documents à exporter.
        chemin: Chemin du fichier de sortie.

    Raises:
        OSError: Si l'écriture du fichier échoue.
    """
    donnees = [doc.to_dict() for doc in documents]
    chemin_path = Path(chemin)
    chemin_path.parent.mkdir(parents=True, exist_ok=True)

    with open(chemin_path, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    logger.info("Catalogue exporté : %d document(s) → %s", len(donnees), chemin)


def importer_catalogue(chemin: str) -> List[DocumentBase]:
    """
    Importe les documents depuis un fichier JSON.

    Args:
        chemin: Chemin du fichier JSON.

    Returns:
        Liste des documents reconstruits.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si le JSON est malformé.
    """
    chemin_path = Path(chemin)
    if not chemin_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    with open(chemin_path, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    documents = []
    for d in donnees:
        doc = _reconstruire_document(d)
        if doc:
            documents.append(doc)

    logger.info("Catalogue importé : %d document(s) ← %s", len(documents), chemin)
    return documents


def _reconstruire_document(data: dict) -> DocumentBase | None:
    """
    Reconstruit un objet document depuis un dictionnaire JSON.

    Args:
        data: Dictionnaire des données du document.

    Returns:
        Instance du bon type ou None si type inconnu.
    """
    type_val = data.get("type", "")

    try:
        if type_val == TypeDocument.LIVRE.value:
            doc = Livre(
                titre=data["titre"],
                reference=data["reference"],
                annee_publication=data["annee_publication"],
                auteur=data["auteur"],
                isbn=data["isbn"],
                genre=data["genre"],
                nombre_pages=data["nombre_pages"],
            )
        elif type_val == TypeDocument.REVUE.value:
            doc = Revue(
                titre=data["titre"],
                reference=data["reference"],
                annee_publication=data["annee_publication"],
                editeur=data["editeur"],
                numero=data["numero"],
                periodicite=data["periodicite"],
                domaine=data["domaine"],
            )
        elif type_val == TypeDocument.DVD.value:
            doc = DVD(
                titre=data["titre"],
                reference=data["reference"],
                annee_publication=data["annee_publication"],
                realisateur=data["realisateur"],
                duree_minutes=data["duree_minutes"],
                categorie=data["categorie"],
                langue=data.get("langue", "français"),
            )
        elif type_val == TypeDocument.MEMOIRE.value:
            doc = Memoire(
                titre=data["titre"],
                reference=data["reference"],
                annee_publication=data["annee_publication"],
                auteur=data["auteur"],
                domaine=data["domaine"],
                niveau=data["niveau"],
                directeur=data["directeur"],
            )
        else:
            logger.warning("Type de document inconnu lors de l'import : %s", type_val)
            return None

        # Restauration du statut
        statut_val = data.get("statut", StatutDocument.DISPONIBLE.value)
        for statut in StatutDocument:
            if statut.value == statut_val:
                doc._statut = statut
                break

        return doc

    except (KeyError, ValeurInvalideError) as e:
        logger.error("Erreur reconstruction document '%s' : %s", data.get("titre"), e)
        return None


def exporter_adherents(adherents: List[Adherent], chemin: str) -> None:
    """
    Exporte les adhérents et leur historique dans un fichier JSON.

    Args:
        adherents: Liste des adhérents.
        chemin: Chemin du fichier de sortie.
    """
    donnees = [a.to_dict() for a in adherents]
    chemin_path = Path(chemin)
    chemin_path.parent.mkdir(parents=True, exist_ok=True)

    with open(chemin_path, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    logger.info("Adhérents exportés : %d → %s", len(donnees), chemin)


def importer_adherents(chemin: str) -> List[Adherent]:
    """
    Importe les adhérents depuis un fichier JSON.

    Args:
        chemin: Chemin du fichier JSON.

    Returns:
        Liste des adhérents reconstruits avec leur historique.
    """
    from datetime import date

    chemin_path = Path(chemin)
    if not chemin_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    with open(chemin_path, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    adherents = []
    for d in donnees:
        try:
            cat = next(
                c for c in CategorieAdherent if c.value == d["categorie"]
            )
            adherent = Adherent(
                identifiant=d["identifiant"],
                nom=d["nom"],
                prenom=d["prenom"],
                email=d["email"],
                categorie=cat,
            )
            # Reconstruction de l'historique d'emprunts (COMPOSITION)
            for emp_data in d.get("historique_emprunts", []):
                from datetime import date as date_cls
                emp = Emprunt(
                    id_emprunt=emp_data["id_emprunt"],
                    reference_document=emp_data["reference_document"],
                    titre_document=emp_data["titre_document"],
                    date_emprunt=date_cls.fromisoformat(emp_data["date_emprunt"]),
                    duree_jours=(
                        date_cls.fromisoformat(emp_data["date_retour_prevue"])
                        - date_cls.fromisoformat(emp_data["date_emprunt"])
                    ).days,
                )
                if emp_data.get("date_retour_effective"):
                    emp.cloture(
                        date_cls.fromisoformat(emp_data["date_retour_effective"]),
                        emp_data.get("amende_payee", 0.0),
                    )
                adherent._historique_emprunts.append(emp)

            adherents.append(adherent)
        except (KeyError, StopIteration, ValeurInvalideError) as e:
            logger.error("Erreur reconstruction adhérent '%s' : %s", d.get("nom"), e)

    logger.info("Adhérents importés : %d ← %s", len(adherents), chemin)
    return adherents
