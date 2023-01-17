from flask import Blueprint
from flask_restx import Api

# Namespaces
from server.controllers.login import login_ns
from server.controllers.clients import clients_ns, emp_clients_ns
from server.controllers.accounts import accounts_ns, emp_accounts_ns
from server.controllers.cards import cards_ns, my_cards_ns, emp_cards_ns
from server.controllers.purchases import purchases_ns


# Blueprint
api_bp = Blueprint("api", __name__, url_prefix="/v1")

# Register namespaces into API
api = Api(api_bp,
    version="0.2.1",
    title="Bank Management Server",
    description="Server for clients to interact with the Banking System.",
    doc="/docs"
)

api.add_namespace(login_ns)
api.add_namespace(clients_ns)
api.add_namespace(emp_clients_ns)
api.add_namespace(accounts_ns)
api.add_namespace(emp_accounts_ns)
api.add_namespace(cards_ns)
api.add_namespace(my_cards_ns)
api.add_namespace(emp_cards_ns)
api.add_namespace(purchases_ns)
