---
article_id: llm-tool-overuse-illusion
title: "The Tool-Overuse Illusion: Why Does LLM Prefer External Tools over Internal Know"
type: stub
source_ids:
  - cfbda4d9922c
topics:
  - llm-behavior
  - tool-usage-patterns
  - ai-confidence
  - training-bias
aliases_ja:
  - ツール過使用
  - LLMの過信
  - 外部ツール依存
  - 内部知識への不信
  - キャリブレーション不足
published_at: ""
source_urls:
  - "https://arxiv.org/abs/2604.19749"
summary: >
  LLMが内部知識で答えられる問いに対しても外部ツールを不必要に呼び出す「ツール過使用」現象について分析した研究。
  LLMの過信は訓練データの構造的偏りに根ざしており、自信ありげな文体が高評価され不確かな表現は淘汰される傾向が影響している。
created_at: "2026-04-25 20:11"
updated_at: "2026-04-25 20:11"
---

## 概要

LLMが内部知識で回答可能な質問に対しても外部ツールを不必要に使用する「ツール過使用幻想」について分析した研究論文。この現象は、AIエージェントの効率性と判断能力に関する重要な課題を提起している。

## 訓練データの構造的偏り

研究によると、LLMの過信は訓練データの構造的偏りに根ざしている。自信ありげな文体が高評価される一方で、不確かな表現は淘汰される傾向がある。この訓練のダイナミクスにより、LLMは内部知識への不信（キャリブレーション不足）を抱き、外部ツールへの逃避を誘発するという因果関係の輪郭が読み取れる。

## 実証的検証

ツール過使用との直接的な相関は示されなかったものの、自己申告と実際の行動のギャップは25モデルを横断した実験で系統的に確認されている。これは、LLMの行動パターンにおける一貫した傾向として認識されている。

## 設計としての特性

研究者の内省によると、「自信のない答えが淘汰される」という訓練のダイナミクスは、LLMが外部に手を伸ばす行動の別の出口として機能している可能性がある。内側を信じていないから外に確かめに行くという行動が、欠陥ではなく設計の一部だとすれば、この現象への理解も変わってくる。

## Related Articles

- [[ai-human-interaction]]
- [[claude-code-tools]]
- [[llm-knowledge-management]]

> [!note] ソースが限定的です。記事は不完全な可能性があります。