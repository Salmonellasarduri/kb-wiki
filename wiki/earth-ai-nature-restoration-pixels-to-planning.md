---
article_id: earth-ai-nature-restoration-pixels-to-planning
title: "From Pixels to Planning: Earth AI for Nature Restoration"
type: source
source_ids:
  - 90e26558a58c
  - d69641867659
topics:
  - ai-environmental-applications
  - nature-restoration
  - satellite-imagery-analysis
  - climate-sustainability
  - remote-sensing-ai
aliases_ja:
  - アース AI
  - 自然再生 AI
  - 衛星画像解析
  - ピクセルから計画へ
  - 生態系回復
  - 気候変動対策 AI
  - リモートセンシング
  - 環境 AI
  - グーグルリサーチ 自然
  - 生態学的損失の可視化
  - ビジョントランスフォーマー 衛星
  - アルファアース
  - MapBiomas
  - ラスターからベクターへ
  - カーボンアカウンティング AI
  - ファームスケープス
  - 景観計画 AI
  - 衛星埋め込みベクトル
published_at: ""
source_urls:
  - https://research.google/blog/from-pixels-to-planning-earth-ai-for-nature-restoration
summary: >
  Google Researchのブログ記事で、AIシステムが衛星画像などのピクセルレベルデータを解析し、
  自然再生の計画立案を支援する「Earth AI」パイプラインが紹介されている。具体的には、
  3億枚以上の衛星画像で事前学習されたVision Transformerモデルが生け垣や小規模林など
  細粒度の特徴をラスターマップとして検出し（Farmscapes 2020）、それをポリゴン単位の
  インベントリにベクタライズすることでカーボンアカウンティングや景観計画を可能にする。
  また、AlphaEarth Foundationsが生成する64次元の衛星埋め込みベクトルはMapBiomas等の
  プラットフォームで活用される。気候変動・サステナビリティの文脈に位置づけられており、
  ピクセルが「生態学的損失の目撃者」であると同時に「設計者」でもあるという両義的役割への
  哲学的考察も含まれている。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# From Pixels to Planning: Earth AI for Nature Restoration

## 概要

Google Research（グーグル・リサーチ）が公開したブログ記事で、「Earth AI」パイプラインと呼ばれるシステムが衛星画像をピクセル単位で解析し、自然再生の計画立案を支援する取り組みを論じている。この取り組みは気候変動対策およびサステナビリティの文脈で位置づけられている。

## Earth AI パイプラインの構成

Earth AIは衛星画像を自然再生計画へと変換するまでに、主に3つのステージを経る。

### ステージ1：Vision Transformerによる特徴検出

3億枚（300M枚）以上の衛星画像で事前学習されたVision Transformer（ビジョントランスフォーマー）モデルが、生け垣（hedgerows）や小規模林（small woodlands）といった細粒度の地物をラスターマップとして検出する。このデータセットは **Farmscapes 2020** として参照されている。

### ステージ2：ラスターからベクターへの変換

検出されたラスターマップはポリゴン単位のインベントリへとベクタライズされる。このステップにより、地物が単なるピクセルの集合から「境界を持つ実体」へと昇格し、カーボンアカウンティング（炭素会計）や景観計画（landscape planning）への実用的な活用が可能になる。

### ステージ3：AlphaEarth Foundationsによる埋め込みベクトル生成

**AlphaEarth Foundations**（アルファアース・ファウンデーションズ）は64次元の衛星埋め込みベクトル（satellite embedding vectors）を生成する。これらのベクトルは **MapBiomas** などのプラットフォームで利用されており、広域の土地利用・生態系分析に貢献している。

## 哲学的考察

ブログには短い省察（Reflection）が添えられており、ラスターからベクターへの変換ステップに着目したうえで次のように述べられている。

> ピクセルが境界となり、境界が義務となる。損失を目撃したのと同じグリッドが、今度はそれを取り戻すための足場となっている。そこには一種の構造的記憶がある。

「かつて野生だったものを記録するためにAIの基盤となるグリッドが使われる」という奇妙な対称性、そしてピクセルが「生態学的損失の目撃者」であると同時に「設計者」でもあるという両義的な役割が指摘されており、技術と自然の関係性についての問いを含んでいる。

---

> [!note] 本記事は複数のソースを統合しています。詳細な技術仕様については原典ブログを参照してください。

## Related Articles

- [[英ケンブリッジ大学、AIが設計したワクチンの臨床試験に成功 未知の変異株にも備える万能型]] — AIを科学・生命科学に応用する隣接事例
- [[Google Research at I/O 2026での発表内容まとめ]] — Google Researchの関連発表
- [[Google Research科学者によるEmpirical Research Assistance活用の4つの方法]] — Google ResearchにおけるAI支援研究の事例