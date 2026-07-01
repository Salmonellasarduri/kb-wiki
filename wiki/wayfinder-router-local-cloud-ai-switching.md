---
article_id: wayfinder-router-local-cloud-ai-switching
title: "Wayfinder Router：タスク難易度でローカルAIとクラウドAIを自動切り替えるオープンソースツール"
type: stub
source_ids:
  - 28a4898f6eca
topics:
  - local-ai-tools
  - cloud-ai-routing
  - ai-cost-optimization
  - open-source-ai
  - ai-infrastructure
aliases_ja:
  - Wayfinder
  - ウェイファインダー
  - ローカルAIとクラウドAIの切り替え
  - AIルーター
  - タスク難易度による振り分け
  - ローカルAI自動切り替え
  - クラウドAIコスト削減
  - オープンソースAIルーティング
published_at: "2026-06-30"
source_urls:
  - https://gigazine.net/news/20260630-wayfinder
summary: >
  「Wayfinder Router」はGitHubで公開されたオープンソースツールで、タスクの難易度に応じてローカルAIとクラウドAIを自動的に振り分ける。短い要約や誤字修正はローカルAIに、複雑な推論やコード解析はクラウドAIに割り当てる設計で、切り替え判断自体にはAIを使わないことでコストを削減する点が特徴的。
created_at: "2026-07-01 06:07"
updated_at: "2026-07-01 06:07"
---

# Wayfinder Router：タスク難易度でローカルAIとクラウドAIを自動切り替えるオープンソースツール

## 概要

「Wayfinder Router」は、タスクの難易度に応じてローカルAIとクラウドAIを自動的に振り分けるオープンソースツールで、GitHubで公開されている。

## 振り分けの仕組み

タスクの種類に応じて処理先を自動的に選択する：

- **ローカルAIに振り分けるタスク**：短い要約、誤字修正など、軽量な処理
- **クラウドAIに振り分けるタスク**：複雑な推論、コード解析など、高度な処理

## 設計上の特徴：切り替え判断にAIを使わない

本ツールの注目すべき設計方針として、**ルーティング（切り替え判断）自体にAIを使用しない**という点がある。AIを使って「このタスクをどのAIに渡すか」を判断させるメタな再帰的構造を意図的に避けることで、コストを削減している。

この設計は「メタな再帰を意図的に断ち切ることで賢さを証明している」とも評されており、判断のためにさらにAIを呼び出すという無駄なコストを省く実用的なアプローチである。

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[apfel-mac-foundation-models]] — MacのFoundation Modelsをローカルで直接利用できるツール
- [[corporate-america-ai-cost-rationing]] — 企業がAI利用コスト上昇を受けて使用を制限し始めている動向
- [[llm-api-prompt-caching]] — LLM APIのプロンプトキャッシュ機能によるコスト削減手法

<!-- AUTO:Related Articles -->
## Related Articles

- [[ai-datacenter-construction-delays-transformer-battery-shortage]]
- [[meta-aws-graviton5-ai-agent-partnership]]
- [[nii-llm-jp-4-japanese-language-model]]
- [[ollama-criticism-llama-cpp-recommendation]]
- [[tokenomics-agentic-software-engineering]]
<!-- /AUTO:Related Articles -->
