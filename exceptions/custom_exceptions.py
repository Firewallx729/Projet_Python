"""
Exceptions métier personnalisées pour la bibliothèque universitaire.
"""


class BibliothèqueError(Exception):
    """Classe de base pour toutes les exceptions métier du projet."""


class DocumentNonDisponibleError(BibliothèqueError):
    """
    Levée lorsqu'un adhérent tente d'emprunter un document
    qui n'est pas au statut DISPONIBLE.
    """

    def __init__(self, titre: str, statut: str) -> None:
        self.titre = titre
        self.statut = statut
        super().__init__(
            f"Le document '{titre}' n'est pas disponible (statut actuel : {statut})."
        )


class QuotaEmpruntDepasseError(BibliothèqueError):
    """
    Levée lorsqu'un adhérent a atteint le nombre maximum
    d'emprunts simultanés autorisés pour sa catégorie.
    """

    def __init__(self, nom: str, quota: int) -> None:
        self.nom = nom
        self.quota = quota
        super().__init__(
            f"L'adhérent '{nom}' a atteint son quota maximum de {quota} emprunt(s) simultané(s)."
        )


class DocumentIntrouvableError(BibliothèqueError):
    """Levée lorsqu'un document est introuvable par sa référence."""

    def __init__(self, reference: str) -> None:
        self.reference = reference
        super().__init__(f"Aucun document trouvé avec la référence '{reference}'.")


class AdherentIntrouvableError(BibliothèqueError):
    """Levée lorsqu'un adhérent est introuvable par son identifiant."""

    def __init__(self, identifiant: str) -> None:
        self.identifiant = identifiant
        super().__init__(f"Aucun adhérent trouvé avec l'identifiant '{identifiant}'.")


class EmpruntIntrouvableError(BibliothèqueError):
    """Levée lorsqu'aucun emprunt actif n'est trouvé pour un document donné."""

    def __init__(self, reference_doc: str) -> None:
        self.reference_doc = reference_doc
        super().__init__(
            f"Aucun emprunt actif trouvé pour le document '{reference_doc}'."
        )


class ValeurInvalideError(BibliothèqueError):
    """Levée lors d'une validation d'entrée utilisateur échouée."""

    def __init__(self, champ: str, raison: str) -> None:
        self.champ = champ
        self.raison = raison
        super().__init__(f"Valeur invalide pour '{champ}' : {raison}.")
