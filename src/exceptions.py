# exceptions.py

class AICrewException(Exception):
    """Classe de base pour les exceptions personnalisées de ce projet."""
    pass

class ConfigurationError(AICrewException):
    """Levée lorsqu'une erreur de configuration est détectée."""
    pass

class MissingAPIKeyError(ConfigurationError):
    """Levée lorsqu'une clé API requise est manquante."""
    pass
