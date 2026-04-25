---
article_id: soulforge-graph-powered-ai-coding
title: "SoulForge: Graph-powered code intelligence, multi-agent coding with codebase-aware AI"
type: source
source_ids:
  - af50edb92452
topics:
  - ai-coding-tools
  - graph-based-intelligence
  - multi-agent-systems
  - codebase-awareness
  - cost-optimization
aliases_ja:
  - AIコーディングツール
  - グラフベース知能
  - マルチエージェントシステム
  - コードベース認識
  - コスト最適化
  - SoulForge
  - ソウルフォージ
  - dependency graph
  - 依存関係グラフ
  - Claude Code
  - クロードコード
published_at: ""
source_urls:
  - https://github.com/ProxySoul/soulforge
summary: >
  SoulForgeは、起動時に依存関係グラフを構築してコードベース全体を理解するAIコーディングツール。
  従来のAIツールと異なり、ファイル探索に時間を費やすことなく、即座にコード構造を把握して効率的な編集を実現する。
  結果として同じタスクを約2倍少ないステップ、約2倍低いコストで完了できる。
created_at: "2026-04-15 02:43"
updated_at: "2026-04-15 02:43"
---

SoulForgeは、従来のAIコーディングツールが抱える「盲目的な探索」問題を解決する革新的なコード支援システムです。起動時にコードベース全体の依存関係グラフを構築し、リアルタイムで更新することで、AIエージェントが迷わずに適切なファイルと関数を特定できます。

## 従来のAIコーディングツールの課題

既存のAIコーディングツールは「盲目状態」でスタートします。ファイルを読み、grepで検索し、徐々にコードベースの構造を理解しようとします。ユーザーは待たされ、料金を支払いながら、エージェントは本来の作業ではなく「探索作業」に時間を費やします。

SoulForgeは起動時点でコードベース全体を把握済みです。どのファイルが重要で、何が何に依存し、編集の影響がどこまで波及するかを、一行も書く前に理解しています。

## 核心技術：リアルタイム依存関係グラフ

### グラフ構築と重要度ランキング
- 全ファイル、シンボル、インポートのグラフを作成
- 重要度によるランキング機能
- Git履歴による情報の豊富化
- リアルタイム更新

### 外科的コード抽出
- 500行のファイルから必要な関数やクラスのみを20行で抽出
- 33言語をサポート
- 名前による正確な抽出

## マルチエージェント並列処理

SoulForgeは並列動作する複数のエージェント（探索、コーディング、ウェブ検索）を展開し、共有キャッシュにより一つのエージェントの発見が他のエージェントに瞬時に伝達されます。

### コンテキスト管理と圧縮
- 会話状況をリアルタイムで追跡
- 長時間の対話では瞬時に圧縮が発動
- 多くの場合、LLMコストゼロで実行

## 技術インフラ

### 4段階フォールバック解析
1. LSP（Language Server Protocol）
2. ts-morph
3. tree-sitter
4. 正規表現フォールバック

デュアルLSPバックエンドにより、エディタの起動有無に関わらず動作します。

### モデル戦略
- 計画立案：Opus
- コーディング：Sonnet
- クリーンアップ：Haiku
- 20のプロバイダーを内蔵
- タスクルーターによる完全制御

## 開発環境統合

### エディタ統合
- 組み込みNeovim（ユーザー設定をそのまま使用）
- ユーザーの設定、プラグイン、LSPサーバーを継承
- AIはユーザーと同じエディタで編集作業

### MCP（Model Context Protocol）サポート
- 任意のMCPサーバーへの接続
- stdio、HTTP、SSEトランスポート
- 自動再接続とネームスペース化されたツール

## 拡張性とカスタマイズ

### フック機能
- 13種類のイベントフック（PreToolUse、PostToolUse、SessionStartなど）
- Claude Code互換
- 既存プラグインのドロップイン対応

### スキルシステム
- ドメイン固有機能をインストール可能
- 承認ゲート付き
- コミュニティレジストリからのブラウジングとインストール

### マルチセッション対応
- 最大5つの同時セッション
- タブごとのモデル設定
- ファイル要求とGit連携の調整

## インストールと使用方法

### macOS/Linux対応
初回起動時にNeovimとNerd Fontsの自動インストールを提案します。

```bash
# Homebrew
brew tap proxysoul/tap && brew install soulforge

# Bun (global)
bun install -g @proxysoul/soulforge

# 事前ビルド版
tar xzf soulforge-*.tar.gz && cd soulforge-*/ && ./install.sh

# ソースからビルド
git clone https://github.com/ProxySoul/soulforge.git && cd soulforge && bun install
bun run dev
```

### 基本コマンド
```bash
soulforge                              # 起動、Ctrl+Lでモデル選択
soulforge --set-key anthropic sk-ant-... # API キー保存
soulforge --headless "your prompt here"   # 非インタラクティブモード
```

## 競合ツールとの比較

| 項目 | SoulForge | Claude Code | Aider |
|------|-----------|-------------|--------|
| コードベース認識 | 依存関係グラフ + ランキング | ファイル読み込み + grep | Tree-sitter + PageRank |
| コスト最適化 | 外科的読み込み + 瞬時圧縮 + 共有キャッシュ | 自動圧縮 | - |
| コード解析 | 4段階フォールバック、デュアルLSP | MCP経由LSP | Tree-sitter AST |
| マルチエージェント | 共有キャッシュ付き並列処理 | サブエージェント + チーム | 単一 |
| エディタ統合 | 組み込みNeovim | なし | なし |

## ライセンス

Business Source License 1.1の下でリリースされています。個人利用と内部利用は無料、商用利用には商用ライセンスが必要です。2030年3月15日にApache 2.0に移行予定です。

## Related Articles

[[claude-code-cli-computer-use]]
[[anthropic-claude-third-party-tools-pricing]]
[[claude-code-simplify-refactoring]]
[[ai-assisted-development]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[claude-advisor-strategy-opus-sonnet-cost-optimization]]
- [[claude-coding-vibes-getting-worse]]
- [[india-ai-film-industry-mahabharat-ai-adaptation]]
- [[mark-zuckerberg-returns-to-coding-with-ai-tools]]
- [[prompt-caching-llm-apis]]
<!-- /AUTO:Related Articles -->
