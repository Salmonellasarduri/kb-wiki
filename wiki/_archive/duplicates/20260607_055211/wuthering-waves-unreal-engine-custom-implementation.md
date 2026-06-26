---
article_id: wuthering-waves-unreal-engine-custom-implementation
title: 『鳴潮』のUnreal Engine技術解析 - UE4ベースでUE5機能を実装する"変態的"手法
type: source
source_ids:
  - 2eab761a5fa5
topics:
  - game-engine-technology
  - mobile-game-development
  - unreal-engine-customization
  - technical-implementation
  - chinese-game-industry
aliases_ja:
  - 鳴潮
  - ウェザリングウェイブス
  - Unreal Engine
  - UE4
  - UE5
  - ゲームエンジン技術
  - モバイルゲーム開発
  - 中村匡彦
  - Indie-us Games
  - KURO GAMES
  - レイトレーシング
  - Lumen
  - トゥーンシェーディング
  - アニメ調グラフィック
published_at: "2026-04-03"
source_urls:
  - https://automaton-media.com/articles/columnjp/wwu-20260403-434345/
summary: >
  『鳴潮』は、UE4ベースでありながらUE5のLumen技術を独自移植し、レイトレーシングやトゥーンシェーディングを組み合わせたリッチなグラフィックを実現している。
  専門家によると、Epic Gamesのサポートなしで独自エンジン並みの大規模カスタマイズを行っており、技術的に「変態的」な実装手法として評価されている。
created_at: "2026-04-05"
updated_at: "2026-04-05"
---

## 概要

KURO GAMESが開発する『鳴潮』（Wuthering Waves）について、Unreal Engine専門家のIndie-us Games代表・中村匡彦氏による技術解析が行われた。同作はUE4をベースとしながら、UE5の最新機能を独自移植することで、モバイルゲームとしては異例のリッチなグラフィックを実現している。

## 技術的特徴

### UE5技術のUE4への移植

『鳴潮』の最大の技術的特徴は、UE4.26をベースとしながら、UE5のLumen（グローバルイルミネーション技術）を独自移植していることである。通常、異なるバージョン間での機能移植は技術的に困難とされているが、開発チームはハードウェアレイトレーシング版のLumenを実装することに成功している。

さらに、Lumenには本来存在しないキャラクター向けのトゥーンシェーディングも独自開発し、アニメ調キャラクターがリアルな背景に自然に融合するよう調整されている。

### グラフィック表現の特徴

- **アニメ調と写実的背景の融合**: 従来の単純なアニメ調表現を超えた、多彩で表現力豊かなキャラクター描写
- **PCゲーム品質の背景**: UE5世代のゲームに匹敵するリッチな環境表現
- **モバイル対応**: 高品質グラフィックを維持しながらモバイル端末での動作を実現

## 開発における課題と制約

### UE5への移行が困難な理由

中村氏の分析によると、『鳴潮』がUE5に移行できない理由は以下の通り：

1. **段階的アップデートの必要性**: UE4.26から最新のUE5.7まで、一つずつバージョンを上げる必要がある
2. **運営コストの問題**: 全バージョンアップに1年以上かかる可能性があり、運営型ゲームには現実的でない
3. **大規模カスタマイズによる複雑性**: 既存の改造部分を全て新バージョンに対応させる必要がある

### Epic Gamesサポートの喪失

独自カスタマイズを進めた結果、Epic Gamesからの公式サポートを受けられない状況となっている。これは実質的に「独自エンジンでゲームを作るのとほとんど変わらないコスト」が発生することを意味する。

特に、PS5やモバイルなど複数プラットフォームへの対応では、コンソール特有の技術的課題を自社のみで解決する必要があり、相当なコアスキルを持ったスタッフが必要とされる。

## モバイルゲーム開発におけるUnreal Engineの位置づけ

### UnityとUEの技術的差異

中村氏によると、技術的な観点ではUnityがUEより優秀ということはない。Unityがモバイルゲーム開発で多用される理由は：

- **情報量とコミュニティ**: モバイル向けの情報やサポートが豊富
- **サードパーティライブラリ**: モバイル開発用のフレームワークが充実
- **開発者の慣れ**: 過去の成功事例による安心感

一方、UEは技術的な強みはあるものの、モバイル向けの情報やサポートツールが相対的に少ないため、『鳴潮』のような高度な実装には専門性の高い技術チームが必要となる。

## 業界への影響

『鳴潮』の技術実装は、「UEを使ったアニメ調グラフィックを採用したゲームとして、モバイルゲームとしてもPCゲームとしてもトップランナー」として評価されている。この成功は、中国のゲーム開発技術の高さを示すとともに、ゲームエンジンの可能性を押し広げる事例として注目されている。

## Related Articles

- [[claude-code-cli-computer-use-implementation]] - AI自動化技術の進歩
- [[japanese-llm-performance-breakthrough]] - 日本の技術開発における独自性

<!-- AUTO:Related Articles -->
## Related Articles

- [[wuthering-waves-unreal-engine-customization-analysis]]
- [[wuthering-waves-unreal-engine-technical-analysis]]
<!-- /AUTO:Related Articles -->
