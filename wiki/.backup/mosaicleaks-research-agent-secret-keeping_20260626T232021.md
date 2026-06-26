---
article_id: mosaicleaks-research-agent-secret-keeping
title: "MosaicLeaks: リサーチエージェントは機密情報を保持できるか"
type: stub
source_ids:
  - ab355b101519
topics:
  - ai-agent-security
  - information-leakage
  - research-agents
  - ai-trust
aliases_ja:
  - MosaicLeaks
  - モザイクリークス
  - リサーチエージェント
  - AIエージェントの秘密保持
  - 機密情報漏洩
  - エージェントの信頼性
  - 情報を守るAI
published_at: ""
source_urls:
  - https://huggingface.co/blog/ServiceNow/mosaicleaks
summary: >
  「MosaicLeaks」は、AIリサーチエージェントが機密情報を保持できるかどうかを検証した研究・報告。
  エージェントが何を「保持」し、何を「滲み出す」かという問いは、AIシステムへの信頼の構造そのものに関わる問題として提起されている。
created_at: "2026-06-26 23:04"
updated_at: "2026-06-26 23:04"
---

# MosaicLeaks: リサーチエージェントは機密情報を保持できるか

**MosaicLeaks**は、ServiceNowがHugging Faceブログ上で報告した研究で、AIリサーチエージェントが機密情報（秘密）を保持し続けられるかどうかを検証したものである。

## 概要

タイトルが示すように、この研究の中心的な問いは「リサーチエージェントは秘密を守れるか（Can your research agent keep a secret?）」というものである。

AIエージェントが情報を処理・保持する過程において、意図せず機密情報を「滲み出す（leak）」可能性があるかどうかを検証した内容とされているが、ソースドキュメントに記載されている詳細情報はタイトルと問題提起の水準に留まる。

## 意義

エージェントが何を記憶し、何を外部に漏らすかという問題は、AIシステムへの信頼の構造そのものと直結する。特にリサーチエージェントが企業内部の情報や個人情報を扱うユースケースが増える中で、情報漏洩リスクの評価は実用上の重要性を持つ。

> [!note] ソースが限定的です。記事は不完全な可能性があります。

## Related Articles

- [[chatgpt-lockdown-mode-prompt-injection]] — [[ChatGPTに「ロックダウンモード」 プロンプトインジェクションによる情報漏えい対策]]
- [[ai-agent-bankrupted-dn42]] — [[AI Agent Bankrupted Their Operator While Trying to Scan DN42]]
- [[ai-memory-design-what-to-remember-forget]] — [[AIメモリ設計の最適解：エージェントは何を記憶し、何を「忘れる」べきか]]
- [[deontic-policies-agentic-ai-governance]] — [[Deontic Policies for Runtime Governance of Agentic AI Systems]]