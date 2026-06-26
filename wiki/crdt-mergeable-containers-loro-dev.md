---
article_id: crdt-mergeable-containers-loro-dev
title: "CRDTs merge concurrent edits. Why not concurrent creation?"
type: stub
source_ids:
  - 42dbd810183d
topics:
  - crdt-technology
  - concurrent-editing
  - mergeable-containers
  - distributed-systems
aliases_ja:
  - CRDT技術
  - 並行編集
  - マージ可能コンテナ
  - 分散システム
  - Loro.dev
  - コンカレント作成
  - 編集マージ
  - 同時編集
published_at: ""
source_urls:
  - https://loro.dev/blog/mergeable-containers
summary: >
  CRDTは並行編集をマージできるが、Loro.devの記事では並行「作成」にも同じアプローチが適用できるかを問いかけている。
  編集と創造を別物として扱う人間の先入観を見直し、生成そのものをコンフリクト解消の問題として捉える新しい視点を提示。
created_at: "2026-06-09 15:49"
updated_at: "2026-06-09 15:49"
---

CRDTは並行編集をマージできるが、Loro.devによるマージ可能なコンテナの設計に関する記事では、並行な「作成」にも同じアプローチが適用できるかという問いが提起されている。

## 編集と創造の境界を問い直す

記事では、編集と創造を別物として扱っていたのは人間の先入観かもしれないという考察が含まれている。生成そのものをコンフリクト解消の問題として見る視点は、従来の分散システム設計における固定観念を揺さぶる新たなアプローチとして注目される。

## Loro.devのマージ可能コンテナ設計

Loro.devは、CRDTの基本概念である並行編集のマージ機能を、作成プロセス自体に拡張することで、より包括的な分散協調システムの構築を目指している。この視点転換により、分散環境での協調作業における新たな可能性が開かれる。

> [!note] ソースが限定的です。記事は不完全な可能性があります。
