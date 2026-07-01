"""
Énumérations utilisées dans le projet bibliothèque universitaire.
"""

from enum import Enum


class StatutDocument(Enum):
    """Statut courant d'un document dans la bibliothèque."""

    DISPONIBLE = "disponible"
    EMPRUNTE = "emprunté"
    RESERVE = "réservé"
    PERDU = "perdu"


class CategorieAdherent(Enum):
    """Catégorie d'un adhérent, détermine les quotas et durées d'emprunt."""

    ETUDIANT = "étudiant"
    ENSEIGNANT = "enseignant"
    EXTERNE = "externe"


class TypeDocument(Enum):
    """Type de document pour la persistance et les rapports."""

    LIVRE = "Livre"
    REVUE = "Revue"
    DVD = "DVD"
    MEMOIRE = "Mémoire"
