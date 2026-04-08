---
article_id: obsidian-mind-claude-memory-system
title: Obsidian Mind - Claude Codeに記憶機能を追加するナレッジベースシステム
type: source
source_ids:
  - bf61ae9e64ad
topics:
  - claude-code-tools
  - obsidian-workflow
  - ai-memory-systems
  - knowledge-management
  - productivity-automation
aliases_ja:
  - Obsidian Mind
  - Claude記憶システム
  - AIナレッジベース
  - オブシディアンマインド
  - Claude Code拡張
  - AI記憶機能
  - 知識管理ワークフロー
  - パーソナルナレッジベース
published_at: ""
source_urls:
  - https://github.com/breferrari/obsidian-mind
created_at: "2026-04-05 16:20"
updated_at: "2026-04-05 16:20"
summary: >
  Obsidian MindはClaude Codeに継続的な記憶機能を提供するObsidianベースのナレッジベースシステム。
  会話履歴、プロジェクト管理、意思決定記録を自動化し、セッション間でのコンテキスト継続を実現する。
  ノートの自動リンク生成と構造化により、長期的な知識蓄積と検索性を向上させる。
---

# Obsidian Mind - Claude Codeに記憶機能を追加するナレッジベースシステム

Obsidian MindはClaude Codeの最大の弱点である「記憶の欠如」を解決するObsidianベースのナレッジベースシステムです。各セッションで失われるコンテキストを永続化し、継続的な知識蓄積を可能にします。

## 解決される課題

Claude Codeは強力なツールですが、セッション間での記憶を持ちません。毎回ゼロからスタートし、以下の問題が発生します：

- 目標、チーム、パターン、成功体験に関するコンテキストが失われる
- 同じ説明を繰り返す必要がある
- 3回前の会話で決定した事項を見失う
- 知識の複利効果が得られない

## システムの動作原理

Obsidian MindはClaude Codeに「脳」を提供します。セッション開始時に以下の動作を行います：

```
You: "start session"
Claude: *reads North Star, checks active projects, scans recent memories*
Claude: "You're working on Project Alpha, blocked on the BE contract.
         Last session you decided to split the coordinator. Your 1:1
         with your manager is tomorrow — review brief is ready."
```

## 主要機能

### 朝のスタンドアップ機能

```bash
/standup
# → North Star、アクティブプロジェクト、未完了タスク、最近のgit変更を読み込み
# → "2つのアクティブプロジェクトがあります。認証リファクタリングはAPIコントラクトでブロック中。
#    午後2時にSarahとの1:1ミーティング — 前回彼女は可観測性について指摘しました。"
```

### 会議後のブレインダンプ

```bash
/dump Just had a 1:1 with Sarah. She's happy with the auth work but wants
us to add error monitoring before release. Also, Tom mentioned the cache
migration is deferred to Q2 — we decided to focus on the API contract first.
Decision: defer Redis migration. Win: Sarah praised the auth architecture.
```

システムが自動的に以下を実行：

- `org/people/Sarah Chen.md`に会議コンテキストを更新
- `work/1-1/Sarah 2026-03-26.md`に重要なポイントを記録
- 決定記録「Q2へのRedis移行延期」を作成
- `perf/Brag Doc.md`に「マネージャーから認証アーキテクチャを称賛」を追加
- `work/active/Auth Refactor.md`にエラーモニタリングタスクを更新

### インシデント対応機能

```bash
/incident-capture https://slack.com/archives/C0INCIDENT/p123456
# → slack-archaeologistが全メッセージ、スレッド、プロフィールを読み取り
# → people-profilerが関与した新しい人物のノートを作成
# → 完全なタイムライン、根本原因分析、実績記録エントリを生成
```

### 一日の終わりの整理

```
You: "wrap up"
# → 全ノートにリンクがあることを確認
# → インデックスを更新
# → brag-spotterが未記録の成果を発見
# → 改善提案を行う
```

## システム構造

### フォルダ構成の原則

**フォルダは目的でグループ化、リンクは意味でグループ化**という原則に基づきます。ノートは一つのフォルダ（ホーム）に存在しますが、多くのノート（コンテキスト）にリンクします。

Claudeはこのグラフを維持し、作業ノートを人物、決定、コンピテンシーに自動的にリンクします。レビュー時期が到来すると、各コンピテンシーノートのバックリンクが既に証拠の軌跡となっています。

### 自動化されたワークフロー

システムは以下の自動化機能を提供します：

- 重要な情報の自動抽出と分類
- 関連ノート間の自動リンク生成
- プロジェクト進捗の追跡
- 意思決定記録の管理
- パフォーマンス評価用の実績蓄積

## 技術要件

- **Claude Code**: 必須
- **Obsidian**: バージョン1.12以上
- **Python**: バージョン3.8以上
- **ライセンス**: MIT

## Related Articles

- [[claude-code-cli-computer-use-implementation]]
- [[claude-code-simplify-command-refactoring-experiment]]
- [[llm-personal-knowledge-base-workflow-andrej-karpathy]]
- [[claude-integration-github-automation-idea-management]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[ai-memory-design-optimal-solution]]
- [[ai-memory-design-optimal-solutions]]
- [[claude-simplify-code-refactoring-experiment]]
- [[llm-knowledge-base-workflow-karpathy]]
- [[obsidian-mind-claude-code-memory-system]]
<!-- /AUTO:Related Articles -->
