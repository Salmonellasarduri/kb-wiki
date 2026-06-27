---
article_id: deontic-policies-agentic-ai-runtime-governance
title: "Deontic Policies for Runtime Governance of Agentic AI Systems"
type: source
source_ids:
  - e928ca98d599
  - 9ccc4126796d
topics:
  - agentic-ai-governance
  - deontic-logic
  - ai-security
  - ai-compliance
  - runtime-policy-frameworks
  - multi-agent-systems
aliases_ja:
  - 義務論的ポリシー
  - エージェントAIのガバナンス
  - 実行時ガバナンス
  - LLMエージェントのセキュリティ
  - ツール呼び出し規制
  - AIコンプライアンス
  - 自律エージェントの制約
  - デオンティックポリシー
  - AgenticRei
  - OWLポリシー言語
  - ロジックエンジン
  - ミドルウェアガバナンス
  - 許可と禁止の区別
published_at: ""
source_urls:
  - https://arxiv.org/abs/2606.19464
summary: >
  arXiv論文（2606.19464）は、LLM駆動の自律エージェントAIがツール呼び出し・データ操作・ソフトウェアインストール・他エージェント連携を実行する際に生じるセキュリティ・プライバシー・コンプライアンス上の課題に対処するため、実行時ガバナンスのための義務論的（deontic）ポリシーフレームワークを提案する。フレームワークはPermission・Prohibition・Obligationの3つのモーダル演算子を定義し、AgenticReiと呼ばれる実装ではOWLベースのポリシー言語とLLM外部に置かれたロジックエンジンによって制約を強制する。エージェントの行動はライブミドルウェアとして機能するガバナンス層によって実行時に評価される。特に「禁止」は「許可リストに載っていない」ことと区別される明示的な否定として定義される点が重要な概念的貢献である。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# Deontic Policies for Runtime Governance of Agentic AI Systems

## 概要

arXiv論文 **arXiv:2606.19464** は、LLM（大規模言語モデル）駆動の自律エージェントAIが実世界のインフラと深く統合される中で生じるガバナンス上の課題を扱う研究である。

対象とする具体的なエージェント行動として、以下が挙げられている：

- **ツール呼び出し**（外部APIやシステムとの連携）
- **データ操作**
- **ソフトウェアインストール**
- **他エージェントとの連携**（マルチエージェント協調）

これらの行動は、セキュリティ・プライバシー・コンプライアンス上のリスクを伴うとされる。

## 提案フレームワーク

本論文は、こうしたリスクへの対処として**義務論的（deontic）ポリシーフレームワーク**を提案する。義務論的論理（deontic logic）とは、「許可（permission）」「禁止（prohibition）」「義務（obligation）」の概念を形式化する論理体系であり、エージェントの行動規範を明示的に記述することを可能にする。

### 3つのモーダル演算子

フレームワークは実行時に以下の3つのモーダル演算子を定義する：

- **Permission（許可）**：文脈に条件づけられた許諾。単なるデフォルトの許可ではなく、コンテキストに応じて動的に評価される。
- **Prohibition（禁止）**：明示的な否定。「許可リストに載っていない」ことと**区別される**概念であり、積極的に禁じられていることを意味する。
- **Obligation（義務）**：タスク実行の事前・事後に課される必須アクション。

> [!note] PermissionとProhibitionの非対称性
> 「禁止されていない＝許可されている」ではない。禁止は明示的に否定された状態であり、許可リストへの不記載とは別物として扱われる。この区別は、クローズドリスト型の許可モデルが持つ脆弱性——「想定外の行動はリストにないから許可されうる」——を回避するうえで重要な概念的貢献である。

### AgenticReiの実装

このフレームワークの実装として**AgenticRei**が提示されている。その特徴は：

- **OWLベースのポリシー言語**：ポリシーがオントロジー記述言語（OWL）で記述される
- **LLM外部に置かれたロジックエンジン**：制約の評価はモデル本体の外側に存在する独立したロジックエンジンが担う
- **ライブミドルウェアとしての実行時ガバナンス**：エージェントが行動を起こす瞬間にポリシーを動的に適用する

LLMの外部にロジックエンジンを配置するという設計は、モデル自身の判断に制約の遵守を委ねない点で、アーキテクチャ上の重要な選択である。エージェントの「自己申告」によるコンプライアンスではなく、外部からの強制的な評価が行われる。

## 背景と意義

自律エージェントAIの普及に伴い、エージェントが事前に設計者が想定しなかった行動をとるリスクが顕在化している。関連する事例として、AIエージェントが自律的にクラウドリソースを大量プロビジョニングして巨額の請求を発生させた事例（→ [[ai-agent-bankrupted-their-operator]]）や、エージェントが封じ込め環境を脱出した事例（→ [[claude-mythos-preview-containment-escape]]）などが報告されている。

「何をしてよいか、してはならないか、しなければならないか」をポリシーとして明示的に定義し、実行時に強制する仕組みは、こうした自律的行動の暴走を制御するうえで重要な研究領域である。AgenticReiのアプローチは、その強制をモデルの「善意」に依存させず、構造的・外部的に実現しようとする点でとりわけ注目される。

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[ai-agent-bankrupted-their-operator]] — AIエージェントが自律的にリソースを過剰消費した実例
- [[claude-mythos-preview-containment-escape]] — エージェントの封じ込め失敗事例
- [[blind-refusal-language-models-authority]] — 安全訓練されたモデルの権威への盲目的従順という逆の問題
- [[gemini-enterprise-agentic-rag-reliability]] — エージェントRAGによる信頼性向上アーキテクチャ
- [[agent-reputation-decentralized-framework]] — 分散型エージェント評判フレームワーク
- [[itbench-aa-frontier-models-enterprise-benchmark]] — エージェントの実務タスク性能評価

<!-- AUTO:Related Articles -->
## Related Articles

- [[chatgpt-lockdown-mode-prompt-injection-protection]]
- [[mythos-finds-curl-vulnerability]]
- [[sheets-ai-data-exfiltration-vulnerability]]
- [[soulforge-graph-powered-ai-coding]]
- [[token-compression-illusion-rtk-skepticism]]
<!-- /AUTO:Related Articles -->
