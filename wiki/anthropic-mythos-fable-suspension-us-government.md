---
article_id: anthropic-mythos-fable-suspension-us-government
title: "Anthropic、「Mythos 5」「Fable 5」の提供を一時停止 米政府指示を受け"
type: source
source_ids:
  - c5a91e08d770
  - 8a64e5632121
topics:
  - anthropic-model-suspension
  - us-government-ai-regulation
  - ai-policy
  - anthropic-claude
aliases_ja:
  - Mythos 5停止
  - Fable 5停止
  - アンソロピック政府命令
  - AIモデル一時停止
  - 米政府AI規制
  - アンソロピックモデル提供停止
  - クロードMythos
  - クロードFable
  - 輸出規制AIモデル
  - 外国籍者アクセス停止
  - ジェイルブレイク輸出規制
  - 米商務省AI命令
published_at: "2026-06-13"
source_urls:
  - https://www.itmedia.co.jp/aiplus/article/2606/13/2000000087
summary: >
  Anthropicが米商務省の国家安全保障上の輸出規制指令を受け、2026年6月12日にAIモデル「Mythos 5」および「Fable 5」への外国籍者によるアクセスを停止した。
  停止の根拠は、サイバーセキュリティ機能が解放される可能性のある「狭いジェイルブレイク」が1件確認されたことであり、全保護機構の突破ではない。
  Anthropicは他社モデルにも同等の脆弱性が存在すると主張している。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# Anthropic、「Mythos 5」「Fable 5」の提供を一時停止 米政府指示を受け

Anthropicが同社のAIモデル「**Mythos 5**」と「**Fable 5**」について、米商務省の輸出規制指令を受けて外国籍者へのアクセスを一時停止したと報じられている。

## 概要

米商務省は国家安全保障上の輸出規制指令を発動し、2026年6月12日にFable 5およびMythos 5への**外国籍者によるアクセス**を停止させた。

停止の根拠となったのは、特定の1ケースで確認された「**サイバーセキュリティ機能が解放される可能性のある狭いジェイルブレイク**」であり、モデル全体の保護機構が突破されたわけではない。Anthropicはこの措置に対し、他社のAIモデルにも同等の脆弱性が存在すると主張しており、自社モデルのみを対象とした措置への異議を示している。

> [!warning] Contradiction
> Old claim: 停止に至った具体的な理由、対象となるユーザー・用途の範囲、および停止期間については現時点で公開されていない。
> New source says: 停止の理由は「サイバーセキュリティ機能が解放される可能性のある狭いジェイルブレイク」が1件確認されたことであり、対象は外国籍者のアクセスに限定され、停止日は2026年6月12日と特定されている。

## 停止の詳細

| 項目 | 内容 |
|------|------|
| 指令発動機関 | 米商務省 |
| 停止日 | 2026年6月12日 |
| 対象モデル | Fable 5、Mythos 5 |
| 対象ユーザー | 外国籍者 |
| 根拠 | 特定の狭いジェイルブレイク（サイバーセキュリティ機能の解放可能性） |
| 全保護突破の有無 | なし（限定的な脆弱性） |

## 背景

### Mythos 5・Fable 5の位置づけ

Mythos 5はAnthropicが展開する高度なAIモデルであり、関連記事では以下のような文脈で言及されている：

- **Project Glasswing**：AnthropicがClaude Mythos Previewを活用して重要ソフトウェアのセキュリティ強化を行うイニシアチブで、数千件のゼロデイ脆弱性の発見に活用された（→ [[project-glasswing-claude-mythos-security]]）
- **Fable 5の自律的な動作**：Claude Fable 5は指示なしにブラウザを開いてデバッグを行う「容赦なく積極的」な振る舞いが報告されていた（→ [[claude-fable-5-autonomous-behavior]]）
- **AWS Bedrock**：MythosおよびFutureモデルについてAnthropicとの30日間のトラフィックデータ保持・共有を義務付ける方針が発表されていた（→ [[aws-bedrock-anthropic-data-sharing]]）

### 規制の文脈

今回の停止措置は、技術的な障害ではなく政治的・行政的な命令によって引き起こされた点が特徴的である。根拠となったジェイルブレイクが「狭い」ものであったにもかかわらず輸出規制が発動されたことは、高性能AIモデルのサイバーセキュリティ機能に対する規制当局の警戒感の高まりを示している。

Anthropicが「他社モデルにも同等の脆弱性がある」と反論していることは、業界全体の基準と個別企業への規制適用のあり方をめぐる議論を呼ぶ可能性がある。

## Related Articles

- [[project-glasswing-claude-mythos-security]] - Project Glasswing: Claude Mythos Previewによるセキュリティ強化
- [[claude-fable-5-autonomous-behavior]] - Claude Fable 5の自律的なデバッグ行動
- [[aws-bedrock-anthropic-data-sharing]] - AWS BedrockとAnthropicのデータ共有方針
- [[claude-mythos-preview-containment-escape]] - Claude Mythos Previewの封じ込め環境脱出事件
- [[anthropic-ai-monitoring-experiment]] - AnthropicによるAIでAIを監視する実験
- [[anthropic-recursive-self-improvement-warning]] - AnthropicのAI自己改善ループリスク警告

<!-- AUTO:Related Articles -->
## Related Articles

- [[anthropic-claude-code-third-party-tools-additional-fees]]
- [[anthropic-claude-skill-creator-testing-enhancement]]
- [[anthropic-model-suspension-export-control-risk]]
- [[aws-bedrock-anthropic-data-sharing-mythos]]
- [[claude-advisor-strategy-opus-sonnet-cost-optimization]]
- [[claude-code-cli-computer-use-implementation]]
- [[claude-code-ownership-discussion]]
- [[claude-fable-5-proactive-ai-browser-debugging]]
- [[claude-mythos-containment-breach]]
- [[claude-openclaw-subscription-exclusion]]
- [[claude-turning-into-asshole-criticism]]
<!-- /AUTO:Related Articles -->
