# Prompt Caching in LLM APIs

Prompt caching is a technique where LLM API providers store previously processed prompts
to reduce latency and cost on subsequent requests with the same prefix.

## How it works

1. The API provider hashes the prompt prefix
2. If a cached version exists, the model skips re-processing those tokens
3. Only the new/different portion of the prompt is processed
4. This results in lower latency and reduced cost (typically 50-90% savings)

## Key providers

- **Anthropic**: Automatic caching for prompts > 1024 tokens. Cache TTL is 5 minutes.
  Cached tokens are billed at 10% of the normal input rate.
- **OpenAI**: Automatic caching with similar mechanics. 50% discount on cached tokens.
- **Google**: Context caching available in Gemini API with configurable TTL.

## Best practices

- Put static content (system prompts, reference docs) at the beginning of the prompt
- Put dynamic content (user message, current context) at the end
- Keep the cacheable prefix stable across requests
- Monitor cache hit rates via API response headers

## Implications for knowledge base design

When using a knowledge base with LLM APIs, prompt caching means:
- Loading the same wiki articles repeatedly is cheap after the first call
- Index files that rarely change benefit most from caching
- The order of context injection matters (stable content first)
