from intent_kit import TreeBuilder, keyword_classifier, execute_taxonomy
import re



# Example argument extractors


def extract_account_args(user_input: str) -> dict:
    """Extract account_id from user input."""
    # Simple regex extraction - in practice, this could use LLM
    match = re.search(r'account(\w+)', user_input)
    if match:
        return {"account_id": match.group(1)}
    # Fallback: try to extract from the end
    words = user_input.split()
    return {"account_id": words[-1] if words else "default"}


def extract_transaction_args(user_input: str) -> dict:
    """Extract account_id and date_range from user input."""
    # Extract account_id
    account_match = re.search(r'account(\w+)', user_input)
    account_id = account_match.group(1) if account_match else "default"

    # Extract date_range
    date_patterns = [
        r'last_(\w+)',  # last_month, last_week
        r'(\d+)_days',  # 30_days
        r'(\w+)_(\d{4})',  # jan_2024
    ]

    date_range = "last_month"  # default
    for pattern in date_patterns:
        match = re.search(pattern, user_input)
        if match:
            date_range = match.group(0)
            break

    return {"account_id": account_id, "date_range": date_range}


def extract_employee_args(user_input: str) -> dict:
    """Extract name and role from user input."""
    # Simple extraction - in practice, this could use LLM
    words = user_input.split()
    if len(words) >= 2:
        # Assume last two words are name and role
        return {"name": words[-2], "role": words[-1]}
    return {"name": "Unknown", "role": "Employee"}

# Example validators


def validate_employee_args(params: dict) -> bool:
    """Validate employee parameters."""
    if not params.get("name") or not params.get("role"):
        return False
    # Check if role is in allowed list
    allowed_roles = ["Developer", "Manager", "Designer", "Analyst", "Admin"]
    return params["role"] in allowed_roles


def validate_account_args(params: dict) -> bool:
    """Validate account parameters."""
    return bool(params.get("account_id") and len(params["account_id"]) > 0)

# Example handlers


def handle_get_balance(account_id: str) -> str:
    return f"Balance for {account_id}: $1,000"


def handle_get_transactions(account_id: str, date_range: str) -> str:
    return f"Transactions for {account_id} in {date_range}: [...]"


def handle_add_employee(name: str, role: str) -> str:
    return f"Added employee {name} as {role}"


# Build the taxonomy tree
banking_node = TreeBuilder.classifier_node(
    name="Banking",
    classifier=keyword_classifier,
    children=[
        TreeBuilder.intent_node(
            name="GetBalance",
            param_schema={"account_id": str},
            handler=handle_get_balance,
            arg_extractor=extract_account_args,
            input_validator=validate_account_args,
            description="Get the account balance."
        ),
        TreeBuilder.intent_node(
            name="GetTransactions",
            param_schema={"account_id": str, "date_range": str},
            handler=handle_get_transactions,
            arg_extractor=extract_transaction_args,
            input_validator=validate_account_args,
            description="Get account transactions."
        ),
    ],
    description="Banking actions"
)

hr_node = TreeBuilder.classifier_node(
    name="HR",
    classifier=keyword_classifier,
    children=[
        TreeBuilder.intent_node(
            name="AddEmployee",
            param_schema={"name": str, "role": str},
            handler=handle_add_employee,
            arg_extractor=extract_employee_args,
            input_validator=validate_employee_args,
            description="Add a new employee."
        ),
    ],
    description="HR actions"
)

root_taxonomy = TreeBuilder.classifier_node(
    name="Root",
    classifier=keyword_classifier,
    children=[banking_node, hr_node],
    description="Business domain root"
)

# Example usage


def main():
    # Test cases
    test_inputs = [
        "banking:GetBalance account123",
        "hr:AddEmployee John Developer",
        "banking:GetTransactions account456 last_month",
        "hr:AddEmployee Jane InvalidRole",  # Should fail validation
        "Request vacation"  # Should fail routing
    ]

    for user_input in test_inputs:
        print(f"\nProcessing: {user_input}")
        result = execute_taxonomy(
            user_input=user_input, node=root_taxonomy, debug=True)
        print(f"Result: {result}")


if __name__ == "__main__":
    main()
