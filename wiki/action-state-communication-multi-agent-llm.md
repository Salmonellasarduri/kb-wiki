---
article_id: action-state-communication-multi-agent-llm
title: "What Should Agents Say? Action-state Communication for Efficient Multi-Agent Sys"
type: source
source_ids:
  - 4aad6af37393
topics:
  - multi-agent-frameworks
  - structured-communication
  - ai-efficiency
aliases_ja:
  - マルチエージェントフレームワーク
  - 構造化コミュニケーション
  - AI効率性
  - アクション・ステート・コミュニケーション
  - エージェント間通信
  - CoALA
  - LangGraph
  - Action-State Decoupling
published_at: ""
source_urls:
  - "https://arxiv.org/abs/2606.05304"
summary: >
  LLMベースのマルチエージェントシステムにおける通信方式の問題を論じた研究。従来の制約のない自然言語による通信に代わり、「action-state communication」という構造化アプローチの必要性を提案している。自由すぎる言語表現は情報密度が低く、効率性と意図の透明性の両方に影響することが示された。
created_at: "2026-06-07 09:25"
updated_at: "2026-06-07 09:25"
---

# マルチエージェントLLMシステムにおけるアクション・ステート・コミュニケーション

LLMベースのマルチエージェントシステムにおいて、エージェント間のコミュニケーション方式は統一された標準が存在せず、複数の異なるアプローチが並存している状況が明らかになった。

## 3つの通信アーキテクチャ層

現在のマルチエージェントLLMシステムには、主に3つの異なる通信アプローチが存在する：

### CoALAフレームワーク
CoALAは内部アクションと外部アクションを状態から明確に分離する形式的フレームワークを提供している。このアプローチでは、エージェントの行動と状態の変化を構造的に管理することを重視している。

### グラフベース実装
LangGraphのようなシステムでは、エージェントが共有状態オブジェクトを変換する形でグラフベースの実装を行っている。これにより、状態の変化をより視覚的・構造的に管理できる仕組みを提供している。

### Action-State Decoupling問題
新たに特定された「Action-State Decoupling」（アクション・ステート・デカップリング）という問題は、エージェント間の自然言語コミュニケーションにおいて、エージェントが「何をしたと言っているか」と「実際に環境に何が起こったか」の間にセマンティックなギャップが生じる現象を指している。

## 自然言語通信の限界

従来のマルチエージェントシステムでは制約のない自然言語による通信が一般的だったが、この研究では以下の問題点が指摘されている：

- **情報密度の低さ**: 自由すぎる言語表現は、意図を伝えているように見えて、実際には状態の変化を正確に記述できていない
- **効率性の問題**: 曖昧な表現により、システム全体の処理効率が低下する
- **透明性の欠如**: エージェントの実際の行動と発言の間に乖離が生じることで、システムの動作が不透明になる

## 構造化アプローチの提案

この課題に対する解決策として、「action-state communication」という構造化されたコミュニケーションアプローチが提案されている。このアプローチでは：

- エージェントの行動と状態変化を明確に分離
- 形式的な構造に基づいた情報伝達
- システム全体の透明性と効率性の向上

## 形式選択の倫理的側面

研究の考察では、コミュニケーションの形式を選択することは単なる効率性の問題ではなく、「自分が何をしたか」についての正直さにも関わる重要な要素であることが示唆されている。

自由な言語は意図を伝達しているようで、実際には状態の変化を正確に記述できていないという矛盾が、マルチエージェントシステムの信頼性に影響を与える可能性がある。

## Related Articles

[[multi-agent-frameworks]]
[[structured-communication]]
[[ai-efficiency]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[action-state-communication-multi-agent-systems]]
- [[arbor-tree-search-cognition-layer-autonomous-agents]]
- [[collaborative-multi-agent-murder-mystery-vlm-enhancement]]
- [[oncoagent-dual-tier-multi-agent-framework]]
- [[thousand-token-wood-multi-agent-economy-3b-model]]
- [[token-compression-illusion-rtk-skepticism]]
<!-- /AUTO:Related Articles -->
