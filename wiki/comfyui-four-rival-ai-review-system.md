---
article_id: comfyui-four-rival-ai-review-system
title: "ComfyUIがOpenAI・Anthropic・Google・MoonshotのAIを競わせてプルリクをレビューする仕組みを公開"
type: stub
source_ids:
  - 452bf0bfef2f
topics:
  - ai-code-review
  - multi-ai-systems
  - cursor-review
aliases_ja:
  - ComfyUI
  - Cursor Review
  - AIコードレビュー
  - プルリクエスト
  - 複数AIモデル競合
  - OpenAI
  - Anthropic
  - Google
  - Moonshot
  - 統合判定システム
published_at: "2026-06-10"
source_urls:
  - https://gigazine.net/news/20260610-comfyui-four-rival-review
summary: >
  ComfyUIの開発チームが「Cursor Review」システムを公開し、OpenAI・Anthropic・Google・Moonshotの4つのAIモデルに同じプルリクエストを異なる観点からレビューさせ、最終的に1つの判定モデルが結果を統合してGitHubに投稿する仕組みを構築した。
created_at: "2026-06-11 01:32"
updated_at: "2026-06-11 01:32"
---

ComfyUIの開発チームが新しいAIコードレビューシステム「Cursor Review」を公開した。このシステムは複数のAI企業のモデルを同時活用する革新的なアプローチを採用している。

## システムの概要

Cursor Reviewは以下の4つの主要AIプラットフォームのモデルを活用する：

- OpenAI
- Anthropic
- Google
- Moonshot

これらの各モデルは同じプルリクエスト（PR）に対して異なる観点からレビューを実施する。各AIが独自の視点で分析を行った後、最終的に1つの統合判定モデルがすべての結果を統合し、GitHubに最終的なレビューコメントを投稿する仕組みとなっている。

## 技術的アプローチ

このシステムは、単一のAIモデルに依存するのではなく、複数の異なるAIの知見を組み合わせることで、より包括的で精度の高いコードレビューを実現することを目指している。各AIモデルが持つ異なる強みや視点を活用し、それらを統合することで、従来の単一モデルベースのレビューシステムを上回る品質を提供しようとしている。

## Related Articles

[[ai-code-review]]
[[multi-agent-frameworks]]

> [!note] ソースが限定的です。記事は不完全な可能性があります。

<!-- AUTO:Related Articles -->
## Related Articles

- [[claude-simplify-code-refactoring-experiment]]
<!-- /AUTO:Related Articles -->
