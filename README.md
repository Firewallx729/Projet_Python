# Projet_Python
# Contributions au projet

## Membres du groupe

- Abibou_Nokho — @Firewallx729
- Hyacinthe Guardebaye Mouladjim — @guerdebaye
- Moussa Diakhaté — @pseudo_github_3

## Répartition du travail

| Membre | Modules / classes développés | Contribution estimée |
|--------|-------------------------------|----------------------|
| Abibou_Nokho | `models/enums.py`, `models/document_base.py`, `models/livre.py`, `models/revue.py`, `models/dvd.py`, `models/memoire.py` | 33% |
| Hyacinthe_Guardebaye_Mouladjim | `models/emprunt.py`, `models/adherent.py`, `services/bibliotheque.py`, `services/rapport.py`, `main.py` | 34% |
| Moussa diakhaté| `exceptions/custom_exceptions.py`, `persistence/json_handler.py`, `persistence/csv_handler.py`, `persistence/db_handler.py`, `README.md` | 33% |

## Répartition par phase

| Phase | Responsable principal |
|-----------------------------------|------------------------|
| Conception (diagramme de classes) | Abibou Nokho |
| Implémentation POO | Abibou Nokho |
| Logique métier (emprunts/retours) | Hyacinthe Mouladjim |
| Interface principale (main.py) | Hyacinthe Mouladjim |
| Persistance fichiers (JSON/CSV) | Moussa diakhaté |
| Persistance SQL | Moussa diakhaté |
| Exceptions personnalisées | Moussa diakhaté |
| Tests / gestion des exceptions | Tous (chacun pour son module) |
| README / documentation | Moussa diakhaté |

## Difficultés rencontrées et résolution

1. **Distinction agrégation / composition** — La relation entre `Bibliotheque` et `Document` est une agrégation car les documents peuvent être créés et exister indépendamment. La relation entre `Adherent` et `Emprunt` est une composition car un emprunt n'a pas de sens sans l'adhérent qui l'a initié. Résolu par Abibou Nokho  & Hyacinthe Mouladjim lors de la phase de conception.

2. **Reconstruction des objets depuis JSON** — Lors de l'import JSON, il fallait restaurer le bon type de document (`Livre`, `Revue`, etc.) et le bon statut (`StatutDocument`) depuis des chaînes. Résolu par Étudiant Moussa diakhaté via la fonction `_reconstruire_document()` avec gestion des exceptions `KeyError`.
