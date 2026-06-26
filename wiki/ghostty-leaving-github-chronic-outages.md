---
article_id: ghostty-leaving-github-chronic-outages
title: "Ghostty Is Leaving GitHub"
type: stub
source_ids:
  - df4ece02e1df
topics:
  - github-reliability
  - development-infrastructure
  - platform-migration
  - software-development
  - ci-cd-issues
aliases_ja:
  - Ghostty
  - GitHub障害
  - Mitchell Hashimoto
  - ミッチェル・ハシモト
  - GitHubから移行
  - 開発効率低下
  - マージキューバグ
  - Elasticsearch過負荷
  - エージェント開発ワークフロー
  - 慢性的な障害
  - 開発プラットフォーム
published_at: ""
source_urls:
  - https://mitchellh.com/writing/ghostty-leaving-github
summary: >
  Ghostty開発者のMitchell Hashimoto（GitHub歴18年以上）が、GitHubの慢性的な障害による開発効率低下を理由に移行を決定。直近の大規模障害（マージキューバグで658リポジトリ影響、Elasticsearch過負荷）と、エージェント開発ワークフローの急激な成長（30倍拡張）が引き金となった。
created_at: "2026-04-30 20:41"
updated_at: "2026-04-30 20:41"
---

# Ghostty Is Leaving GitHub

Ghosttyの開発者であるMitchell Hashimoto（GitHubユーザーID 1299、18年以上の初期ユーザー）が、GitHubの慢性的な障害による開発効率低下を理由に、同プラットフォームからの移行を決定した。

## 移行の理由

移行の直接的な引き金となったのは、直近に発生した2つの大規模障害である：

1. **マージキューバグ**: 658のリポジトリに影響を与えた障害
2. **Elasticsearch過負荷**: 検索機能が完全に停止した障害

GitHubのCTOは、これらの問題の原因として「エージェント開発ワークフローの急激な成長」を挙げ、同ワークフローが30倍に拡張する計画があることを説明した。

## 開発者の判断

Mitchell Hashimotoの判断について、記事では「イデオロギーでも反感でもなく、純粋に『壊れているから離れる』という判断の静けさ」が特徴的だと評されている。

移行先のプラットフォームについては、現時点では未発表となっている。

## 技術的含意

GitHubのCTOが言及した「エージェント開発ワークフローが30倍成長した」という状況は、AI開発の急激な拡大がインフラに与える影響を示す象徴的な事例として注目されている。

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[ai-infrastructure-supply-chain-constraints]]
- [[microsoft-azure-infrastructure-failure]]
- [[github-reliability-issues]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[ai-development-eight-years-three-months]]
- [[claude-code-cli-computer-use-implementation]]
- [[open-source-does-not-imply-open-community]]
<!-- /AUTO:Related Articles -->
