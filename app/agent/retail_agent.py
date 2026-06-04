"""Retail Agent orchestration with LangChain."""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService
from app.tools import retail_tools

load_dotenv()


class RetailAgent:
    """Coordinate catalog, cart, and LangChain tools for agent workflows."""

    def __init__(self, catalog_service=None, cart_service=None, agent=None):
        self.catalog_service = catalog_service or CatalogService()
        self.cart_service = cart_service or CartService()
        self.tools = retail_tools

        self.agent = agent or self._create_agent()

    def _create_agent(self):
        return create_agent(
            model=ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
            ),
            tools=self.tools,
            system_prompt=(
                "You are a retail shopping assistant. "
                "Use the available tools to search products, check inventory, "
                "manage the cart, and calculate totals. "
                "Only discuss products that exist in the catalogue. "
                "Do not invent product IDs, prices, inventory, or cart contents."
            ),
        )

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

        result = self.agent.invoke(
            {
                "messages": messages,
            }
        )

        return result["messages"][-1].content
