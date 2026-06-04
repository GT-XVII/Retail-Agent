"""Application error types and response helpers."""


class RetailAgentError(Exception):
    """Base error for expected application failures."""

    code = "retail_agent_error"
    status_code = 500

    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_response(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ModelConfigurationError(RetailAgentError):
    code = "model_configuration_error"
    status_code = 500


class AgentConfigurationError(RetailAgentError):
    code = "agent_configuration_error"
    status_code = 500


class AgentExecutionError(RetailAgentError):
    code = "agent_execution_error"
    status_code = 502


class ChatServiceError(RetailAgentError):
    code = "chat_service_error"
    status_code = 500
