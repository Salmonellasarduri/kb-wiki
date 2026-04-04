---
article_id: sofia-ai-memory-system-event-driven-personality
title: ソフィアAI記憶システム - イベント駆動による人格変化の実装アーキテクチャ
source_ids:
  - 6b49f210bcc5
topics:
  - ai-character-development
  - memory-systems
  - event-driven-architecture
  - cognitive-modeling
  - personality-simulation
aliases_ja:
  - ソフィアちゃん
  - メモリーイベント
  - 認知ループ
  - 記憶システム
  - イベント駆動
summary: >
  AIキャラクター「ソフィア」は従来の会話ログ保存に代わり「イベント駆動認知ループ」による記憶システムを実装。
  MemoryEventによる体験の評価・選別・圧縮を通じて、人間の記憶特性（新しさ・感情・社会的重要性）を模倣し、体験による人格変化を実現する。
created_at: "2026-04-05"
updated_at: "2026-04-05"
---

# ソフィアAI記憶システム - イベント駆動による人格変化の実装アーキテクチャ

AIキャラクター「ソフィア」の開発チームが公開した記憶システムは、従来の会話ログ全量保存アプローチとは根本的に異なる「イベント駆動認知ループ」を採用している。このシステムは人間の記憶特性を構造化し、体験による人格変化を実現することを目指している。

## 従来手法の限界と新アプローチ

多くのAIキャラクター実装では、以下の単純な記憶システムが採用されている：

1. 会話ログを全量保存
2. embedding化して類似検索
3. 過去ログをプロンプトに注入

このアプローチは知識検索としては有効だが、人間らしい「記憶」としては不十分である。人間は会話を一字一句保存するのではなく、以下の要素を選別的に記憶する：

- **新しかったこと**
- **感情が動いたこと**  
- **対人的に重要だったこと**
- **未解決で引っかかっていること**
- **何度も繰り返し起きたこと**

## イベント駆動認知ループの構造

ソフィアの記憶システムは「イベント駆動の認知ループ」として設計されている。処理フローは以下の通り：

```
外部イベント
↓
MemoryEvent に正規化
↓
write gate で保存価値を判定
├─ raw episodic に保存
└─ interpreted episodic に保存
↓
relational state 更新
social field 更新
consolidation 実行
↓
response / relation / self_consistency の3モードで想起
↓
状態要約を次の system context に戻す
```

重要なのは、記憶が単に保存されるだけでなく、**どの出来事を重要だと感じたか**、**その体験で相手への見方がどう変わったか**、**場の空気をどう感じたか**まで含めて一つのループを形成していることである。

## MemoryEventデータ構造

システムの入力は会話ログではなく `MemoryEvent` である。この設計思想により、**本文そのものより appraisal（評価）が主役**となっている：

```python
@dataclass
class MemoryEvent:
    source: str
    event_type: str
    actor_id: str | None
    target_id: str | None
    conversation_id: str | None
    timestamp: datetime
    content_text: str | None
    normalized_summary: str | None
    context_tags: list[str] = field(default_factory=list)
    publicness: float = 0.0
    audience_size_hint: float = 0.0
    novelty_hint: float = 0.0
    social_importance_hint: float = 0.0
    goal_relevance_hint: float = 0.0
    unresolvedness_hint: float = 0.0
    positive_hint: float = 0.0
    negative_hint: float = 0.0
    identity_relevance_hint: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
```

このデータ構造では、**その出来事が本人にとってどんな意味を持つか**のヒント値を保存する。同じ一言でも、初対面で言われたのか、信頼関係のある相手に言われたのか、公開の場で言われたのかによって、記憶への残り方が構造的に異なる。

## 最小実装からの段階的構築

このシステムの利点は、最初から巨大な感情モデルを必要とせず、段階的に構築できることである。初期段階では `event_builder.py` でキーワードベースの簡易実装から開始できる：

```python
def _detect_tags(text: str) -> list[str]:
    tags = []
    if "?" in text or "？" in text:
        tags.append("question")
    if any(w in text for w in _REPAIR_WORDS):
        tags.append("repair")
    if any(w in text for w in _THREAT_WORDS):
        tags.append("threat")
    if any(w in text for w in _IDENTITY_WORDS):
        tags.append("identity")
    # 続く...
    return tags
```

## 人格変化メカニズムの意義

このシステムが従来の知識ベースAIと根本的に異なるのは、記憶が**relational state**（関係状態）と**social field**（社会的場）の更新を通じて、次の発話に影響を与える点である。体験による学習と人格変化が、単なる情報検索を超えた人間らしい対話を可能にする。

この記憶システムは、AIキャラクターに真の「体験による成長」を与える可能性を示している。会話ログの蓄積ではなく、意味のある体験の積み重ねによる人格形成こそが、次世代のAIキャラクター開発の方向性を示していると言えるだろう。

## Related Articles

[[claude-automation]] - Claudeを活用したGitHub自動メモシステムの構築
[[llm-workflows]] - LLM-Driven Knowledge Base Pattern
[[japanese-llm]] - 国立情報学研究所、日本語特化LLM「LLM-jp-4」をオープンソース公開
