---
article_id: junkyard-computing-retired-phones-low-carbon-platform
title: "Junkyard Computing：退役スマートフォンを低炭素コンピューティング基盤に転用する研究"
type: stub
source_ids:
  - 49b2e682bb47
topics:
  - sustainable-computing
  - carbon-footprint-reduction
  - hardware-reuse
  - green-computing
  - embodied-carbon
aliases_ja:
  - ジャンクヤードコンピューティング
  - 再利用スマホクラスタ
  - 炭素集約度
  - 体化炭素
  - 低炭素コンピュート
  - 退役スマートフォン転用
  - CCI指標
  - Pixel 2000台クラスタ
  - GoogleとUCSD共同研究
  - ASPLOS 2023
published_at: ""
source_urls:
  - https://research.google/blog/a-low-carbon-computing-platform-from-your-retired-phones
summary: >
  退役スマートフォンをコンピュートノードとして再利用する場合、製造炭素コスト（C_M）がゼロとみなせるため、
  新品サーバと比較して炭素集約度（CCI）が大幅に低くなる。GoogleとUCSDは2026年にPixel 2,000台の
  マザーボードをクラスタ化し、ASPLOS 2023の「Junkyard Computing」論文がほぼ全ベンチマークで
  再利用スマホの優位性を定量的に示した。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# Junkyard Computing：退役スマートフォンを低炭素コンピューティング基盤に転用する研究

## 概要

GoogleとUCSD（カリフォルニア大学サンディエゴ校）が共同で、役割を終えたスマートフォンをコンピュートノードとして再利用するアプローチ「Junkyard Computing」を研究・実装した。この概念はASPLOS 2023で発表された論文にて定量的に分析されている。

## 炭素集約度（CCI）の優位性

コンピューティングシステムの炭素効率を評価する指標として**炭素集約度（CCI: Carbon Cost Intensity）**が用いられる。新品サーバを導入する場合、製造段階で発生する炭素コスト（C_M：製造炭素コスト）が指標に大きく影響する。

一方、退役スマートフォンを転用する場合、製造炭素コスト（C_M）はすでに消費済みのものとみなされるため**ゼロ**として計上できる。これにより、再利用スマホのCCIは新品サーバと比較して大幅に低くなる。ASPLOS 2023の「Junkyard Computing」論文では、ほぼ全ベンチマークにおいて再利用スマートフォンが優位であることが示された。

## GoogleとUCSDによる実装

2026年にGoogleとUCSDは、実際にGoogle Pixel 2,000台のマザーボードをクラスタ化した実装を公開した。内部評価では、**マザーボードが体化炭素（embodied carbon）の約50%を占める**ことも明らかにされている。

## 意義

役割を終えた機器が「製造コストゼロの炭素資源」として演算し続けるという構図は、廃棄と再生の境界を曖昧にする新たな視点を提示している。「最もクリーンなコンピュート」は、新しいハードウェアを製造するのではなく、すでに存在するものを使い続けることによって実現されうる。

---

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[AIデータセンター建設計画の半数が変圧器・バッテリー不足で延期・中止へ]] — AIインフラ拡大とその物理的・環境的制約
- [[サンガブリエルバレーのデータセンター建設阻止運動]] — データセンターが地域社会に外部化するコスト
- [[Texas grid flags risks as data centers, crypto sites fail voltage tests]] — データセンターの電力インフラへの影響