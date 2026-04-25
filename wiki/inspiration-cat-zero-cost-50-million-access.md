---
article_id: inspiration-cat-zero-cost-50-million-access
title: "キュピーン猫画像メーカー初日50万アクセスもサーバ代「0円」その秘密"
type: source
source_ids:
  - 36cdc2de5940
topics:
  - web-application-architecture
  - serverless-computing
  - ai-background-removal
  - cloudflare-pages
  - client-side-processing
aliases_ja:
  - キュピーン猫画像メーカー
  - サーバーレス
  - クライアントサイド処理
  - Cloudflare Pages
  - ONNX Runtime Web
  - AI背景除去
  - でんでんきき
  - バズったサービス
  - ゼロ円運用
  - WebGPU
published_at: "2026-04-09"
source_urls:
  - https://www.itmedia.co.jp/news/articles/2604/09/news108.html
summary: >
  猫などの写真に「ひらめき」エフェクトを追加するWebアプリ「InspirationCat」が初日50万アクセスを記録しながらサーバ代0円を実現。
  ONNX Runtime WebとCloudflare Pagesを活用したクライアントサイド処理により、背景除去AIをブラウザで直接実行する設計が鍵となっている。
created_at: "2026-04-09 19:38"
updated_at: "2026-04-09 19:38"
---

# キュピーン猫画像メーカー初日50万アクセスもサーバ代「0円」その秘密

猫などの動物写真に「ひらめき」エフェクトを追加するWebアプリ「InspirationCat」が、公開初日に50万アクセスを記録する大ヒットサービスとなった。しかし、大量アクセスにも関わらずサーバ代は「0円」という驚異的なコスト効率を実現している。

## サービス概要とバズの背景

「InspirationCat」は、動物の写真をアップロードするとAIで背景を自動除去し、電球マークやキラキラエフェクトを重ねて「キュピーン」画像に編集・ダウンロードできるサービス。開発者の でんでんきき（@nya3_neko2）氏によると、バズったサービスにも関わらずサーバ代は実際に0円だったという。

サービスは、人気の「キュピーン」画像を投稿していた「ぬこまる（5）」（@neko_muchamaru）氏からの内容使用許可を得て開発されたとしている。

## ゼロ円運用を可能にした技術アーキテクチャ

### クライアントサイド処理による負荷分散

通常、背景除去処理には本格的なサーバとGPUを搭載したAIモデルが必要となる。しかし「InspirationCat」では、背景除去ライブラリ「@imgly/background-removal」を使用し「ONNX Runtime Web」を活用することで、サーバではなくユーザーの端末で直接処理を実行している。

ONNX Runtime Webは、AI用の計算をブラウザ上でWebAssemblyとWebGPUで処理するランタイムである。初回アクセス時に約40MBのAIモデルをダウンロード・キャッシュする仕組みにより、2回目以降は高速に処理が開始される。

### モバイル対応とパフォーマンス最適化

スマートフォンのメモリが不足する場合は、処理する画像サイズを1024px、768px、512pxと段階的に縮小することで軽量化を実現している。

## シンプルな構成による開発効率

アプリの構成も極めてシンプルに設計されている。フロントエンドビルドツール「Vite」とTypeScriptで静的ファイルを作成し、無料ホスティングサービス「Cloudflare Pages」に配置。Reactなどのフレームワークを使わず、バニラTypeScriptとCanvas APIによるシンプルな構成としている。

## Cloudflare Pagesの無料枠活用

Cloudflare Pagesは帯域制限が緩い無料枠のため、50万アクセスで発生した約1TBの転送量も無料で処理できた。開発者の計算によると、通常規模のアクセスを他のホスティングサービス「Vercel」で運用した場合、月5万4000円の費用になっていたという。

### データ転送量の最適化

各テンプレートの背景画像をWebP（約80KB）で配信し、非対応ブラウザではPNG（5.6MB）にフォールバックしている。50万ユーザー全員がPNGで配信された場合、背景画像だけで2.8TBになるが、WebPなら40GBに縮小できる。これは「ユーザーの読み込み速度にも配慮した」仕組みだとしている。

## プライバシーとセキュリティ配慮

画像をサーバに保存しない設計のため、EXIF情報に含まれるGPS座標や写真撮影時の個人情報が第三者に送信されることはない。個人情報の管理やセキュリティ、ストレージの心配もすべて不要になった。

## コスト比較：サーバサイド処理との差

仮にサーバサイドで背景除去を実行する設計だった場合、50万アクセスのうち20万枚の画像処理を行うとして、AWS Lambda + S3で1ヶ月あたり1万7000円の費用が発生していたと開発者は試算している。

## まとめ

開発者は今回の成功要因を以下の3点にまとめている：

1. **サーバの計算コスト削減**：クライアントサイド処理
2. **画像をサーバに保存しない**：プライバシー保護と運用負荷軽減  
3. **Cloudflare Pagesへのデプロイ**：無料枠での大量アクセス対応

これにより「バズっても課金されない、炎上しない」サービスを実現したとしている。

## Related Articles

[[ai-background-removal-technology]]
[[serverless-web-applications]]  
[[cloudflare-pages-hosting]]
[[client-side-ai-processing]]
