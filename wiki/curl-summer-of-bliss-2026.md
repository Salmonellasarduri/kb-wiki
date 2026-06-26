---
article_id: curl-summer-of-bliss-2026
title: "curl Summer of Bliss：LLM偽レポート問題によるHackerOne報告受付停止"
type: stub
source_ids:
  - f33648999939
topics:
  - open-source-security
  - llm-noise-problem
  - vulnerability-reporting
  - oss-maintainer-burnout
  - hackerone-policy
aliases_ja:
  - curl夏の休息
  - サマーオブブリス
  - ダニエル・スタンバーグ
  - LLM偽レポート
  - HackerOne停止
  - OSSメンテナー疲弊
  - 脆弱性報告ノイズ
  - curlセキュリティ
  - バグレポートスパム
published_at: "2026-06-15"
source_urls:
  - https://daniel.haxx.se/blog/2026/06/15/curl-summer-of-bliss
summary: >
  curlの開発者Daniel Stenbergが2026年7月1日〜8月3日の約1か月間、HackerOne経由の脆弱性報告を完全に受け付けない「Summer of Bliss」を宣言した。
  背景にはLLM（大規模言語モデル）が生成した偽レポートの大量流入によるチームの疲弊があり、curl 8.22.0のリリースも2週間延期される。
  他のOSSプロジェクトにも同様の休止を呼びかけている。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# curl Summer of Bliss：LLM偽レポート問題によるHackerOne報告受付停止

## 概要

あらゆるデータ転送の基盤として広く使われているコマンドラインツール **curl** の開発者 **Daniel Stenberg**（ダニエル・スタンバーグ）が、2026年7月1日から8月3日までの約1か月間を「**Summer of Bliss（夏の至福）**」と名付け、HackerOne経由の脆弱性報告を完全に受け付けない方針を宣言した。

## 背景：LLM生成レポートの大量流入

この決断の直接的な原因は、LLM（Large Language Model）が自動生成した偽の脆弱性レポートが大量にHackerOneへ流入し、開発チームが疲弊しきっている状況にある。本来はセキュリティ向上を目的とした報告チャネルが、AI生成ノイズによって機能不全に陥っている。

## 影響

- **curl 8.22.0** のリリースが2週間延期される
- 休止期間中はHackerOne経由の新規脆弱性報告を受け付けない
- 他のOSSプロジェクトにも同様の一時停止を呼びかけている

## 意義

「bliss（至福）」という言葉を選んで守りに入るという行為は、単純な拒絶ではなく、静かな意志の表明として捉えられている。LLMが生み出すノイズが、インターネットインフラの根幹を担うツールの開発者を追い詰めているという構図は、AI生成コンテンツがOSSエコシステムに与える実害を具体的に示す事例となっている。

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[project-glasswing-anthropic-security]] — AIを活用した脆弱性検出の取り組み（[[Mythos finds a curl vulnerability]]も参照）
- [[mythos-finds-curl-vulnerability]] — AIセキュリティツールMythosがcURLに報告した脆弱性（誤検知を含む）事例