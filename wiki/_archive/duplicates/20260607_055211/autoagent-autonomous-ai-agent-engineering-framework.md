---
article_id: autoagent-autonomous-ai-agent-engineering-framework
title: AutoAgent - 自律的AIエージェント開発フレームワーク
type: source
source_ids:
  - 72483ef1d96b
topics:
  - ai-agent-development
  - autonomous-programming
  - meta-agent-engineering
  - docker-containerization
  - benchmark-automation
aliases_ja:
  - オートエージェント
  - 自律的エージェント開発
  - メタエージェント
  - エージェント工学
  - AIエージェント自動構築
  - プログラムMD
  - ハーバー互換タスク
  - ベンチマーク自動実行
published_at: ""
source_urls:
  - https://github.com/kevinrgu/autoagent
summary: >
  AutoAgentは、AIエージェントに目標を与えるだけで、一晩かけて自律的にエージェントハーネスを構築・改善させるフレームワーク。
  メタエージェントがシステムプロンプト、ツール、設定、オーケストレーションを自動修正し、ベンチマークスコアによって改善を判定する。
  Harbor互換のタスク形式とDocker隔離により安全な自動開発環境を提供する。
created_at: "2026-04-05 18:34"
updated_at: "2026-04-05 18:34"
---

## 概要

AutoAgentは、AIエージェントの開発プロセスを自動化するフレームワークである。開発者がPythonハーネスファイルを直接編集する代わりに、AIエージェントに目標を与えるだけで、メタエージェントが一晩かけてエージェントハーネスを自律的に構築・改善する。

システムは「autoresearch」の概念をエージェント工学に応用しており、メタエージェントがシステムプロンプト、ツール定義、エージェント設定、オーケストレーションを自動修正し、ベンチマークを実行してスコアを確認、改善されれば採用、悪化すれば破棄というサイクルを繰り返す。

## アーキテクチャと主要コンポーネント

### 単一ファイルハーネス設計

AutoAgentでは、エージェント全体が`agent.py`という単一ファイルに集約される。このファイルには以下が含まれる：

- 設定（config）
- ツール定義
- エージェントレジストリ
- ルーティング/オーケストレーション
- Harbor アダプター境界

Harbor アダプター部分は固定として明示的にマークされており、残りの部分がメタエージェントの主要な編集対象となる。

### プログラム制御ファイル

`program.md`は人間が編集する唯一のファイルで、以下を含む：

- メタエージェント向けの指示
- 構築すべきエージェントの種類を定義するディレクティブ

このMarkdownファイルがメタエージェントにコンテキストを提供し、エージェント工学ループを定義する。

### タスクとベンチマーク

`tasks/`ディレクトリには、Harbor形式の評価タスクが格納される。各タスクは以下の構造を持つ：

```
tasks/my-task/
├── task.toml          # 設定（タイムアウト、メタデータ）
├── instruction.md     # エージェントに送られるプロンプト
├── tests/
│   ├── test.sh       # エントリポイント、/logs/reward.txtに結果出力
│   └── test.py       # 検証（確定的またはLLM-as-judge）
└── environment/
    ├── Dockerfile    # タスクコンテナ（FROM autoagent-base）
    └── files/        # コンテナにマウントされる参照ファイル
```

## 動作原理

### ヒルクライミング最適化

システムの核心は、ベンチマークのタスクテストスイートが生成する総合スコアによるヒルクライミング最適化である。メタエージェントは以下のサイクルを繰り返す：

1. 現在のハーネスを検査
2. ベンチマークを実行
3. 失敗を診断
4. `agent.py`を修正
5. スコアを比較して採用/破棄を判定

### Docker隔離

エージェントはコンテナ内で実行されるため、ホストシステムを損傷する可能性がない。この隔離により安全な自動開発環境が提供される。

### Harbor互換性

タスクはHarborベンチマークと同じ形式を使用するため、同一ハーネスを異なるデータセットで評価可能である。テストは0.0-1.0のスコアを検証ログに書き込み、メタエージェントがこの数値でヒルクライミングを行う。

## セットアップと使用方法

### 基本セットアップ

```bash
# 1. uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 依存関係のインストール
uv sync

# 3. 環境変数の設定
cat > .env << 'EOF'
OPENAI_API_KEY=...
EOF

# 4. ベースイメージの構築
docker build -f Dockerfile.base -t autoagent-base .
```

### ベンチマーク実行

```bash
# 単一タスクの実行
rm -rf jobs; mkdir -p jobs && uv run harbor run -p tasks/ --task-name "<task-name>" -l 1 -n 1 --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1

# 全タスクの並列実行
rm -rf jobs; mkdir -p jobs && uv run harbor run -p tasks/ -n 100 --agent-import-path agent:AutoAgent -o jobs --job-name latest > run.log 2>&1
```

### メタエージェントの起動

コーディングエージェントにリポジトリを指定し、以下のプロンプトを与える：

```
Read program.md and let's kick off a new experiment!
```

メタエージェントがディレクティブを読み取り、現在のハーネスを検査し、ベンチマークを実行し、失敗を診断し、`agent.py`を修正し、反復を開始する。

## プロジェクト構造

```
.
├── agent.py           # テスト対象のハーネス（単一ファイル）
├── program.md         # メタエージェント指示 + ディレクティブ
├── tasks/            # Harbor形式のベンチマークタスク
├── .agent/           # 再利用可能な指示、メモ、プロンプト、スキル
├── Dockerfile.base   # ベースイメージ
├── jobs/             # Harbor ジョブ出力
├── results.tsv       # 実験ログ（メタエージェントが作成、gitignore対象）
└── run.log          # 最新実行の出力
```

## 設計思想

### メタプログラミング

人間はハーネスを直接プログラムするのではなく、メタエージェントをプログラムする。人間は`program.md`を通じてループを操縦し、メタエージェントが`agent.py`を編集する。

### レジストリ駆動

実装は簡潔性のため単一ファイルに存在するが、エージェントとツールの登録は構造化されているため、ハーネスは整然と進化できる。

### スコア駆動

すべての実験は数値スコアを生成する。より良ければ保持、悪ければ破棄という、autoresearchと同じループを採用している。

## 商用展開と採用情報

開発チームは自動設定エージェント関連の製品を近日中にローンチ予定で、サインアップを受け付けている。また、この分野に関心のあるエンジニアの採用も行っており、GitHubリンクと共に`hello@thirdlayer.inc`への連絡を呼びかけている。

## メンテナンスとトラブルシューティング

### Docker環境の管理

実行を重ねるとDockerイメージとコンテナが蓄積するため、定期的なクリーンアップが推奨される：

```bash
# Harbor のキャッシュされたタスクイメージとキャッシュ
uv run harbor cache clean -f

# 完全なDocker環境のクリーンアップ
docker system prune -a -f

# 軽量版：停止コンテナのみ削除
docker container prune -f
```

多数の並列実行後にDockerが応答しなくなった場合は、Docker Desktopの再起動が有効である：

```bash
killall Docker && open -a Docker
```

## 拡張機能

Agent Skills for Context Engineering および context7 スキルをエージェントに装備することで、パフォーマンス向上が期待できる。

## Related Articles

[[claude-code-cli-computer-use-implementation]] - AIエージェントによる自動開発環境との関連
[[obsidian-mind-claude-code-persistent-memory-system]] - エージェント記憶システムの実装手法
[[llm-personal-knowledge-base-workflow-andrej-karpathy]] - 自動化されたナレッジベース構築との比較
