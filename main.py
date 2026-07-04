"""
Point d'entrée principal — démonstration complète du système de bibliothèque.

Scénarios couverts :
    1. Création du catalogue (8 documents, 4 types)
    2. Enregistrement des adhérents (3 catégories)
    3. Emprunts et retours (avec et sans retard)
    4. Démonstration des exceptions métier
    5. Rapport des emprunts en cours et des retards
    6. Persistance JSON (export + reimport)
    7. Export CSV des retards
    8. Persistance SQLite + 4 requêtes métier
    9. Bonus : système de réservation
"""

import logging
import sys
from datetime import date, timedelta
from pathlib import Path

# ── Configuration du logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bibliotheque.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")

# ── Imports du projet ─────────────────────────────────────────────────────────
from models.livre import Livre
from models.revue import Revue
from models.dvd import DVD
from models.memoire import Memoire
from models.adherent import Adherent
from models.enums import CategorieAdherent
from services.bibliotheque import Bibliotheque
from services import rapport
from persistence import json_handler, csv_handler, db_handler
from exceptions.custom_exceptions import (
    DocumentNonDisponibleError,
    QuotaEmpruntDepasseError,
    DocumentIntrouvableError,
    ValeurInvalideError,
)

# ── Chemins de persistance ────────────────────────────────────────────────────
DATA_DIR = Path("data")
DB_PATH = str(DATA_DIR / "bibliotheque.db")
JSON_CATALOGUE = str(DATA_DIR / "catalogue.json")
JSON_ADHERENTS = str(DATA_DIR / "adherents.json")
CSV_RETARDS = str(DATA_DIR / "retards.csv")
CSV_EMPRUNTS = str(DATA_DIR / "emprunts_en_cours.csv")


def separateur(titre: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {titre}")
    print('═' * 60)


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 1 — Construction du catalogue
# ─────────────────────────────────────────────────────────────────────────────
def creer_catalogue() -> Bibliotheque:
    """Crée la bibliothèque et peuple le catalogue avec 8 documents variés."""
    separateur("SCÉNARIO 1 — Création du catalogue")

    biblio = Bibliotheque("Bibliothèque Universitaire ISI Dakar")

    # --- Livres (3) ---
    l1 = Livre(
        titre="Python Fluent",
        reference="LIV-001",
        annee_publication=2022,
        auteur="Luciano Ramalho",
        isbn="978-1492056355",
        genre="Informatique",
        nombre_pages=792,
    )
    l2 = Livre(
        titre="Clean Code",
        reference="LIV-002",
        annee_publication=2008,
        auteur="Robert C. Martin",
        isbn="978-0132350884",
        genre="Génie logiciel",
        nombre_pages=431,
    )
    l3 = Livre(
        titre="Réseaux informatiques",
        reference="LIV-003",
        annee_publication=2020,
        auteur="Andrew Tanenbaum",
        isbn="978-2744074806",
        genre="Réseaux",
        nombre_pages=944,
    )

    # --- Revues (2) ---
    r1 = Revue(
        titre="IEEE Communications",
        reference="REV-001",
        annee_publication=2024,
        editeur="IEEE",
        numero="Vol. 62 N°3",
        periodicite="mensuelle",
        domaine="Télécommunications",
    )
    r2 = Revue(
        titre="Journal of Network Security",
        reference="REV-002",
        annee_publication=2024,
        editeur="Hindawi",
        numero="Vol. 15",
        periodicite="trimestrielle",
        domaine="Cybersécurité",
    )

    # --- DVDs (2) ---
    d1 = DVD(
        titre="Introduction aux algorithmes — MIT OpenCourseWare",
        reference="DVD-001",
        annee_publication=2011,
        realisateur="MIT",
        duree_minutes=720,
        categorie="cours",
        langue="anglais",
    )
    d2 = DVD(
        titre="Le monde des réseaux",
        reference="DVD-002",
        annee_publication=2019,
        realisateur="France Télévisions",
        duree_minutes=52,
        categorie="documentaire",
    )

    # --- Mémoires (2) ---
    m1 = Memoire(
        titre="Optimisation des protocoles de routage dans les réseaux SDN",
        reference="MEM-001",
        annee_publication=2023,
        auteur="Mamadou Diallo",
        domaine="Réseaux Informatiques",
        niveau="Master",
        directeur="Pr. Sow",
    )
    m2 = Memoire(
        titre="Sécurisation des communications IoT par chiffrement léger",
        reference="MEM-002",
        annee_publication=2024,
        auteur="Fatou Ndiaye",
        domaine="Cybersécurité",
        niveau="Licence",
        directeur="Dr. Kane",
    )

    # AGRÉGATION : documents créés en dehors de la bibliothèque
    for doc in [l1, l2, l3, r1, r2, d1, d2, m1, m2]:
        biblio.ajouter_document(doc)

    print(f"\n✓ {len(biblio.catalogue)} documents ajoutés au catalogue.")
    print(rapport.rapport_catalogue(biblio))
    return biblio


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 2 — Enregistrement des adhérents
# ─────────────────────────────────────────────────────────────────────────────
def creer_adherents(biblio: Bibliotheque) -> None:
    """Crée et enregistre 3 adhérents de catégories différentes."""
    separateur("SCÉNARIO 2 — Enregistrement des adhérents")

    # AGRÉGATION : adhérents créés en dehors de la bibliothèque
    a1 = Adherent("ETU-2024-001", "Sarr", "Ibrahima", "ibrahima.sarr@isi.sn", CategorieAdherent.ETUDIANT)
    a2 = Adherent("ENS-001", "Diop", "Aminata", "aminata.diop@isi.sn", CategorieAdherent.ENSEIGNANT)
    a3 = Adherent("EXT-001", "Ndiaye", "Omar", "omar.ndiaye@gmail.com", CategorieAdherent.EXTERNE)

    for adherent in [a1, a2, a3]:
        biblio.ajouter_adherent(adherent)
        print(f"  ✓ Adhérent enregistré : {adherent}")


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 3 — Emprunts et retours (cycle complet)
# ─────────────────────────────────────────────────────────────────────────────
def scenario_emprunts(biblio: Bibliotheque) -> None:
    """Démontre le cycle complet d'emprunt : emprunt, retour, amende."""
    separateur("SCÉNARIO 3 — Cycle complet d'emprunt")

    today = date.today()

    # Emprunt 1 : étudiant emprunte un livre — retour à temps
    e1 = biblio.emprunter_document("ETU-2024-001", "LIV-001", today)
    print(f"\n  ✓ Emprunt créé : {e1.id_emprunt} — retour prévu {e1.date_retour_prevue}")

    # Emprunt 2 : enseignant emprunte une revue — retour à temps
    e2 = biblio.emprunter_document("ENS-001", "REV-001", today)
    print(f"  ✓ Emprunt créé : {e2.id_emprunt} — retour prévu {e2.date_retour_prevue}")

    # Emprunt 3 : étudiant emprunte un DVD
    e3 = biblio.emprunter_document("ETU-2024-001", "DVD-001", today)
    print(f"  ✓ Emprunt créé : {e3.id_emprunt} — retour prévu {e3.date_retour_prevue}")

    # Emprunt 4 : externe emprunte un mémoire
    e4 = biblio.emprunter_document("EXT-001", "MEM-001", today)
    print(f"  ✓ Emprunt créé : {e4.id_emprunt} — retour prévu {e4.date_retour_prevue}")

    # Emprunt 5 : étudiant emprunte un second livre — pour simuler retard
    e5 = biblio.emprunter_document("ETU-2024-001", "LIV-002",
                                   today - timedelta(days=30))
    print(f"  ✓ Emprunt (retardé) : {e5.id_emprunt} — prévu {e5.date_retour_prevue}")

    # Emprunt 6 : enseignant emprunte un deuxième document
    e6 = biblio.emprunter_document("ENS-001", "LIV-003",
                                   today - timedelta(days=10))
    print(f"  ✓ Emprunt (retardé) : {e6.id_emprunt} — prévu {e6.date_retour_prevue}")

    # Retour sans retard
    amende = biblio.retourner_document("ENS-001", "REV-001")
    print(f"\n  ✓ Retour REV-001 sans retard — amende : {amende:.0f} FCFA")

    # Retour avec retard (LIV-002 emprunté il y a 30 jours, durée max 21 j)
    amende_retard = biblio.retourner_document("ETU-2024-001", "LIV-002")
    print(f"  ⚠ Retour LIV-002 avec retard — amende : {amende_retard:.0f} FCFA")

    # Affichage du rapport
    print("\n" + rapport.rapport_emprunts_en_cours(biblio))
    print(rapport.rapport_retards(biblio))


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 4 — Démonstration des exceptions
# ─────────────────────────────────────────────────────────────────────────────
def scenario_exceptions(biblio: Bibliotheque) -> None:
    """Teste les exceptions personnalisées."""
    separateur("SCÉNARIO 4 — Exceptions métier")

    # Tenter d'emprunter un document déjà emprunté
    print("\n  [TEST] Emprunt d'un document déjà emprunté :")
    try:
        biblio.emprunter_document("ENS-001", "LIV-001")
    except DocumentNonDisponibleError as e:
        print(f"  ✓ Exception capturée → {e}")

    # Tenter de dépasser le quota (étudiant = max 3, déjà 2 actifs)
    print("\n  [TEST] Dépassement du quota d'emprunt :")
    try:
        # L'étudiant a déjà LIV-001 et DVD-001 actifs (2/3)
        biblio.emprunter_document("ETU-2024-001", "MEM-002")
        biblio.emprunter_document("ETU-2024-001", "REV-002")  # quota atteint ici
        biblio.emprunter_document("ETU-2024-001", "DVD-002")  # doit échouer
    except QuotaEmpruntDepasseError as e:
        print(f"  ✓ Exception capturée → {e}")

    # Tenter d'accéder à un document inexistant
    print("\n  [TEST] Document inexistant :")
    try:
        biblio.get_document("XXX-999")
    except DocumentIntrouvableError as e:
        print(f"  ✓ Exception capturée → {e}")

    # Tenter de créer un document avec des données invalides
    print("\n  [TEST] Données invalides (titre vide) :")
    try:
        Livre("", "LIV-ERR", 2020, "Auteur", "123", "Genre", 100)
    except ValeurInvalideError as e:
        print(f"  ✓ Exception capturée → {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 5 — Persistance JSON
# ─────────────────────────────────────────────────────────────────────────────
def scenario_json(biblio: Bibliotheque) -> None:
    """Exporte et reimporte le catalogue depuis JSON."""
    separateur("SCÉNARIO 5 — Persistance JSON")

    # Export
    docs = list(biblio.catalogue.values())
    json_handler.exporter_catalogue(docs, JSON_CATALOGUE)
    print(f"\n  ✓ Catalogue exporté → {JSON_CATALOGUE}")

    json_handler.exporter_adherents(list(biblio.adherents.values()), JSON_ADHERENTS)
    print(f"  ✓ Adhérents exportés → {JSON_ADHERENTS}")

    # Reimport (vérification)
    docs_reimportes = json_handler.importer_catalogue(JSON_CATALOGUE)
    print(f"  ✓ Catalogue reimporté : {len(docs_reimportes)} document(s)")

    adherents_reimportes = json_handler.importer_adherents(JSON_ADHERENTS)
    print(f"  ✓ Adhérents reimportés : {len(adherents_reimportes)} adhérent(s)")


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 6 — Export CSV
# ─────────────────────────────────────────────────────────────────────────────
def scenario_csv(biblio: Bibliotheque) -> None:
    """Exporte les retards et les emprunts en cours en CSV."""
    separateur("SCÉNARIO 6 — Export CSV")

    n_retards = csv_handler.exporter_emprunts_en_retard(biblio, CSV_RETARDS)
    print(f"\n  ✓ {n_retards} retard(s) exporté(s) → {CSV_RETARDS}")

    n_actifs = csv_handler.exporter_tous_emprunts(biblio, CSV_EMPRUNTS)
    print(f"  ✓ {n_actifs} emprunt(s) actif(s) exporté(s) → {CSV_EMPRUNTS}")


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 7 — Persistance SQLite + requêtes métier
# ─────────────────────────────────────────────────────────────────────────────
def scenario_sqlite(biblio: Bibliotheque) -> None:
    """Synchronise en base SQLite et exécute les 4 requêtes métier."""
    separateur("SCÉNARIO 7 — Base de données SQLite")

    db_handler.initialiser_base(DB_PATH)
    db_handler.synchroniser_catalogue(biblio, DB_PATH)
    db_handler.synchroniser_emprunts(biblio, DB_PATH)
    print(f"\n  ✓ Base synchronisée → {DB_PATH}")

    # Requête 1 : retards actifs
    print("\n  [SQL] Retards actifs :")
    retards = db_handler.requete_retards_actifs(DB_PATH)
    for r in retards:
        print(f"    • {r['adherent_nom']} — {r['titre_document']} "
              f"({r['jours_retard']} jour(s) de retard)")

    # Requête 2 : top documents
    print("\n  [SQL] Top 5 documents empruntés :")
    tops = db_handler.requete_top_documents(DB_PATH, limite=5)
    for i, t in enumerate(tops, 1):
        print(f"    {i}. {t['titre_document']} — {t['nb_emprunts']} emprunt(s)")

    # Requête 3 : historique étudiant
    print("\n  [SQL] Historique adhérent ETU-2024-001 :")
    historique = db_handler.requete_historique_adherent(DB_PATH, "ETU-2024-001")
    for h in historique:
        print(f"    [{h['statut']}] {h['titre_document']} — prévu {h['date_retour_prevue']}")

    # Requête 4 : amendes dues
    print("\n  [SQL] Amendes dues par adhérent :")
    amendes = db_handler.requete_amendes_dues(DB_PATH)
    for a in amendes:
        print(f"    • {a['adherent_nom']} — {a['nb_retards']} retard(s), "
              f"{a['total_jours_retard']} jour(s) au total")


# ─────────────────────────────────────────────────────────────────────────────
# SCÉNARIO 8 — Bonus : réservation
# ─────────────────────────────────────────────────────────────────────────────
def scenario_reservation(biblio: Bibliotheque) -> None:
    """Démontre le système de réservation (bonus)."""
    separateur("SCÉNARIO 8 (BONUS) — Réservation")

    # DVD-001 est emprunté → l'enseignant peut le réserver
    try:
        biblio.reserver_document("ENS-001", "DVD-001")
        print("\n  ✓ DVD-001 réservé par ENS-001")
        doc = biblio.get_document("DVD-001")
        print(f"  Statut : {doc.statut.value}")
    except ValeurInvalideError as e:
        print(f"  Info : {e}")

    # Tenter de réserver un document déjà disponible
    try:
        biblio.reserver_document("ETU-2024-001", "REV-001")
    except ValeurInvalideError as e:
        print(f"  ✓ Exception correctement levée → {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Exécute tous les scénarios de démonstration."""
    logger.info("=== Démarrage de la démonstration ===")

    biblio = creer_catalogue()
    creer_adherents(biblio)
    scenario_emprunts(biblio)
    scenario_exceptions(biblio)
    scenario_json(biblio)
    scenario_csv(biblio)
    scenario_sqlite(biblio)
    scenario_reservation(biblio)

    separateur("RÉSUMÉ FINAL")
    stats = biblio.statistiques()
    for cle, val in stats.items():
        print(f"  {cle:30} : {val}")

    # Rapport complet d'un adhérent
    print("\n" + rapport.rapport_adherent(biblio, "ETU-2024-001"))

    logger.info("=== Démonstration terminée ===")
    print("\n✓ Tous les scénarios ont été exécutés avec succès.")
    print(f"✓ Logs enregistrés dans bibliotheque.log")
    print(f"✓ Données persistées dans {DATA_DIR}/")


if __name__ == "__main__":
    main()
