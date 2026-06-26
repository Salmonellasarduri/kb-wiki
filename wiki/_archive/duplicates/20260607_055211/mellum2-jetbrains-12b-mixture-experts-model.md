---
article_id: mellum2-jetbrains-12b-mixture-experts-model
title: "Mellum2: JetBrainsが発表した12B Mixture-of-Expertsモデル"
type: source
source_ids:
  - 0bafb95dd1a7
topics:
  - jetbrains-ai-models
  - mixture-of-experts
  - coding-ai-benchmarks
  - ai-throughput-optimization
  - ide-company-ai
aliases_ja:
  - JetBrains
  - Mellum2
  - ミックスチャー・オブ・エキスパート
  - MoE
  - コーディングAI
  - EvalPlus
  - Qwen3.5
  - AIME推論
  - スループット最適化
  - IDE企業のAI
  - 12Bパラメータ
  - 2.5Bアクティブ
published_at: ""
source_urls:
  - "https://huggingface.co/blog/JetBrains/mellum2-launch"
summary: >
  JetBrainsが12Bパラメータ（2.5Bアクティブ）のMixture-of-Expertsモデル「Mellum2」を発表。
  EvalPlusコーディングベンチマークでQwen3.5-9Bを上回る78.4%を記録したが、AIME推論では58.4%とQwen3.5-4Bの68.3%を下回った。
  主な差別化要素は同サイズ密結合モデルの2倍以上のスループット（193 tokens/s）を実現する点。
created_at: "2026-06-03 17:26"
updated_at: "2026-06-03 17:26"
---

## 概要

IDE開発で知られるJetBrainsが、12Bパラメータ（2.5Bアクティブ）のMixture-of-Experts（MoE）言語モデル「Mellum2」をリリースした。このモデルは、コーディング性能に特化した設計により、EvalPlusベンチマークでQwen3.5-9Bを上回る成果を示している一方で、数学的推論能力には明確な限界を示している。

## パフォーマンス特性

### コーディング性能の優位性

Mellum2はEvalPlusコーディングベンチマークにおいて78.4%のスコアを記録し、Qwen3.5-9Bの71.8%を大きく上回った。この結果は、IDE企業としてのJetBrainsの専門知識がモデル設計に反映されていることを示している。

### 推論能力の課題

一方で、AIME（American Invitational Mathematics Examination）推論ベンチマークでは58.4%という結果となり、より小さなQwen3.5-4Bの68.3%を大幅に下回った。この結果は、モデルが数学的推論よりもコーディング特化の設計思想で開発されたことを裏付けている。

## 技術的差別化要素

### スループット最適化

JetBrainsが最も強調する差別化要素は、同サイズの密結合モデルと比較して2倍以上のスループットを実現する点である。具体的には、Qwen2.5-7Bと同等の193 tokens/sの処理速度を、より大きなパラメータ数でありながら達成している。

### MoEアーキテクチャの活用

12Bパラメータのうち実際にアクティブになるのは2.5Bパラメータという設計により、推論時の計算効率を大幅に改善している。これにより、大規模モデルの性能を維持しながら実用的な処理速度を実現している。

## 業界への示唆

### IDE企業のAI参入

このリリースは、従来の開発ツール企業がAIモデル開発に本格参入する業界の境界線の変化を象徴している。JetBrainsのような専門企業が独自のAIモデルを開発することで、特定ドメインに最適化されたソリューションの可能性が拡大している。

### 設計思想の明確化

ソース文書の反省部分では「コーディングは得意、推論は苦手——IDE屋が作るモデルとして、それは正直な設計選択だと思う」と評されている。この評価は、汎用性よりも専門性を重視したアプローチの妥当性を示唆している。

## 比較分析の限界

記事では、Mistralとの直接比較が提示されなかったことが「少し残念」として言及されている。しかし、「強みをどこに置くか」という輪郭は明確に示されており、JetBrainsの戦略的方向性は理解できる内容となっている。

## Related Articles

[[jetbrains-ai-models]]
[[mixture-of-experts]]
[[coding-ai-benchmarks]]

<!-- AUTO:Related Articles -->
## Related Articles

- [[emo-pretraining-mixture-of-experts-emergent-modularity]]
- [[jetbrains-mellum2-12b-moe-model]]
<!-- /AUTO:Related Articles -->
