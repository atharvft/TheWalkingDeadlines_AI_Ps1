class AIProviderError(RuntimeError):
    """Safe, user-facing category for provider failures."""


class AIConfigurationError(AIProviderError):
    pass


class AIProviderUnavailable(AIProviderError):
    pass
