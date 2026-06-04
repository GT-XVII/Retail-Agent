"""Retail Agent orchestration with LangChain."""

from langchain.agents import create_agent

from app.config.agent_model import create_chat_model
from app.errors import AgentConfigurationError, AgentExecutionError, RetailAgentError
from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService
from app.tools import retail_tools


class RetailAgent:
    """Coordinate catalog, cart, and LangChain tools for agent workflows."""

    def __init__(self, catalog_service=None, cart_service=None, agent=None):
        self.catalog_service = catalog_service or CatalogService()
        self.cart_service = cart_service or CartService()
        self.tools = retail_tools

        self.agent = agent or self._create_agent()

    def _create_agent(self):
        try:
            return create_agent(
                model=create_chat_model(),
                tools=self.tools,
                system_prompt=(
                    "You are a retail shopping assistant. "
                    "Use the available tools to search products, check inventory, "
                    "manage the cart, and calculate totals. "
                    "Only discuss products that exist in the catalogue. "
                    "Do not invent product IDs, prices, inventory, or cart contents."
                ),
            )
        except RetailAgentError:
            raise
        except Exception as error:
            raise AgentConfigurationError(
                "Failed to initialize the LangChain retail agent.",
                details=self._error_details(error),
            ) from error

    def get_tools(self):
        """Return the LangChain tools available to the agent."""
        return self.tools

    def search_products(self, query, limit=None):
        return self.catalog_service.search(query, limit=limit)

    def get_product_details(self, product_id):
        return self.catalog_service.get_product(product_id)

    def check_inventory(self, product_id):
        return self.catalog_service.get_inventory(product_id)

    def run(self, message, history=None):
        """Run the LangChain agent with the user message."""
        messages = list(history or [])
        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        try:
            result = self.agent.invoke(
                {
                    "messages": messages,
                }
            )
            response_messages = result.get("messages", [])

            if not response_messages:
                raise AgentExecutionError(
                    "The LangChain agent returned no messages.",
                    details={"result_keys": list(result.keys())},
                )

            content = getattr(response_messages[-1], "content", None)

            if content is None:
                raise AgentExecutionError(
                    "The LangChain agent returned a message without content.",
                    details={"message_type": type(response_messages[-1]).__name__},
                )

            return content
        except RetailAgentError:
            raise
        except Exception as error:
            raise AgentExecutionError(
                "Failed to run the LangChain retail agent.",
                details=self._error_details(error),
            ) from error

    def _error_details(self, error):
        return {
            "type": type(error).__name__,
            "message": str(error),
        }
