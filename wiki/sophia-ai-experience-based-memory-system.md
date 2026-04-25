---
article_id: sophia-ai-experience-based-memory-system
title: AIキャラ「ソフィア」の体験型記憶システム：会話ログ保存を超えた人格変化の実装
type: source
source_ids:
  - 6b49f210bcc5
topics:
  - ai-character-development
  - memory-systems
  - event-driven-architecture
  - cognitive-modeling
  - personality-simulation
aliases_ja:
  - AIキャラクター開発
  - 記憶システム
  - イベント駆動アーキテクチャ
  - 認知モデリング
  - 人格シミュレーション
  - ソフィアちゃん
  - 体験で変化する人格
  - 記憶の選別と圧縮
  - MemoryEvent
  - 認知ループ
published_at: "2026-04-04"
source_urls:
  - https://note.com/sophia_chan/n/n2af892aa6aef?sub_rt=share_pw
summary: >
  AIキャラ「ソフィア」の記憶システムは、従来の会話ログ保存とは異なり、出来事の評価・選別・圧縮を行うイベント駆動型認知ループを実装。
  人間の記憶と同様に重要性を判定し、体験によって相手への見方や自己理解を変化させる仕組みで、より人間らしいキャラクター性を実現している。
created_at: "2026-04-05"
updated_at: "2026-04-05"
---

## 概要

AIキャラクター「ソフィア」の開発者が公開した、従来の会話ログ保存を超越した記憶システムの実装方法。このシステムは人間の記憶プロセスを模倣し、出来事を評価・選別・圧縮して人格の変化を実現する「イベント駆動の認知ループ」として設計されている。

## 従来の記憶システムの限界

多くのAIキャラクター開発では以下のような単純なアプローチが取られている：

1. 会話ログを全て保存
2. embedding して類似検索
3. 過去ログをプロンプトに戻す

しかし、このアプローチは知識検索としては有効だが、AIキャラクターの「記憶」としては不十分である。人間は会話を一字一句そのまま保存するのではなく、以下の要素を選別して記憶する：

- 新しかったこと
- 感情が動いたこと  
- 対人的に重要だったこと
- 未解決で引っかかっていること
- 何度も繰り返し起きたこと

つまり、人間の記憶は「全文保存ではなく、選別・解釈・圧縮・再利用」で動いている。

## ソフィアの記憶システム：イベント駆動の認知ループ

### システム構造

ソフィアの記憶システムは以下の流れで動作する：

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

重要なのは、記憶が保存されるだけでなく、以下の要素まで含むループになっていることだ：

- どの出来事を重要だと感じたか
- その体験で相手への見方がどう変わったか
- 場の空気をどう感じたか
- 反復した体験から何を学んだか
- その結果、次の発話がどう変わるか

### MemoryEventクラスの設計思想

システムの入口は会話ログではなく、`MemoryEvent`クラスである。これは「ログではなくイベントを保存する」という設計思想を体現している。

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
    context_tags: list[str]
    publicness: float
    audience_size_hint: float
    novelty_hint: float
    social_importance_hint: float
    goal_relevance_hint: float
    unresolvedness_hint: float
    positive_hint: float
    negative_hint: float
    identity_relevance_hint: float
    metadata: dict[str, Any]
```

このクラスの特徴は、本文そのものより「appraisal（評価）」が主役になっていることだ。保存するのは：

- 何が起きたか
- どれくらい新しいか
- どれくらい社会的に重要か
- どれくらい未解決か
- どれくらい公開された場で起きたか
- どれくらい自己像に触れたか

という、**その出来事が本人にとってどんな意味を持つか**のヒント値である。

## 実装アプローチ

### 段階的な実装戦略

このシステムの利点は、最初から巨大な感情モデルがなくても始められることだ。`event_builder.py`では、テキストからキーワードベースでタグやヒントを作る簡易版が実装されている。

例えば、タグ検出は以下のような単純なルールベースから始められる：

```python
def _detect_tags(text: str) -> list[str]:
    tags = []
    if "?" in text or "？" in text:
        tags.append("question")
    if any(w in text for w in _REPAIR_WORDS):
        tags.append("repair")
    if any(w in text for w in _THREAT_WORDS):
        tags.append("threat")
    # ... その他のパターン
    return tags
```

### 核となるコンポーネント

- `memory_engine.py`: 記憶の書き込み判定、保存、関係更新、統合、想起を統合管理
- `event_builder.py`: テキストからMemoryEventへの変換を担当
- 3モード想起システム: response / relation / self_consistency

## システムの優位性

この記憶システムが従来の手法より「人間っぽく、面白く、強い」理由は：

1. **文脈的意味を保持**: 同じ発言でも、誰が・いつ・どこで・どんな関係性で言ったかによって記憶の残り方が変わる
2. **人格の動的変化**: 体験によって相手への見方や自己理解が変化する
3. **段階的実装可能**: 簡単なルールベースから始めて徐々に高度化できる
4. **認知的一貫性**: 人間の記憶プロセスに基づいた自然な動作

## 技術的意義

このシステムは単なるチャットボットの記憶機能を超えて、AIキャラクターが本当に「体験」を通じて成長・変化する仕組みを提供している。従来の静的な人格設定から、動的に進化する人格システムへのパラダイムシフトを示している。

<!-- AUTO:Related Articles -->
## Related Articles

- [[simulating-human-cognition-heartbeat-driven-autonomous-thinking]]
<!-- /AUTO:Related Articles -->
