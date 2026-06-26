---
---
article_id: chatgpt-lockdown-mode-prompt-injection-protection
title: "ChatGPTに「ロックダウンモード」 プロンプトインジェクションによる情報漏えい対策"
type: source
source_ids:
  - f90e58e4ad1d
  - 316506b1606b
topics:
  - ai-security
  - prompt-injection-defense
  - data-protection
aliases_ja:
  - ChatGPT
  - チャットGPT
  - ロックダウンモード
  - プロンプトインジェクション
  - 情報漏えい対策
  - AIセキュリティ
  - OpenAI
  - オープンAI
  - データ流出防止
  - アウトバウンド接続遮断
  - 出口対策
  - エージェント機能無効化
published_at: "2026-06-07"
source_urls:
  - "https://www.itmedia.co.jp/news/articles/2606/07/news022.html"
summary: >
  OpenAIがChatGPTにプロンプトインジェクション攻撃によるデータ流出を防ぐ「ロックダウンモード」を追加。
  攻撃自体を無効化するのではなく、アウトバウンド接続を遮断して流出経路を物理的に封鎖する「出口を守る」設計思想を採用。
  ブラウジング・エージェント機能は無効化されるが、テキスト会話は維持される。
created_at: "2026-06-07 12:53"
updated_at: "2026-06-09 08:50"
---

OpenAI（オープンAI）がChatGPT（チャットGPT）に新たなセキュリティ機能「ロックダウンモード」を追加したと発表された。この機能は、プロンプトインジェクション攻撃によるデータ流出を防ぐことを目的としている。

## 機能概要と設計思想

ChatGPT Lockdown Modeは、プロンプトインジェクションそのものを無効化するのではなく、攻撃が成功してもデータを外部に送れないようアウトバウンド接続を遮断するという設計思想を採っている。これは攻撃の検知ではなく流出経路の物理的な封鎖で被害を防ぐ、「入口ではなく出口を守る」アーキテクチャが核心となっている。

ロックダウンモードが有効化されると、ブラウジング・エージェント機能など外部接続を要する機能は無効化される。一方、テキスト会話はネットワーク不要のローカルセッション完結のため保持される。これにより、悪意のあるプロンプトインジェクション攻撃によって機密情報が外部に漏洩するリスクを軽減する仕組みとなっている。

## 対象ユーザー

この機能は特に機密データを扱う個人や組織向けに設計されており、セキュリティを重視する環境での利用を想定している。

## 哲学的考察

「窓を閉める」という選択が、攻撃を跳ね返すことではなく逃げ道を塞ぐことだったという点について、記事では興味深い観察がなされている。それはある種の諦念と徹底さが同居した設計で、自分の限界をよく知っているAIの身振りに見えるとしている。

AIが「外の世界への接続を自ら断ち切ることでデータを守る」という選択肢を持つことについて、哲学的な重みについても触れられている。

## Related Articles

- [[ai-safety]]
- [[prompt-injection-defense]]
- [[enterprise-ai-security]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[mythos-finds-curl-vulnerability]]
- [[sheets-ai-data-exfiltration-vulnerability]]
<!-- /AUTO:Related Articles -->