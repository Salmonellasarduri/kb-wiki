---
article_id: claude-code-simplify-refactoring-experiment
title: Claude Code の /simplify によるコードリファクタリング実験 - 467行が208行へ半減
type: source
source_ids:
  - cfd7fba73ec2
topics:
  - ai-code-refactoring
  - code-quality-improvement
  - claude-code-features
  - automated-code-review
  - software-development-automation
aliases_ja:
  - Claude Code
  - simplify
  - コードリファクタリング
  - AIコードレビュー
  - 自動コード改善
  - TypeScript
  - Next.js
  - コード品質改善
  - 重複コード削除
  - パフォーマンス最適化
published_at: ""
source_urls:
  - https://zenn.dev/maniizu3110/articles/010-claude-code-simplify-auto-refactor
summary: >
  Claude Code の /simplify 機能を意図的に汚く書いたNext.jsコードで検証した結果、467行のコードが208行へと半分以下に削減された。
  3つの専門エージェント（Code Reuse、Code Quality、Efficiency）が並列動作し、重複コード削除、型安全性向上、パフォーマンス改善を自動実行する。
created_at: "2026-04-05"
updated_at: "2026-04-05"
---

# Claude Code の /simplify によるコードリファクタリング実験 - 467行が208行へ半減

## 概要

Claude Code のビルトインスキル `/simplify` の性能検証として、意図的に低品質なNext.jsプロジェクトを作成し、自動リファクタリング機能を検証した実験レポート。結果として、7ファイル467行のコードが208行へと半分以下に削減され、同時に型安全性とパフォーマンスの向上も実現された。

## /simplify の仕組み

`/simplify` は Claude Code のバンドルスキルで、実行時に3つの専門エージェントが並列起動し、最近変更されたコードを自動レビュー・修正する。

| エージェント | 担当領域 |
|---|---|
| **Code Reuse** | コピペされた重複コードの検出・共通化 |
| **Code Quality** | 型安全性、冗長な記述の改善 |
| **Efficiency** | アルゴリズムの計算量、不要な再計算の排除 |

## 実験セットアップ

Next.js（App Router + TypeScript + Tailwind CSS）でタスク管理ダッシュボードを構築し、以下の典型的な問題を意図的に仕込んだ：

```
simplify-demo/
├── src/
│   ├── app/
│   │   ├── page.tsx # タスク一覧ページ
│   │   └── dashboard/page.tsx # 統計のインライン計算、重複formatDate
│   ├── components/
│   │   ├── TaskCard.tsx # ローカルにformatDate等を重複定義
│   │   ├── TaskList.tsx # メモ化なし、手動forループ
│   │   └── UserCard.tsx # ローカルにformatDate等を重複定義
│   ├── lib/
│   │   ├── api.ts # API関数4つに同じエラー処理をコピペ
│   │   └── utils.ts # バブルソート、if/elseチェーン
│   └── types/index.ts # priority: number のような緩い型
```

### 仕込んだ問題一覧

- 同じ `formatDate` 関数が4ファイルにコピペ
- if/elseチェーンが延々と続くラベル・カラー判定
- API関数4つに同じヘッダー設定 + エラーハンドリングをコピペ
- バブルソート（O(n²)）でタスク一覧をソート
- forループで手動配列操作（filter/map を使わない）
- 毎レンダーで同じ計算を繰り返す（useMemo なし）
- `priority: number` のような緩い型定義

## リファクタリング結果

```
src/app/dashboard/page.tsx | 78 +++----------
src/components/TaskCard.tsx | 54 ++-------
src/components/TaskList.tsx | 52 +++------
src/components/UserCard.tsx | 35 +-----
src/lib/api.ts | 171 +++++++++------------------
src/lib/utils.ts | 275 ++++++++++++++++----------------------------
src/types/index.ts | 10 +-
7 files changed, 208 insertions(+), 467 deletions(-)
```

## 主要な改善内容

### 1. Code Reuse: 重複コードの撲滅

#### formatDate の共通化
**Before**: 4ファイルに同じ `formatDate` をローカル定義
```typescript
// TaskCard.tsx, UserCard.tsx, dashboard/page.tsx に重複
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  // ... 冗長な文字列操作
  return year + "/" + monthStr + "/" + dayStr + " " + hoursStr + ":" + minutesStr;
};
```

**After**: utils.ts に一元化し、各コンポーネントはimportのみ
```typescript
import { formatDate, getPriorityLabel, getPriorityColor } from "@/lib/utils";
```

#### API関数の共通化
**Before**: 4つのAPI関数に同じヘッダー設定とエラーハンドリングをコピペ（1関数約30行）

**After**: 共通の `apiRequest` ヘルパーを抽出、各関数は2〜3行のラッパーに
```typescript
async function apiRequest(path: string, options: RequestInit = {}) {
  // 共通のヘッダー設定とエラーハンドリング
}

export async function fetchTasks() {
  const { data } = await apiRequest("/tasks");
  return data as unknown[] | null;
}

export async function deleteTask(id: number): Promise<boolean> {
  const { ok } = await apiRequest(`/tasks/${id}`, { method: "DELETE" });
  return ok;
}
```

136行 → 75行への削減に加え、「DELETE成功時のnullとエラー時のnullを区別できない」バグも解消。

### 2. Code Quality: 型安全性と明瞭さ

#### Union Type による型制限
```typescript
// Before
export interface Task {
  priority: number; // 999等の不正値も通る
}

// After
export type Priority = 1 | 2 | 3;
export type UserRole = "admin" | "manager" | "developer" | "designer";

export interface Task {
  priority: Priority;
}
```

#### if/elseチェーンをRecordルックアップマップへ
```typescript
// Before: 冗長な分岐処理
export function getPriorityLabel(priority: number): string {
  if (priority === 1) return "Low";
  else if (priority === 2) return "Medium";
  else if (priority === 3) return "High";
  else return "Unknown";
}

// After: データと処理の分離
const PRIORITY_LABELS: Record<Priority, string> = {
  1: "Low", 2: "Medium", 3: "High"
};

export function getPriorityLabel(priority: Priority): string {
  return PRIORITY_LABELS[priority] ?? "Unknown";
}
```

### 3. Efficiency: パフォーマンス改善

#### バブルソート → Array.sort()
```typescript
// Before: O(n²) のバブルソート（25行）
export function sortTasks(tasks: any[], sortBy: string, sortOrder: string) {
  for (let i = 0; i < sorted.length; i++) {
    for (let j = i + 1; j < sorted.length; j++) {
      // 複雑な分岐とswap処理
    }
  }
}

// After: O(n log n) のネイティブソート（7行）
export function sortTasks(tasks: Task[], sortBy: string, sortOrder: string): Task[] {
  const dir = sortOrder === "asc" ? 1 : -1;
  return [...tasks].sort((a, b) => {
    if (sortBy === "priority") return (a.priority - b.priority) * dir;
    if (sortBy === "title") return a.title.localeCompare(b.title) * dir;
    return (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) * dir;
  });
}
```

#### useMemoによるメモ化
```typescript
// Before: 毎レンダーで全再計算
const filteredTasks = filterTasks(tasks, statusFilter, priorityFilter, searchQuery);
const sortedTasks = sortTasks(filteredTasks, sortBy, sortOrder);

// After: 依存値変更時のみ再計算
const filteredTasks = useMemo(
  () => filterTasks(tasks, statusFilter, priorityFilter, searchQuery),
  [tasks, statusFilter, priorityFilter, searchQuery]
);
const sortedTasks = useMemo(
  () => sortTasks(filteredTasks, sortBy, sortOrder),
  [filteredTasks, sortBy, sortOrder]
);
```

#### 手動forループ → Arrayメソッド
```typescript
// Before: 手動配列操作
const newTasks = [];
for (let i = 0; i < tasks.length; i++) {
  if (tasks[i].id !== id) {
    newTasks.push(tasks[i]);
  }
}
setTasks(newTasks);

// After: 関数型プログラミング
setTasks(tasks.filter((t) => t.id !== id));
```

## 改善効果まとめ

| 観点 | Before | After |
|---|---|---|
| **Code Reuse** | formatDate等が4ファイルにコピペ、API関数に同じエラー処理 | utils.ts に一元化、apiRequest ヘルパーに集約 |
| **Code Quality** | `priority: number`, `role: string` で何でも代入可能 | union type で制限、Record ルックアップマップ |
| **Efficiency** | バブルソート O(n²)、毎レンダー全計算、手動forループ | Array.sort() O(n log n)、useMemo、filter/map |

**結果**: 467行削除、208行追加でコード量が半分以下に。同時にバグ修正と型安全性向上も実現。

## 適用場面と限界

### /simplify が有効なケース
- プロトタイピング後のコード整理
- レビュー前のセルフチェック  
- 「動くけど汚い」コードのリファクタリング

### 限界
アーキテクチャレベルの設計変更（モノリスをマイクロサービスに分割等）は対象外。あくまで既存構造内でのコード品質向上ツールとしての位置づけ。

## Related Articles

[[claude-code-computer-use-cli-implementation]] - Claude Code CLIの他の機能について
[[llm-knowledge-management-andrej-karpathy-workflow]] - LLMを活用した開発ワークフローの参考例

<!-- AUTO:Related Articles -->
## Related Articles

- [[claude-simplify-code-refactoring-experiment]]
<!-- /AUTO:Related Articles -->
