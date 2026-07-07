# Bibliothèque Universitaire ISI Dakar

Projet de fin de semestre — **Sujet B** — Programmation Orientée Objet & Persistance des données  
Module Python — L2 Réseaux Informatiques — 2025-2026  
Formateur : M. HAMANE

---

## Description

Système de gestion d'une bibliothèque universitaire permettant de gérer :
- Un catalogue de documents (Livres, Revues, DVDs, Mémoires)
- Des adhérents de catégories différentes (Étudiant, Enseignant, Externe)
- Le cycle complet d'un emprunt : emprunt → retour → calcul d'amende
- La persistance des données (JSON, CSV, SQLite)

---

## Structure du projet

```
bibliotheque_universitaire/
├── models/
│   ├── enums.py            # StatutDocument, CategorieAdherent, TypeDocument
│   ├── document_base.py    # Classe abstraite DocumentBase (ABC)
│   ├── livre.py            # Sous-classe Livre (21j, 50 FCFA/j)
│   ├── revue.py            # Sous-classe Revue (7j, 25 FCFA/j)
│   ├── dvd.py              # Sous-classe DVD (3j, 100 FCFA/j)
│   ├── memoire.py          # Sous-classe Mémoire (14j, 75 FCFA/j)
│   ├── emprunt.py          # Classe Emprunt (composition avec Adherent)
│   └── adherent.py         # Classe Adherent
├── services/
│   ├── bibliotheque.py     # Classe Bibliotheque (agrégation)
│   └── rapport.py          # Génération de rapports textuels
├── persistence/
│   ├── json_handler.py     # Export/import JSON
│   ├── csv_handler.py      # Export CSV
│   └── db_handler.py       # SQLite : schéma + 4 requêtes métier
├── exceptions/
│   └── custom_exceptions.py  # Exceptions personnalisées
├── main.py                 # Point d'entrée — scénarios de démonstration
├── requirements.txt
├── README.md
└── CONTRIBUTIONS.md
```

---

## Installation

**Prérequis :** Python 3.10 ou supérieur (aucune dépendance externe requise).

```bash
git clone <url-du-repo>
cd bibliotheque_universitaire
python main.py
```

---

## Utilisation

```bash
# Lancer la démonstration complète
python main.py

# Les fichiers générés apparaissent dans data/
#   data/catalogue.json
#   data/adherents.json
#   data/retards.csv
#   data/emprunts_en_cours.csv
#   data/bibliotheque.db

# Les logs sont enregistrés dans bibliotheque.log
```

---

## Architecture POO

| Concept | Implémentation |
|---|---|
| Classe abstraite | `DocumentBase` (ABC) avec `emprunter()` et `calculer_amende()` abstraites |
| Héritage | `Livre`, `Revue`, `DVD`, `Memoire` héritent de `DocumentBase` |
| Enum | `StatutDocument`, `CategorieAdherent`, `TypeDocument` |
| Agrégation | `Bibliotheque` contient des `Document` et `Adherent` créés en dehors |
| Composition | `Adherent` crée et possède ses `Emprunt` (cycle de vie lié) |

---

## Persistance

| Type | Fichier | Contenu |
|---|---|---|
| JSON | `data/catalogue.json` | Catalogue complet exporté/importé |
| JSON | `data/adherents.json` | Adhérents + historique d'emprunts |
| CSV | `data/retards.csv` | Emprunts en retard avec amendes estimées |
| CSV | `data/emprunts_en_cours.csv` | Tous les emprunts actifs |
| SQLite | `data/bibliotheque.db` | Tables `documents` + `emprunts` (FK) |

### Requêtes SQL métier
1. `requete_retards_actifs()` — emprunts actifs dépassant la date prévue
2. `requete_top_documents()` — documents les plus empruntés
3. `requete_historique_adherent()` — historique complet d'un adhérent
4. `requete_amendes_dues()` — total des amendes dues par adhérent

---

## Exceptions personnalisées

| Exception | Déclencheur |
|---|---|
| `DocumentNonDisponibleError` | Emprunt d'un document non disponible |
| `QuotaEmpruntDepasseError` | Quota d'emprunts simultanés dépassé |
| `DocumentIntrouvableError` | Référence de document inexistante |
| `AdherentIntrouvableError` | Identifiant d'adhérent inexistant |
| `EmpruntIntrouvableError` | Aucun emprunt actif pour ce document |
| `ValeurInvalideError` | Validation d'entrée échouée |
