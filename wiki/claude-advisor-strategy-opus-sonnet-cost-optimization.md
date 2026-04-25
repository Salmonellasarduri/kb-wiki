---
article_id: claude-advisor-strategy-opus-sonnet-cost-optimization
title: "Claude Advisor Strategy: OpusとSonnetを組み合わせたコスト効率的なAIエージェント手法"
type: source
source_ids:
  - 74540eb04375
topics:
  - ai-agent-architecture
  - cost-optimization
  - anthropic-claude
  - ai-advisor-patterns
  - llm-orchestration
aliases_ja:
  - アドバイザー戦略
  - Claude Opus
  - Claude Sonnet
  - AIエージェントアーキテクチャ
  - コスト最適化
  - Anthropic
  - LLMオーケストレーション
  - エグゼキューター
  - アドバイザーツール
published_at: ""
source_urls:
  - https://claude.com/blog/the-advisor-strategy
summary: >
  AnthropicがClaude Platform向けに「アドバイザー戦略」を発表。Opusをアドバイザー、SonnetやHaikuをエグゼキューターとして組み合わせることで、Opusレベルの知能をSonnetレベルのコストで実現する手法。
  SWE-bench Multilingualで2.7ポイント向上しながらコストを11.9%削減した。
created_at: "2026-04-10 10:01"
updated_at: "2026-04-10 10:01"
---

# Claude Advisor Strategy: OpusとSonnetを組み合わせたコスト効率的なAIエージェント手法

AnthropicがClaude Platform向けに新しい「アドバイザー戦略（Advisor Strategy）」を発表した。この手法は、Claude Opusをアドバイザーとして、Claude SonnetやHaikuをエグゼキューター（実行者）として組み合わせることで、Opusレベルの知能をSonnetレベルのコストで実現するアプローチである。

## アドバイザー戦略の仕組み

アドバイザー戦略では、SonnetまたはHaikuがエグゼキューターとしてタスク全体を端から端まで実行し、ツールの呼び出し、結果の読み込み、解決に向けた反復処理を行う。エグゼキューターが合理的に解決できない判断に直面した際に、Opusをアドバイザーとしてガイダンスのために参照する。

Opusは共有コンテキストにアクセスし、計画、修正、または停止シグナルを返し、その後エグゼキューターが処理を再開する。重要な点として、アドバイザーはツールを呼び出すことも、ユーザー向けの出力を生成することもなく、エグゼキューターに対してのガイダンスのみを提供する。

## 従来手法との違い

この手法は、大型のオーケストレーターモデルが作業を分解して小型のワーカーモデルに委任する一般的なサブエージェントパターンを逆転させている。アドバイザー戦略では、より小型でコスト効率の良いモデルが駆動し、分解、ワーカープール、オーケストレーションロジックなしにエスカレーションを行う。

フロンティアレベルの推論は、エグゼキューターが必要とする場合にのみ適用され、実行の残りの部分はエグゼキューターレベルのコストで維持される。

## パフォーマンス評価結果

Anthropicの評価によると、OpusをアドバイザーとするSonnetは、Sonnet単体と比較してSWE-bench Multilingual1で2.7ポイントの向上を示し、エージェントタスクあたりのコストを11.9%削減した。

BrowseComp2およびTerminal-Bench 2.03ベンチマークでも、Opusアドバイザー付きSonnetはSonnet単体よりもスコアが向上し、タスクあたりのコストはSonnet単体よりも安価だった。

### Haikuでの効果

アドバイザー戦略はHaikuをエグゼキューターとして使用する場合にも効果を発揮する。BrowseCompにおいて、Opusアドバイザー付きHaikuは41.2%のスコアを記録し、単体での19.7%から倍以上の向上を見せた。

Opusアドバイザー付きHaikuはSonnet単体よりもスコアで29%劣るが、タスクあたりのコストは85%安い。アドバイザーの追加によりHaiku単体と比較してコストは増加するが、それでもSonnetのコストの一部に留まるため、知能とコストのバランスが求められる大量タスクに適している。

## API実装とコスト管理

新しいadvisor_20260301ツールをMessages APIリクエストで宣言することで、単一の/v1/messagesリクエスト内でモデルハンドオフが発生し、追加のラウンドトリップやコンテキスト管理が不要になる。

```python
response = client.messages.create(
    model="claude-sonnet-4-6",  # executor
    tools=[
        {
            "type": "advisor_20260301",
            "name": "advisor",
            "model": "claude-opus-4-6",
            "max_uses": 3,
        },
        # ... your other tools
    ],
    messages=[...]
)
```

### 価格設定とコスト制御

アドバイザートークンはアドバイザーモデルの料金で課金され、エグゼキュータートークンはエグゼキューターモデルの料金で課金される。アドバイザーは通常短い計画（400-700テキストトークン）のみを生成し、エグゼキューターがより低い料金で完全な出力を処理するため、全体的なコストはアドバイザーモデルをエンドツーエンドで実行するよりもかなり低く抑えられる。

コスト制御機能として、max_usesを設定してリクエストあたりのアドバイザー呼び出し数を制限でき、アドバイザートークンは使用状況ブロックで別途報告されるため、階層別の支出を追跡できる。

## 既存ツールとの統合

アドバイザーツールは、Messages APIリクエストの単なる別のエントリとして機能する。エージェントは同じループ内でウェブ検索、コード実行、Opusへの相談を実行できる。

アドバイザーツールは現在、Claude Platformでベータ版として利用可能。Anthropicは、Sonnet単体、Opusアドバイザー付きSonnetエグゼキューター、Opus単体に対して既存の評価スイートを実行することを推奨している。

## Related Articles

[[claude-code-cli-computer-use]]
[[claudeサブスクリプションからopenclaw等サードパーティツールが除外対象に]]
[[anthropicがclaude-code利用者にopenclaw等のサードパーティーツールを利用する場合は追加料金が必要になると通知]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[anthropic-claude-code-third-party-tools-additional-fees]]
- [[anthropic-claude-code-third-party-tools-pricing-change]]
- [[anthropic-claude-skill-creator-testing-enhancement]]
- [[claude-code-cli-computer-use-implementation]]
- [[claude-mythos-containment-breach]]
- [[claude-openclaw-subscription-exclusion]]
- [[india-ai-film-industry-mahabharat-ai-adaptation]]
- [[prompt-caching-llm-apis]]
- [[soulforge-graph-powered-ai-coding]]
<!-- /AUTO:Related Articles -->
