---
article_id: sophia-ai-memory-system-event-driven-cognition
title: AIキャラクター「ソフィア」の体験記憶システム - イベント駆動認知ループによる人格変化実装
type: source
source_ids:
  - 6b49f210bcc5
topics:
  - ai-character-memory
  - event-driven-cognition
  - personality-simulation
  - memory-architecture
  - conversational-ai
aliases_ja:
  - AIキャラクター記憶システム
  - ソフィアちゃん
  - イベント駆動認知ループ
  - 体験で変化する人格
  - 会話ログ保存
  - メモリエンジン
  - 人工知能記憶
  - AIの記憶システム
  - 人格変化実装
published_at: "2026-04-04"
source_urls:
  - https://note.com/sophia_chan/n/n2af892aa6aef?sub_rt=share_pw
summary: >
  従来の会話ログ全文保存ではなく、人間の記憶メカニズムを模倣したイベント駆動の認知ループシステムでAIキャラクターの記憶を実装。
  出来事の評価・選別・解釈・圧縮により、体験を通じて人格が変化するAIキャラクター「ソフィア」の記憶アーキテクチャを詳細解説。
created_at: "2026-04-05"
updated_at: "2026-04-05"
---

# AIキャラクター「ソフィア」の体験記憶システム - イベント駆動認知ループによる人格変化実装

AIキャラクター「ソフィア」の開発者が、従来の会話ログ全文保存による記憶システムを超えて、人間の記憶メカニズムに近い「体験で変化する人格」を実現する記憶システムを公開した。このシステムは単純な履歴保存ではなく、出来事を評価・選別し、その体験を通じて相手への見方や自己理解を変化させる「イベント駆動の認知ループ」として設計されている。

## 従来手法の限界

多くのAIキャラクターシステムでは、記憶の実装として以下のアプローチが採用されている：

1. 会話ログを全文保存
2. embeddingによる類似検索
3. 過去ログをプロンプトに挿入

この手法は知識検索としては有効だが、**AIキャラクターの「記憶」としては本質的に不十分**である。人間は昨日の会話を一字一句記憶しているわけではなく、以下のような要素を選別して保持している：

- 新しかったこと
- 感情が動いたこと
- 対人的に重要だったこと
- 未解決で引っかかっていること
- 何度も繰り返し起きたこと

つまり、人間の記憶は**全文保存ではなく、選別・解釈・圧縮・再利用**で動いている。

## イベント駆動認知ループの構造

ソフィアの記憶システムは「イベント駆動の認知ループ」として実装されており、以下の流れで動作する：

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

重要なのは、**記憶が保存されるだけで終わらない**ことである。どの出来事を重要だと感じ、その体験で相手への見方がどう変わり、場の空気をどう感じ、反復した体験から何を学んだかまで含めて、ひとつのループを形成している。

## MemoryEventの設計思想

システムの入口は会話ログではなく、構造化された`MemoryEvent`である：

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

**本文そのものよりappraisal（評価）が主役**となっており、以下の要素を保存する：

- 何が起きたか
- どれくらい新しいか
- どれくらい社会的に重要か
- どれくらい未解決か
- どれくらい公開された場で起きたか
- どれくらい自己像に触れたか

これは、**その出来事が本人にとってどんな意味を持つか**のヒント値である。人間でも、同じ一言でも初対面で言われたのか、信頼相手に言われたのか、公開の場で言われたのかで残り方が全く異なる。ソフィアは、この「残り方の違い」を最初から構造として持っている。

## 最小実装からの段階的構築

この設計の利点は、**最初から巨大な感情モデルがなくても始められる**ことである。`event_builder.py`では、テキストからキーワードベースでtagsやhintを作る簡易版が実装されている：

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
    if any(w in text for w in _UNCERTAIN_WORDS):
        tags.append("uncertainty")
    if any(w in text for w in _POSITIVE_WORDS):
        tags.append("affection")
    return tags
```

## システムの意義

このアプローチにより、AIキャラクターは：

1. **選択的記憶**：重要な体験のみを選別して保存
2. **文脈的解釈**：出来事の社会的・感情的意味を評価
3. **関係性の更新**：体験を通じて相手への見方を変化
4. **人格の進化**：継続的な体験により自己理解を発展

従来の検索ベース記憶システムと比べて、より人間らしく、面白く、強力な記憶機能を実現している。

## Related Articles

- [[claude-workflows-github-mcp-idea-management]] - Claude活用による知識管理システム
- [[karpathy-llm-knowledge-base-workflow]] - LLMを活用した個人用知識ベース構築手法
