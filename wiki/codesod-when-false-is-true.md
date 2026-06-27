---
article_id: codesod-when-false-is-true
title: "CodeSOD: When False is True"
type: stub
source_ids:
  - 5d28755f1d17
topics:
  - ruby-on-rails
  - dry-run-flag
  - boolean-evaluation-bug
  - software-safety-flags
  - api-integration-bugs
aliases_ja:
  - フォルスがトゥルーになる
  - ドライランフラグ
  - Rubyオンレールズ
  - 安全フラグの誤動作
  - dry_run バグ
  - 変更が適用されてしまった
  - FalseがTrueと評価される
  - APIインテグレーションバグ
published_at: ""
source_urls:
  - https://thedailywtf.com/articles/when-false-is-true
summary: >
  開発者Lillithが Ruby on Rails APIに新しいツールを統合した際、dry_runフラグが
  FalseをTrueとして評価してしまうバグが発生した。これにより「変更を適用しない」
  という安全保証が破られた事例として報告されている。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# CodeSOD: When False is True

## 概要

The Daily WTFのCodeSODシリーズに掲載された事例。開発者Lillith（リリス）がRuby on Rails（ルビー・オン・レールズ）製のAPIに新しいツールを統合した際に発生したバグについて報告している。

## 何が起きたか

問題の核心は `dry_run` フラグの扱いにある。新たに統合したツールがこのフラグを送信する際、**False（偽）がTrue（真）として評価される**という挙動を引き起こした。

`dry_run` フラグは「変更を実際には適用しない」ことを保証するための安全機構であるが、この誤った評価により、その保証が破られた。

## 教訓

この事例はThe Daily WTFの「Reflection（振り返り）」として次のように総括されている：

> 「発火する安全フラグ。『これは何もしない』というのは、結局最も信頼できない約束だった。」

安全のために存在するはずのフラグが、むしろ危険な動作を引き起こすという逆説的な状況を示している。

---

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[ai-agent-bankrupted-operator-dn42]] — AIエージェントが意図しない実行を行った別の事例
- [[bunnyCDN-silent-file-loss]] — 通知なしに本番環境が壊れていた別のインフラ信頼性事例
