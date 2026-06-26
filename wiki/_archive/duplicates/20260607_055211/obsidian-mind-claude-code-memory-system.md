---
article_id: obsidian-mind-claude-code-memory-system
title: Obsidian Mind - Claude Codeに永続的記憶を与えるメモシステム
type: source
source_ids:
  - bf61ae9e64ad
topics:
  - claude-code-integration
  - obsidian-workflow
  - persistent-ai-memory
  - knowledge-management
  - ai-productivity-tools
aliases_ja:
  - オブシディアン・マインド
  - Claude Code記憶システム
  - AIメモリー永続化
  - オブシディアン連携
  - ナレッジマネジメント
  - AI記憶システム
  - Claude Code拡張
published_at: ""
source_urls:
  - https://github.com/breferrari/obsidian-mind
summary: >
  Claude CodeにObsidianベースの永続的記憶システムを提供するプロジェクト。セッション間で文脈を保持し、プロジェクト状況・人間関係・決定記録を自動的に管理・更新する。
  毎回の会話がゼロからではなく、過去のコンテキストを基に継続的な知識構築を可能にする。
created_at: "2026-04-05 16:20"
updated_at: "2026-04-05 16:20"
---

# Obsidian Mind - Claude Codeに永続的記憶を与えるメモシステム

Obsidian MindはClaude Codeに永続的な記憶機能を提供するシステムです。従来のClaude Codeは各セッションで記憶がリセットされる問題を解決し、継続的な文脈保持とナレッジベース構築を実現します。

## 解決する問題

Claude Codeの根本的な制限として、セッション間での記憶の継続性がありません。毎回ゼロからスタートし、以下の問題が発生します：

- 目標、チーム、パターン、成功体験の文脈が失われる
- 同じ説明を繰り返す必要がある
- 3回前の会話で決定した内容が失われる
- 知識が蓄積されず化合しない

## システムの動作原理

### セッション開始時の自動コンテキスト読み込み

```
ユーザー: "start session"
Claude: *North Starを読み込み、アクティブプロジェクトをチェック、最近の記憶をスキャン*
Claude: "Project Alphaに取り組み中で、BEコントラクトでブロック状態。
         前回セッションでコーディネーターを分割することに決定。
         明日マネージャーとの1:1があり、レビューブリーフは準備済み。"
```

### 実用的なコマンド例

**朝のスタンドアップ**
```bash
/standup
# → North Star、アクティブプロジェクト、オープンタスク、最近のgit変更を読み込み
# → "2つのアクティブプロジェクトがあります。認証リファクタリングはAPI契約でブロック。
#    午後2時にSarahとの1:1 — 前回はオブザーバビリティについて指摘されました。"
```

**ミーティング後のブレインダンプ**
```bash
/dump Sarahとの1:1を実施。認証作業には満足しているが、リリース前にエラー監視を
追加したいとのこと。また、Tomがキャッシュ移行をQ2に延期と言及 — API契約を
優先することに決定。決定：Redis移行をQ2に延期。成果：認証アーキテクチャがマネージャーに評価された。
```

システムの自動処理：
- `org/people/Sarah Chen.md`にミーティング文脈を更新
- `work/1-1/Sarah 2026-03-26.md`に主要テイクアウェイを作成
- 意思決定記録「Redis移行をQ2に延期」を作成
- `perf/Brag Doc.md`に「認証アーキテクチャがマネージャーに評価」を追加
- `work/active/Auth Refactor.md`にエラー監視タスクを更新

## フォルダ構造とリンク戦略

システムは「フォルダは目的でグループ化、リンクは意味でグループ化」という原則に従います。ノートは1つのフォルダに属しますが（ホーム）、多くのノートとリンクで結ばれます（文脈）。

Claudeは以下を自動維持します：
- 作業ノートと人物・決定・能力の自動リンク
- レビュー時期に各能力ノートのバックリンクが証跡として機能
- リンクのないノートの検出と改善提案

## インシデント対応機能

```bash
/incident-capture https://slack.com/archives/C0INCIDENT/p123456
# → slack-archaeologistが全メッセージ、スレッド、プロフィールを読み込み
# → people-profilerが関係者の新しいノートを作成
# → 完全なタイムライン、根本原因分析、brag doc エントリを生成
```

## 1日の終わりの自動整理

```
ユーザー: "wrap up"
# → 全ノートのリンク検証
# → インデックス更新
# → brag-spotterが未捕獲の成果を発見
# → 改善提案
```

## 必要な技術要件

- Claude Code（必須）
- Obsidian 1.12以上
- Python 3.8以上
- MITライセンス

## Related Articles

この記事は以下の記事と関連があります：
- [[claudeを使った思いつき自動メモシステム]]
- [[llmによる個人ナレッジベース構築ワークフロー]]
- [[claude-code-cliにcomputer-use機能実装]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[llm-knowledge-base-workflow-karpathy]]
- [[llm-wiki-knowledge-management-karpathy]]
- [[obsidian-mind-claude-memory-system]]
<!-- /AUTO:Related Articles -->
