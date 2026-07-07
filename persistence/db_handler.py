"""
Gestion de la persistance SQLite pour la bibliothèque universitaire.

Tables :
    documents  — catalogue des documents
    emprunts   — emprunts avec clé étrangère vers documents

Requêtes métier implémentées :
    1. retards_actifs()      — emprunts en retard non clôturés
    2. top_documents()       — documents les plus empruntés
    3. historique_adherent() — historique complet d'un adhérent
    4. amendes_dues()        — total des amendes par adhérent
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import date
from pathlib import Path
from typing import List, Optional

from services.bibliotheque import Bibliotheque

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    reference          TEXT PRIMARY KEY,
    type_document      TEXT NOT NULL,
    titre              TEXT NOT NULL,
    annee_publication  INTEGER NOT NULL,
    statut             TEXT NOT NULL,
    details            TEXT
);

CREATE TABLE IF NOT EXISTS emprunts (
    id_emprunt              TEXT PRIMARY KEY,
    reference_document      TEXT NOT NULL,
    titre_document          TEXT NOT NULL,
    adherent_id             TEXT NOT NULL,
    adherent_nom            TEXT NOT NULL,
    adherent_categorie      TEXT NOT NULL,
    date_emprunt            TEXT NOT NULL,
    date_retour_prevue      TEXT NOT NULL,
    date_retour_effective   TEXT,
    amende_payee            REAL DEFAULT 0.0,
    FOREIGN KEY (reference_document) REFERENCES documents(reference)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_emprunts_reference
    ON emprunts(reference_document);

CREATE INDEX IF NOT EXISTS idx_emprunts_adherent
    ON emprunts(adherent_id);
"""


def initialiser_base(chemin: str) -> None:
    """
    Crée ou vérifie le schéma de la base de données SQLite.

    Args:
        chemin: Chemin du fichier .db SQLite.
    """
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(chemin) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    logger.info("Base de données initialisée : %s", chemin)


def synchroniser_catalogue(bibliotheque: Bibliotheque, chemin: str) -> None:
    """
    Insère ou met à jour tous les documents du catalogue en base.

    Args:
        bibliotheque: Instance de la bibliothèque.
        chemin: Chemin du fichier SQLite.
    """
    with sqlite3.connect(chemin) as conn:
        for doc in bibliotheque.catalogue.values():
            conn.execute(
                """
                INSERT INTO documents (reference, type_document, titre, annee_publication, statut)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(reference) DO UPDATE SET
                    statut = excluded.statut,
                    titre  = excluded.titre
                """,
                (
                    doc.reference,
                    doc.type_document.value,
                    doc.titre,
                    doc.annee_publication,
                    doc.statut.value,
                ),
            )
        conn.commit()
    logger.info("Catalogue synchronisé en base (%d doc(s)).", len(bibliotheque.catalogue))


def synchroniser_emprunts(bibliotheque: Bibliotheque, chemin: str) -> None:
    """
    Insère ou met à jour tous les emprunts de tous les adhérents en base.

    Args:
        bibliotheque: Instance de la bibliothèque.
        chemin: Chemin du fichier SQLite.
    """
    with sqlite3.connect(chemin) as conn:
        for adherent in bibliotheque.adherents.values():
            for emprunt in adherent.historique_emprunts:
                conn.execute(
                    """
                    INSERT INTO emprunts (
                        id_emprunt, reference_document, titre_document,
                        adherent_id, adherent_nom, adherent_categorie,
                        date_emprunt, date_retour_prevue,
                        date_retour_effective, amende_payee
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id_emprunt) DO UPDATE SET
                        date_retour_effective = excluded.date_retour_effective,
                        amende_payee          = excluded.amende_payee
                    """,
                    (
                        emprunt.id_emprunt,
                        emprunt.reference_document,
                        emprunt.titre_document,
                        adherent.identifiant,
                        adherent.nom_complet,
                        adherent.categorie.value,
                        emprunt.date_emprunt.isoformat(),
                        emprunt.date_retour_prevue.isoformat(),
                        emprunt.date_retour_effective.isoformat()
                        if emprunt.date_retour_effective
                        else None,
                        emprunt.amende_payee,
                    ),
                )
        conn.commit()
    logger.info("Emprunts synchronisés en base.")


# ── Requêtes métier ───────────────────────────────────────────────────────────

def requete_retards_actifs(chemin: str, date_reference: Optional[str] = None) -> List[dict]:
    """
    Requête 1 — Retourne tous les emprunts actifs en retard.

    Args:
        chemin: Chemin SQLite.
        date_reference: Date ISO (YYYY-MM-DD) de référence. Aujourd'hui par défaut.

    Returns:
        Liste de dictionnaires avec les détails du retard.
    """
    ref = date_reference or date.today().isoformat()
    with sqlite3.connect(chemin) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT
                e.id_emprunt,
                e.adherent_nom,
                e.adherent_categorie,
                e.titre_document,
                e.reference_document,
                e.date_retour_prevue,
                CAST(julianday(?) - julianday(e.date_retour_prevue) AS INTEGER) AS jours_retard
            FROM emprunts e
            WHERE e.date_retour_effective IS NULL
              AND e.date_retour_prevue < ?
            ORDER BY jours_retard DESC
            """,
            (ref, ref),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    logger.info("Requête retards actifs : %d résultat(s).", len(rows))
    return rows


def requete_top_documents(chemin: str, limite: int = 5) -> List[dict]:
    """
    Requête 2 — Top documents les plus empruntés.

    Args:
        chemin: Chemin SQLite.
        limite: Nombre de documents à retourner.

    Returns:
        Liste triée par nombre d'emprunts décroissant.
    """
    with sqlite3.connect(chemin) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT
                e.reference_document,
                e.titre_document,
                d.type_document,
                COUNT(e.id_emprunt)   AS nb_emprunts,
                SUM(e.amende_payee)   AS total_amendes_collectees
            FROM emprunts e
            JOIN documents d ON d.reference = e.reference_document
            GROUP BY e.reference_document
            ORDER BY nb_emprunts DESC
            LIMIT ?
            """,
            (limite,),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    logger.info("Requête top documents : %d résultat(s).", len(rows))
    return rows


def requete_historique_adherent(chemin: str, adherent_id: str) -> List[dict]:
    """
    Requête 3 — Historique complet des emprunts d'un adhérent.

    Args:
        chemin: Chemin SQLite.
        adherent_id: Identifiant de l'adhérent.

    Returns:
        Liste des emprunts triés par date décroissante.
    """
    with sqlite3.connect(chemin) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT
                e.id_emprunt,
                e.titre_document,
                e.reference_document,
                e.date_emprunt,
                e.date_retour_prevue,
                e.date_retour_effective,
                e.amende_payee,
                CASE WHEN e.date_retour_effective IS NULL THEN 'EN COURS' ELSE 'CLÔTURÉ' END AS statut
            FROM emprunts e
            WHERE e.adherent_id = ?
            ORDER BY e.date_emprunt DESC
            """,
            (adherent_id,),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    logger.info(
        "Requête historique adhérent '%s' : %d emprunt(s).", adherent_id, len(rows)
    )
    return rows


def requete_amendes_dues(chemin: str) -> List[dict]:
    """
    Requête 4 — Total des amendes dues par adhérent (emprunts en retard non clôturés).

    Args:
        chemin: Chemin SQLite.

    Returns:
        Liste des adhérents avec leur total d'amendes dues, triés par montant décroissant.
    """
    today = date.today().isoformat()
    with sqlite3.connect(chemin) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT
                e.adherent_id,
                e.adherent_nom,
                e.adherent_categorie,
                COUNT(e.id_emprunt) AS nb_retards,
                SUM(
                    CAST(julianday(?) - julianday(e.date_retour_prevue) AS INTEGER)
                ) AS total_jours_retard,
                SUM(e.amende_payee) AS amendes_deja_payees
            FROM emprunts e
            WHERE e.date_retour_effective IS NULL
              AND e.date_retour_prevue < ?
            GROUP BY e.adherent_id
            ORDER BY total_jours_retard DESC
            """,
            (today, today),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    logger.info("Requête amendes dues : %d adhérent(s) en retard.", len(rows))
    return rows
