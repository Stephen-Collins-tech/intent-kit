# Cost Monitoring and Reporting

## Overview

Intent Kit provides built-in cost monitoring capabilities to track and analyze API usage costs across different AI providers. This document covers how to use the cost monitoring features and generate detailed cost reports.

## Cost Tracking Features

### Automatic Cost Tracking

The framework automatically tracks costs for all AI service calls through the pricing service:

- **Token Counting**: Input and output tokens are counted for each request
- **Cost Calculation**: Costs are calculated based on provider-specific pricing
- **Model Tracking**: Different models and their costs are tracked separately
- **Session Correlation**: Costs are correlated with session IDs for analysis

### Supported Providers

- **OpenAI**: GPT models with real-time pricing
- **Anthropic**: Claude models with current pricing
- **Google**: Gemini models with Google's pricing structure
- **Ollama**: Local models (typically $0 cost)
- **OpenRouter**: Various models with OpenRouter pricing

## Cost Report Generation

### Basic Cost Report

To generate a cost report from your application logs:

```bash
# First, run your application with cost logging enabled
PYTHONUNBUFFERED=1 LOG_LEVEL=debug uv run examples/simple_demo.py | grep "COST" > file.log

# Then generate the cost report
sed -nE 's/.*Cost: \$([0-9.]+).*Input: ([0-9]+) tokens, Output: ([0-9]+) tokens,.*Model: ([^,]+).*/\1 \2 \3 \4/p' file.log \
| awk '{
    c=$1; i=$2; o=$3; m=$4
    cost[m]+=c; inT[m]+=i; outT[m]+=o; n[m]++
    Tcost+=c; Tin+=i; Tout+=o; N++
}
END{
    printf "%-30s %6s %10s %10s %10s %14s %14s\n", "Model","Requests","InTok","OutTok","Tokens","Cost($)","$/token"
    for(m in cost){
        all=inT[m]+outT[m]; rate=(all>0?cost[m]/all:0)
        printf "%-30s %6d %10d %10d %10d %14.9f %14.9f\n", m, n[m], inT[m], outT[m], all, cost[m], rate
    }
    printf "-----------------------------------------------------------------------------------------------\n"
    allTot=Tin+Tout; rateTot=(allTot>0?Tcost/allTot:0)
    printf "%-30s %6d %10d %10d %10d %14.9f %14.9f\n", "TOTAL", N, Tin, Tout, allTot, Tcost, rateTot
}'
```

### Sample Output

```
Model                          Requests      InTok     OutTok     Tokens        Cost($)        $/token
mistralai/ministral-8b             12       1390        242       1632    0.000245000    0.000000150
google/gemma-2-9b-it                6       1031         28       1059    0.000012000    0.000000011
-----------------------------------------------------------------------------------------------
TOTAL                              18       2421        270       2691    0.000257000    0.000000096
```

## Cost Monitoring in Code

### Enabling Cost Tracking

Cost tracking is enabled by default when using the AI service clients. The framework automatically:

1. **Counts tokens** for each request
2. **Calculates costs** based on current pricing
3. **Logs cost information** with structured logging
4. **Correlates costs** with session and request IDs

### Accessing Cost Information

```python
from intent_kit.services.ai import LLMFactory
from intent_kit.context import Context

# Create context with debug logging
context = Context(debug=True)

# Create LLM client
client = LLMFactory.create_client("openai", api_key="your-key")

# Make requests - costs are automatically tracked
response = client.generate_text("Hello, world!", context=context)

# Cost information is logged automatically
# Look for log entries containing "COST" information
```

### Cost Log Format

Cost information is logged in the following format:

```
COST: $0.000123, Input: 10 tokens, Output: 5 tokens, Model: gpt-3.5-turbo, Session: abc-123
```

This includes:
- **Cost**: Total cost in USD
- **Input tokens**: Number of input tokens
- **Output tokens**: Number of output tokens  
- **Model**: Model name used
- **Session**: Session ID for correlation

## Advanced Cost Analysis

### Provider-Specific Analysis

You can filter cost reports by provider:

```bash
# Filter for OpenAI costs only
grep "openai" file.log | grep "COST" | # ... cost analysis script

# Filter for Anthropic costs only  
grep "anthropic" file.log | grep "COST" | # ... cost analysis script
```

### Time-Based Analysis

Add timestamps to your cost analysis:

```bash
# Extract timestamp and cost information
sed -nE 's/.*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*Cost: \$([0-9.]+).*/\1 \2/p' file.log \
| awk '{
    date=$1; cost=$2
    daily_cost[date]+=cost
}
END{
    for(date in daily_cost){
        printf "%s: $%.6f\n", date, daily_cost[date]
    }
}'
```

### Session-Based Analysis

Track costs per session:

```bash
# Extract session and cost information
sed -nE 's/.*Session: ([^,]+).*Cost: \$([0-9.]+).*/\1 \2/p' file.log \
| awk '{
    session=$1; cost=$2
    session_cost[session]+=cost
}
END{
    for(session in session_cost){
        printf "Session %s: $%.6f\n", session, session_cost[session]
    }
}'
```

## Cost Optimization Strategies

### 1. Model Selection

- **Use cheaper models** for simple tasks
- **Reserve expensive models** for complex reasoning
- **Consider local models** (Ollama) for development

### 2. Token Optimization

- **Minimize input tokens** by being concise
- **Use few-shot examples** efficiently
- **Implement caching** for repeated requests

### 3. Request Batching

- **Batch similar requests** when possible
- **Use streaming** for long responses
- **Implement request deduplication**

### 4. Monitoring and Alerts

- **Set cost thresholds** for alerts
- **Monitor usage patterns** regularly
- **Track cost per session/user**

## Integration with Monitoring Systems

### Prometheus Metrics

You can expose cost metrics for Prometheus:

```python
from prometheus_client import Counter, Histogram

# Cost metrics
cost_counter = Counter('ai_cost_total', 'Total AI cost', ['provider', 'model'])
token_counter = Counter('ai_tokens_total', 'Total tokens', ['provider', 'model', 'type'])
```

### Custom Dashboards

Create dashboards to visualize:

- **Cost trends** over time
- **Model usage** distribution
- **Session cost** analysis
- **Provider comparison** charts

## Best Practices

### 1. **Regular Monitoring**
- Generate cost reports daily/weekly
- Set up automated cost alerts
- Track cost per feature/component

### 2. **Cost Attribution**
- Tag costs with user/session IDs
- Track costs per workflow step
- Correlate costs with business metrics

### 3. **Optimization**
- Regularly review model usage
- Implement cost-aware routing
- Use caching strategies

### 4. **Documentation**
- Document cost expectations
- Track cost changes over time
- Share cost insights with team

## Troubleshooting

### Common Issues

1. **Missing cost information**
   - Ensure debug logging is enabled
   - Check that pricing service is configured
   - Verify provider API keys are valid

2. **Incorrect cost calculations**
   - Verify pricing data is current
   - Check token counting accuracy
   - Validate provider-specific pricing

3. **Performance impact**
   - Cost tracking has minimal overhead
   - Consider sampling for high-volume applications
   - Use async logging for better performance

## Conclusion

The cost monitoring system in Intent Kit provides comprehensive tracking and analysis capabilities. By following the patterns outlined in this document, you can:

- **Track costs** across all AI providers
- **Generate detailed reports** for analysis
- **Optimize usage** based on cost data
- **Integrate with monitoring systems** for real-time insights

This enables informed decision-making about AI model usage and helps control costs while maintaining application performance.
