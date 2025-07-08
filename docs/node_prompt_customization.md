# Node-Level Prompt Customization

## Overview

Node-level prompt customization is an **advanced feature** that allows you to override the default prompts used by LLM-powered nodes. This feature is designed for expert users who need fine-grained control over how their intent classification and argument extraction works.

## ⚠️ Important Warnings

**This is an advanced feature that should be used with caution:**

- **Performance Impact**: Custom prompts can degrade performance and cause unexpected behavior
- **Debugging Complexity**: Issues with custom prompts can be difficult to troubleshoot
- **Support Limitations**: When reporting issues, always mention if you're using custom prompts
- **Default Recommendation**: Use default prompts for most use cases

## When to Use Custom Prompts

Custom prompts should only be used when:

1. You have a specific domain or use case that requires specialized prompting
2. You've thoroughly tested the default prompts and found them insufficient
3. You understand the risks and are prepared to troubleshoot issues
4. You're an advanced user with experience in prompt engineering

## Default Behavior

By default, all nodes use internal default prompts that are:

- **Optimized for performance** and reliability
- **Thoroughly tested** across various use cases
- **Well-documented** and maintained
- **Recommended for most users**

## Supported Node Types

### HandlerNode (Argument Extraction)

Handler nodes support custom prompts for argument extraction:

```python
from intent_kit.builder import handler

# Basic usage (recommended)
greet_handler = handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG
)

# Advanced usage (expert only)
greet_handler = handler(
    name="greet",
    description="Greet the user", 
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG,
    custom_prompts={
        "extraction": """
        You are a specialized name extractor for greeting users.
        
        User Input: {user_input}
        
        Required Parameters:
        {param_descriptions}
        
        {context_info}
        
        Instructions:
        - Extract the person's name from the user input
        - If no name is found, use "there" as default
        - Return the result as: "name: [extracted_name]"
        
        Extracted Parameters:
        """
    },
    suppress_warnings=True  # Acknowledge risks to silence warnings
)
```

### ClassifierNode (Intent Classification)

Classifier nodes support custom prompts for intent classification:

```python
from intent_kit.builder import llm_classifier

# Basic usage (recommended)
classifier = llm_classifier(
    name="root",
    children=[greet_handler, calc_handler, weather_handler],
    llm_config=LLM_CONFIG
)

# Advanced usage (expert only)
classifier = llm_classifier(
    name="root",
    children=[greet_handler, calc_handler, weather_handler],
    llm_config=LLM_CONFIG,
    custom_prompts={
        "classification": """
        You are a specialized intent classifier for a customer service bot.
        
        User Input: {user_input}
        
        Available Intents:
        {node_descriptions}
        
        {context_info}
        
        Instructions:
        - Classify the user's intent based on the available options
        - Consider the context information when making your decision
        - Return only the number (1-{num_nodes}) corresponding to your choice
        - If no intent matches, return 0
        
        Your choice (number only):
        """
    }
)
```

## Warning Suppression

By default, nodes with custom prompts will log warning messages to alert you about the advanced nature of this feature. If you acknowledge the risks and want to suppress these warnings, you can set `suppress_warnings=True`:

```python
# With warnings (default)
handler = handler(
    name="test",
    description="Test handler",
    handler_func=lambda x: f"Hello {x}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG,
    custom_prompts={"extraction": "Custom prompt..."}
    # Warning will be logged
)

# Without warnings (acknowledge risks)
handler = handler(
    name="test",
    description="Test handler", 
    handler_func=lambda x: f"Hello {x}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG,
    custom_prompts={"extraction": "Custom prompt..."},
    suppress_warnings=True  # No warnings logged
)
```

**Note**: Only use `suppress_warnings=True` when you fully understand the risks of custom prompts and are prepared to handle any issues that may arise.

## Prompt Template Variables

When creating custom prompts, you can use these template variables:

### For Argument Extraction (`extraction` prompt)

- `{user_input}`: The user's input text
- `{param_descriptions}`: Formatted list of required parameters
- `{param_names}`: Comma-separated list of parameter names
- `{context_info}`: Available context information (if any)

### For Intent Classification (`classification` prompt)

- `{user_input}`: The user's input text
- `{node_descriptions}`: Formatted list of available child nodes
- `{num_nodes}`: Number of available child nodes
- `{context_info}`: Available context information (if any)

## Troubleshooting

### If You Experience Issues

1. **First Step**: Revert to default prompts
   ```python
   # Remove custom_prompts parameter
   handler = handler(
       name="test",
       description="Test handler",
       handler_func=lambda x: x,
       param_schema={"x": str},
       llm_config=LLM_CONFIG
       # No custom_prompts parameter
   )
   ```

2. **Test with Defaults**: Verify the issue persists with default prompts

3. **Report Issues**: When reporting issues, always mention:
   - Whether you're using custom prompts
   - What custom prompts you're using
   - Whether the issue occurs with default prompts

### Common Issues

- **Poor Performance**: Custom prompts may be too complex or inefficient
- **Inconsistent Results**: Custom prompts may not handle edge cases properly
- **Token Limits**: Very long custom prompts may exceed model token limits
- **Format Issues**: Custom prompts may not follow expected output formats

## Best Practices

### Do's

- ✅ Test thoroughly with various inputs
- ✅ Keep prompts concise and focused
- ✅ Use clear, unambiguous instructions
- ✅ Include fallback instructions for edge cases
- ✅ Document your custom prompts

### Don'ts

- ❌ Don't use custom prompts unless necessary
- ❌ Don't make prompts overly complex
- ❌ Don't ignore the template variables
- ❌ Don't use prompts that are too long
- ❌ Don't forget to test edge cases

## Migration Guide

### From Builder-Level Prompts

If you're currently using builder-level prompt customization:

```python
# Old way (builder-level)
handler = handler(
    name="test",
    description="Test",
    handler_func=lambda x: x,
    param_schema={"x": str},
    llm_config=LLM_CONFIG,
    extraction_prompt="Custom prompt..."  # Old parameter
)

# New way (node-level)
handler = handler(
    name="test", 
    description="Test",
    handler_func=lambda x: x,
    param_schema={"x": str},
    llm_config=LLM_CONFIG,
    custom_prompts={
        "extraction": "Custom prompt..."  # New parameter
    }
)
```

## Support and Documentation

- **Default prompts are recommended** for most use cases
- **Custom prompts are for advanced users only**
- **Always test thoroughly** before using in production
- **Report issues with context** about prompt usage

## Examples

See the `examples/` directory for complete working examples of node-level prompt customization.