class UsageError(Exception):
    """
    Narq usage error
    """


class ConfigurationError(Exception):
    """
    Narq configuration error
    """


class SerializationError(Exception):
    """
    Serialization error
    """


class DeserializationError(Exception):
    """
    Deserialization error
    """


class TaskDisabledError(Exception):
    """
    Task disabled error
    """
