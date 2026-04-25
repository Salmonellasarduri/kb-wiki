---
article_id: collaborative-multi-agent-murder-mystery-vlm-enhancement
title: "Collaborative Multi-Agent Scripts Generation for Enhancing Imperfect-Information Reasoning in Murder Mystery Games"
type: stub
source_ids:
  - 6e2fd89bc3c0
topics:
  - multi-agent-frameworks
  - vision-language-models
  - murder-mystery-games
  - imperfect-information-reasoning
  - synthetic-data-generation
published_at: "2026-04-13"
source_urls:
  - https://arxiv.org/html/2604.11741v1
summary: >
  Vision-language models (VLMs) struggle with complex multi-hop reasoning in multi-player game settings with imperfect and deceptive information. 
  Researchers propose a collaborative multi-agent framework for generating high-quality murder mystery game scripts to enhance VLM reasoning capabilities through specialized training.
  The system uses coordinated agent interactions to create rich multimodal contexts and implements two-stage training with Chain-of-Thought fine-tuning and GRPO-based reinforcement learning.
aliases_ja:
  - マルチエージェントフレームワーク
  - ビジョン言語モデル
  - 殺人ミステリーゲーム
  - 不完全情報推論
  - 合成データ生成
  - VLM強化
  - Chain-of-Thought
  - 強化学習
  - GRPO
  - 多人数ゲーム
created_at: "2026-04-15 18:45"
updated_at: "2026-04-15 18:45"
---

## 概要

Vision-language models（VLM）は知覚タスクでは優れた性能を示すものの、不完全で欺瞞的な情報を含む多人数ゲーム環境での複雑な多段階推論において性能が低下することが課題となっている。

この問題に対処するため、研究者らは殺人ミステリーゲームを代表的な多人数タスクとして選択し、異なる意図を持つ役割によって提供される部分的な手がかりに基づいて隠された真実を推論する能力の向上を目指している。

## 提案手法

研究チームは、高品質で役割駆動型の多人数ゲームスクリプトを評価・合成するためのコラボレーティブ・マルチエージェント・フレームワークを提案している。このシステムは以下の特徴を持つ：

- キャラクターアイデンティティ（殺人者 vs. 無実の人）に適応した細粒度のインタラクションパターンの実現
- キャラクターの背景、視覚・テキスト手がかり、多段階推論チェーンを含む豊富なマルチモーダルコンテキストの生成
- 調整されたエージェント間相互作用による協調的データ生成

## 訓練戦略

VLMの推論能力向上のため、2段階のエージェント監視訓練戦略が設計されている：

1. **Chain-of-Thought（CoT）ベースファインチューニング**: 不確実性と欺瞞をモデル化した厳選・合成データセットでの訓練
2. **GRPOベースの強化学習**: エージェント監視型報酬シェーピングにより、キャラクター固有の推論行動と効果的なマルチモーダル多段階推論の開発を促進

## 実験結果

広範囲な実験により、この手法がVLMの以下の能力を大幅に向上させることが実証されている：

- 物語推論
- 隠された事実の抽出  
- 欺瞞に対する耐性理解

> [!note] ソースが限定的です。記事は不完全な可能性があります。

<!-- AUTO:Related Articles -->
## Related Articles

- [[synthetic-datasets-mechanism-design-real-world]]
<!-- /AUTO:Related Articles -->
