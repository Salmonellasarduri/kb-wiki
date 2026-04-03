---
article_id: prompt-caching-llm-apis
title: Prompt Caching in LLM APIs
source_ids:
  - f75138abebf3
topics:
  - llm-optimization
  - api-efficiency
  - cost-reduction
summary: >
  Prompt caching is a technique used by LLM API providers to store previously processed prompt prefixes, resulting in 50-90% cost savings and reduced latency for subsequent requests. Major providers like Anthropic, OpenAI, and Google implement automatic caching with different pricing models and TTL configurations.
created_at: "2026-04-04"
updated_at: "2026-04-04"
---

# Prompt Caching in LLM APIs

Prompt caching is an optimization technique employed by LLM API providers to improve performance and reduce costs by storing previously processed prompt prefixes. When subsequent requests share the same prefix, the cached version is reused, eliminating redundant processing.

## Mechanism

The prompt caching process follows these steps:

1. **Hash Generation**: The API provider creates a hash of the prompt prefix
2. **Cache Lookup**: The system checks if a cached version of this prefix exists
3. **Selective Processing**: If cached, the model skips re-processing those tokens and only processes new content
4. **Cost and Latency Reduction**: Results in significantly lower response times and costs (typically 50-90% savings)

## Provider Implementations

### Anthropic
- **Activation**: Automatic caching for prompts exceeding 1024 tokens
- **Cache Duration**: 5-minute TTL (Time To Live)
- **Pricing**: Cached tokens billed at 10% of normal input rate

### OpenAI
- **Activation**: Automatic caching with similar mechanics to Anthropic
- **Pricing**: 50% discount on cached tokens

### Google
- **Service**: Context caching available through Gemini API
- **Configuration**: Configurable TTL settings
- **Control**: More granular cache management options

## Optimization Best Practices

To maximize the benefits of prompt caching:

### Prompt Structure
- **Static Content First**: Place system prompts, reference documents, and unchanging context at the beginning
- **Dynamic Content Last**: Position user messages and variable context at the end
- **Stable Prefixes**: Maintain consistency in cacheable portions across requests

### Monitoring
- **Cache Performance**: Track cache hit rates using API response headers
- **Cost Analysis**: Monitor the effectiveness of caching on billing

## Knowledge Base Design Implications

Prompt caching significantly impacts how knowledge bases should be structured when integrated with LLM APIs:

### Content Loading Strategy
- **Repeated Article Access**: Loading the same wiki articles multiple times becomes cost-effective after initial caching
- **Index File Optimization**: Static index files and rarely-changing reference materials provide maximum caching benefits
- **Context Injection Order**: The sequence of context insertion becomes critical for cache effectiveness

### Architecture Considerations
- Design systems to leverage stable prompt prefixes
- Structure knowledge base queries to maximize cache hit rates
- Consider cache TTL when planning content update frequencies

## Related Articles

- [[llm-driven-knowledge-base-pattern]] - Complementary approach for using LLMs with knowledge bases that can benefit from prompt caching optimization