#!/usr/bin/env python3
"""
Audit Log Demo

This example demonstrates the audit log functionality in the LLM base class.
The audit log stores all input and output interactions for compliance and debugging.
"""

import os
from intent_kit.services.ai.base_client import AuditLogEntry
from intent_kit.services.ai.openai_client import OpenAIClient
from intent_kit.services.ai.anthropic_client import AnthropicClient
from intent_kit.services.ai.ollama_client import OllamaClient


def demo_audit_log():
    """Demonstrate the audit log functionality."""
    print("Audit Log Demo")
    print("=" * 50)
    
    # Example 1: Using OpenAI client with audit logging
    print("\n1. OpenAI Client Audit Log Example")
    print("-" * 40)
    
    # Note: In a real scenario, you would set your API key
    # api_key = os.getenv("OPENAI_API_KEY")
    # client = OpenAIClient(api_key=api_key)
    
    # For demo purposes, we'll show the structure without making actual API calls
    print("Audit log automatically captures:")
    print("  - Input prompts")
    print("  - Output responses") 
    print("  - Model used")
    print("  - Provider")
    print("  - Token usage (input/output)")
    print("  - Cost")
    print("  - Duration")
    print("  - Timestamp")
    
    # Example 2: Accessing audit log data
    print("\n2. Accessing Audit Log Data")
    print("-" * 40)
    
    print("Methods available:")
    print("  - client.get_audit_log() -> List[AuditLogEntry]")
    print("  - client.clear_audit_log() -> None")
    print("  - client.audit_log -> List[AuditLogEntry] (direct access)")
    
    # Example 3: Audit log entry structure
    print("\n3. Audit Log Entry Structure")
    print("-" * 40)
    
    print("AuditLogEntry fields:")
    print("  - timestamp: datetime")
    print("  - input_prompt: str")
    print("  - output_response: str")
    print("  - model: str")
    print("  - provider: str")
    print("  - input_tokens: int")
    print("  - output_tokens: int")
    print("  - cost: float")
    print("  - duration: float")
    
    # Example 4: Usage pattern
    print("\n4. Usage Pattern")
    print("-" * 40)
    
    print("""
# Initialize client
client = OpenAIClient(api_key="your-api-key")

# Make LLM calls (audit logging happens automatically)
response1 = client.generate("What is AI?", model="gpt-4")
response2 = client.generate("Explain machine learning", model="gpt-4")

# Access audit log
audit_log = client.get_audit_log()
print(f"Total interactions: {len(audit_log)}")

# Process audit entries
for entry in audit_log:
    print(f"Model: {entry.model}, Cost: ${entry.cost:.4f}")
    print(f"Input: {entry.input_prompt[:50]}...")
    print(f"Output: {entry.output_response[:50]}...")
    print("---")

# Clear audit log if needed
client.clear_audit_log()
""")
    
    # Example 5: Compliance and debugging benefits
    print("\n5. Benefits")
    print("-" * 40)
    
    print("Compliance:")
    print("  - Track all AI interactions for regulatory requirements")
    print("  - Maintain detailed logs for audit purposes")
    print("  - Monitor usage patterns and costs")
    
    print("\nDebugging:")
    print("  - Review input/output pairs for quality issues")
    print("  - Analyze performance and cost patterns")
    print("  - Troubleshoot model behavior")
    
    print("\nAnalytics:")
    print("  - Calculate total costs across all interactions")
    print("  - Analyze token usage patterns")
    print("  - Monitor response times and performance")


def show_audit_log_structure():
    """Show the structure of the audit log implementation."""
    print("\nAudit Log Implementation Details")
    print("=" * 50)
    
    print("""
The audit log feature is implemented in the BaseLLMClient class:

1. Audit Log Storage:
   - self.audit_log: List[AuditLogEntry] = []
   - Automatically initialized in __init__

2. Logging Method:
   - _log_audit_entry(response: LLMResponse, prompt: str)
   - Called automatically after each generate() call

3. Access Methods:
   - get_audit_log() -> List[AuditLogEntry]
   - clear_audit_log() -> None

4. Integration:
   - All concrete LLM clients (OpenAI, Anthropic, etc.) 
     automatically log audit entries
   - No additional code required in client implementations
   - Transparent to existing code
""")


if __name__ == "__main__":
    demo_audit_log()
    show_audit_log_structure()