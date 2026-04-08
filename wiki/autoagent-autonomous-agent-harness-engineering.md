---
article_id: autoagent-autonomous-agent-harness-engineering
title: AutoAgent - AIエージェントハーネス自律開発システム
type: source
source_ids:
  - 72483ef1d96b
topics:
  - autonomous-ai-agents
  - agent-engineering
  - meta-learning-systems
  - docker-automation
  - benchmark-optimization
aliases_ja:
  - 自律AIエージェント
  - エージェントエンジニアリング
  - メタ学習システム
  - Docker自動化
  - ベンチマーク最適化
  - autoagent
  - ケビン・グ
  - サードレイヤー
  - harbor
  - エージェントハーネス
published_at: ""
source_urls:
  - https://github.com/kevinrgu/autoagent
summary: >
  AutoAgentは、AIエージェントに課題を与えて一晩で自律的にエージェントハーネスを構築・最適化させる開発システム。
  AIエージェントがシステムプロンプト、ツール、設定、オーケストレーションを自動修正し、ベンチマークスコアで評価して改善を繰り返す。
  人間はharness Pythonファイルではなくprogram.mdでメタエージェントに指示を与える新しい開発手法を提案している。
created_at: "2026-04-05 18:34"
updated_at: "2026-04-05 18:34"
---

## 概要

AutoAgentは、AIエージェントに課題を与えることで、一晩かけて自律的にエージェントハーネスを構築・最適化させる開発システムです。kevinrguによって開発され、thirdlayer.incが商用化を進めています。

このシステムの核心は、従来の「エンジニアがPythonファイルを直接編集する」開発手法を根本的に変革することです。代わりに、人間は`program.md`というMarkdownファイルでメタエージェントに指示を与え、AIがシステムプロンプト、ツール、エージェント設定、オーケストレーションを自動修正します。

## システム構造

### 主要ファイル構成

AutoAgentは以下の明確な役割分担でファイルが構成されています：

**agent.py** - テスト対象の全ハーネスが単一ファイルに集約されています。設定、ツール定義、エージェントレジストリ、ルーティング/オーケストレーション、Harbor適応境界が含まれ、適応セクションは固定、残りがメタエージェントの主要編集領域となります。

**program.md** - メタエージェントへの指示とディレクティブ（構築すべきエージェントの種類）を定義するファイルで、人間が編集します。

**tasks/** - Harbor形式の評価タスクが格納され、クリーンなベースラインブランチではベンチマークペイロードが省略される場合があります。

**.agent/** - 再利用可能な指示、ノート、プロンプト、スキルのためのオプション作業領域です。

### 評価・最適化メカニズム

メタエージェントは**ベンチマークのタスクテストスイートによって生成される総合スコア**を評価指標として使用します。このスコアに対してヒルクライミング手法で最適化を行い、改善があれば変更を保持、なければ破棄するサイクルを繰り返します。

## 技術的要件とセットアップ

### 前提条件

- Docker
- Python 3.10+
- uv
- 現在のagent.pyハーネスが要求するモデルプロバイダーの認証情報

### インストールプロセス

```bash
# 1. uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 依存関係のインストール
uv sync

# 3. 環境変数の設定
cat > .env << 'EOF'
OPENAI_API_KEY=...
EOF

# 4. ベースイメージのビルド
docker build -f Dockerfile.base -t autoagent-base .
```

### ベンチマーク実行

単一タスクの実行：
```bash
rm -rf jobs; mkdir -p jobs && uv run harbor run -p tasks/ --task-name "<task-name>" -l 1 -n 1 --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1
```

並列全タスク実行：
```bash
rm -rf jobs; mkdir -p jobs && uv run harbor run -p tasks/ -n 100 --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1
```

## Harbor互換タスクフォーマット

AutoAgentはHarborのタスクフォーマットを採用しており、以下の構造でタスクを定義します：

```
tasks/my-task/
├── task.toml          # 設定（タイムアウト、メタデータ）
├── instruction.md     # エージェントに送信されるプロンプト
├── tests/
│   ├── test.sh       # エントリーポイント、/logs/reward.txtを書き出し
│   └── test.py       # 検証（決定論的またはLLM-as-judge）
└── environment/
    ├── Dockerfile    # タスクコンテナ（FROM autoagent-base）
    └── files/        # コンテナにマウントされる参照ファイル
```

テストは0.0-1.0のスコアを検証ログに書き出し、メタエージェントがこの値でヒルクライミングを行います。

## 設計哲学

### 4つの核心原則

1. **メタエージェント主導** - 人間はハーネスを直接プログラムせず、`program.md`を通じてループを操作
2. **単一ファイルベース** - 実装は簡潔性のため一つのファイルに集約、ただしレジストリ駆動で構造は維持
3. **Docker分離** - エージェントはコンテナ内で実行され、ホストシステムを損傷できない
4. **スコア駆動** - 全ての実験が数値スコアを生成し、改善があれば保持、なければ破棄

## 運用とメンテナンス

### 実行方法

コーディングエージェントにリポジトリを向けて以下のプロンプトを使用：
```
Read program.md and let's kick off a new experiment!
```

メタエージェントがディレクティブを読み、現在のハーネスを検査し、ベンチマークを実行し、失敗を診断して`agent.py`を修正、反復を行います。

### Docker環境のクリーンアップ

実行を重ねるとDockerイメージとコンテナが蓄積するため、定期的なクリーンアップが必要です：

```bash
# Harborのキャッシュされたタスクイメージとキャッシュ
uv run harbor cache clean -f

# 完全なDockerクリーンアップ
docker system prune -a -f

# 軽量版：停止コンテナのみ
docker container prune -f
```

## パフォーマンス向上オプション

AutoAgentは、パフォーマンス向上のためにAgent Skills for Context Engineeringとcontext7スキルを装備することができます。

## Related Articles

[[claude-code-cli-computer-use-implementation]] - AIによる自律的PC操作システム
[[obsidian-mind-claude-code-memory-system]] - Claude Codeの記憶システム強化
[[llm-personal-knowledge-base-workflow-karpathy]] - LLMを活用した知識ベース構築手法
