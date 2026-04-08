---
article_id: claude-simplify-code-refactoring-experiment
title: Claude Code /simplifyコマンドによる自動リファクタリング実験 - 汚いコードが半分以下に
type: source
source_ids:
  - cfd7fba73ec2
topics:
  - claude-code-tools
  - automatic-refactoring
  - code-quality-improvement
  - typescript-optimization
  - ai-code-review
aliases_ja:
  - クロードコード
  - 自動リファクタリング
  - コード品質改善
  - TypeScript最適化
  - AIコードレビュー
  - simplifyコマンド
  - 重複コード削除
  - バブルソート最適化
  - useMemo最適化
  - 型安全性向上
published_at: ""
source_urls:
  - https://zenn.dev/maniizu3110/articles/010-claude-code-simplify-auto-refactor
summary: >
  Claude Code の /simplify コマンドを使った実験で、意図的に汚く書いたNext.jsコード（467行）が208行まで削減され、重複コード排除・型安全性向上・パフォーマンス最適化が自動実行された。
  3つの専門エージェント（Code Reuse・Code Quality・Efficiency）が並列動作し、バブルソートからArray.sort()への変更やuseMemoによるメモ化などの改善を実施。
created_at: "2026-04-05 13:06"
updated_at: "2026-04-05 13:06"
---

# Claude Code /simplifyコマンドによる自動リファクタリング実験 - 汚いコードが半分以下に

Claude Code のビルトインスキル `/simplify` の実力を検証するため、意図的に汚いコードで構築したNext.jsプロジェクトを用意し、どの程度まで自動修正されるかを実験した結果、467行のコードが208行まで削減され、半分以下になった。

## /simplifyの仕組み

`/simplify` は Claude Code のバンドルスキルで、実行すると3つの専門エージェントが並列で起動し、最近変更されたコードをレビュー・修正する。

| エージェント | 観点 |
|---|---|
| Code Reuse | コピペされた重複コードの検出・共通化 |
| Code Quality | 型安全性、冗長な記述の改善 |
| Efficiency | アルゴリズムの計算量、不要な再計算の排除 |

## 実験セットアップ

Next.js（App Router + TypeScript + Tailwind CSS）でタスク管理ダッシュボードを作成し、以下の「あるある」な問題を意図的に仕込んだ：

```
simplify-demo/
├── src/
│ ├── app/
│ │ ├── page.tsx # タスク一覧ページ
│ │ └── dashboard/
│ │ └── page.tsx # ダッシュボード（統計のインライン計算、重複formatDate）
│ ├── components/
│ │ ├── TaskCard.tsx # タスクカード（ローカルにformatDate等を重複定義）
│ │ ├── TaskList.tsx # タスクリスト（メモ化なし、手動forループ）
│ │ └── UserCard.tsx # ユーザーカード（ローカルにformatDate等を重複定義）
│ ├── lib/
│ │ ├── api.ts # API関数4つにまったく同じエラー処理をコピペ
│ │ └── utils.ts # バブルソート、if/elseチェーン、手動カウンタ
│ └── types/
│ └── index.ts # priority: number のような緩い型
```

仕込んだ問題：
- 同じ `formatDate` 関数が4ファイルにコピペ
- `if/else` チェーンが延々と続くラベル・カラー判定
- API関数4つに同じヘッダー設定 + エラーハンドリングをコピペ
- バブルソート（O(n²)）でタスク一覧をソート
- `for` ループで手動配列操作（filter/map を使わない）
- 毎レンダーで同じ計算を繰り返す（useMemo なし）
- `priority: number` のような緩い型定義

## 実行結果

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

## Code Reuse: 重複コードの撲滅

### formatDateの一元化

**修正前**: TaskCard, UserCard, Dashboard にそれぞれ同じ `formatDate` がローカル定義されていた。

```typescript
// src/components/TaskCard.tsx (Before)
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  let monthStr = month < 10 ? "0" + month : "" + month;
  let dayStr = day < 10 ? "0" + day : "" + day;
  let hoursStr = hours < 10 ? "0" + hours : "" + hours;
  let minutesStr = minutes < 10 ? "0" + minutes : "" + minutes;
  return (
    year + "/" + monthStr + "/" + dayStr + " " + hoursStr + ":" + minutesStr
  );
};
```

**修正後**: 各コンポーネントからローカル定義を削除し、utils.ts の共通関数を import するだけに。

```typescript
// src/components/TaskCard.tsx (After)
import {
  formatDate,
  getPriorityLabel,
  getPriorityColor,
  getStatusLabel,
  getStatusColor,
} from "@/lib/utils";
```

### API関数の共通化

**修正前**: `fetchTasks`, `fetchUsers`, `createTask`, `deleteTask` に同じヘッダー設定 + エラーハンドリングが丸ごとコピペされていた（1関数あたり約30行）。

**修正後**: 共通の `apiRequest` ヘルパーを抽出し、各関数は2〜3行のラッパーに。

```typescript
// src/lib/api.ts (After)
async function apiRequest(
  path: string,
  options: RequestInit = {},
): Promise<{ ok: boolean; data: unknown }> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
        ...options.headers,
      },
    });
    if (response.ok) {
      const data = response.status === 204 ? null : await response.json();
      return { ok: true, data };
    }
    const messages: Record<number, string> = {
      401: "Unauthorized",
      404: "Not found",
      500: "Server error",
    };
    console.log(messages[response.status] ?? "Unknown error");
    return { ok: false, data: null };
  } catch {
    console.log("Network error");
    return { ok: false, data: null };
  }
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

136行 → 75行に削減。さらに、戻り値が `{ ok, data }` になったことで、修正前にあった「DELETE 成功時の null とエラー時の null を区別できない」というバグも解消された。

## Code Quality: 型安全性と明瞭さの向上

### union typeによる型制限

```typescript
// src/types/index.ts
+export type Priority = 1 | 2 | 3;
+export type UserRole = "admin" | "manager" | "developer" | "designer";

export interface Task {
  status: "todo" | "in_progress" | "done";
- priority: number;
+ priority: Priority;
}

export interface User {
- role: string;
+ role: UserRole;
}
```

`priority: number` だと `priority: 999` がコンパイルを通ってしまうが、`Priority = 1 | 2 | 3` にすることで不正な値をコンパイル時に弾けるようになった。

### if/elseチェーンからRecordルックアップへ

```typescript
// src/lib/utils.ts
-export function getPriorityLabel(priority: number): string {
- if (priority === 1) {
-   return "Low";
- } else if (priority === 2) {
-   return "Medium";
- } else if (priority === 3) {
-   return "High";
- } else {
-   return "Unknown";
- }
-}

+const PRIORITY_LABELS: Record<Priority, string> = {
+ 1: "Low", 2: "Medium", 3: "High"
+};
+
+export function getPriorityLabel(priority: Priority): string {
+ return PRIORITY_LABELS[priority] ?? "Unknown";
+}
```

`getStatusLabel`, `getStatusColor`, `getRoleLabel`, `getRoleColor` もすべて同じパターンで書き換えられ、データと処理が分離されて新しい値の追加も1行で済むようになった。

### 型安全性の強化

```typescript
// src/components/TaskCard.tsx
-onStatusChange: (id: number, status: string) => void;
+onStatusChange: (id: number, status: Task["status"]) => void;
```

`string` だと `onStatusChange(1, "typo")` が通ってしまうが、`Task["status"]` なら `"todo" | "in_progress" | "done"` のみに制限される。

## Efficiency: パフォーマンス改善

### バブルソートからArray.sort()への最適化

**修正前**: O(n²) のバブルソート実装（25行）

**修正後**: Array.sort() を使用した実装（7行）

```typescript
// src/lib/utils.ts
+export function sortTasks(tasks: Task[], sortBy: string, sortOrder: string): Task[] {
+ const dir = sortOrder === "asc" ? 1 : -1;
+ return [...tasks].sort((a, b) => {
+   if (sortBy === "priority") return (a.priority - b.priority) * dir;
+   if (sortBy === "title") return a.title.localeCompare(b.title) * dir;
+   return (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) * dir;
+ });
+}
```

O(n²) → O(n log n) に改善され、さらに `any[]` → `Task[]` に型も強化された。

### useMemoによるメモ化

```typescript
// src/components/TaskList.tsx
-const filteredTasks = filterTasks(tasks, statusFilter, priorityFilter, searchQuery);
-const sortedTasks = sortTasks(filteredTasks, sortBy, sortOrder);
-const stats = calculateTaskStats(tasks);

+const filteredTasks = useMemo(
+ () => filterTasks(tasks, statusFilter, priorityFilter, searchQuery),
+ [tasks, statusFilter, priorityFilter, searchQuery]
+);
+const sortedTasks = useMemo(
+ () => sortTasks(filteredTasks, sortBy, sortOrder),
+ [filteredTasks, sortBy, sortOrder]
+);
+const stats = useMemo(() => calculateTaskStats(tasks), [tasks]);
```

修正前はレンダーのたびにフィルタ・ソート・統計をすべて再計算していたが、依存値が変わった時だけ再計算するようになった。

### 手動forループからArrayメソッドへ

```typescript
// handleDelete の変更
-const newTasks = [];
-for (let i = 0; i < tasks.length; i++) {
- if (tasks[i].id !== id) {
-   newTasks.push(tasks[i]);
- }
-}
-setTasks(newTasks);

+setTasks(tasks.filter((t) => t.id !== id));

// handleStatusChange の変更
+setTasks(tasks.map((t) => (t.id === id ? { ...t, status: newStatus } : t)));
```

フィールドを1つずつ手動コピーしていたのが、スプレッド構文で変更点だけ上書きする形に改善された。

## 実験結果まとめ

| 観点 | Before | After |
|---|---|---|
| Code Reuse | formatDate等が4ファイルにコピペ、API関数4つに同じエラー処理 | utils.ts に一元化、apiRequest ヘルパーに集約 |
| Code Quality | `priority: number`, `role: string` で何でも代入可能 | union type で制限、Record ルックアップマップ |
| Efficiency | バブルソート O(n²)、毎レンダー全計算、手動 for ループ | Array.sort() O(n log n)、useMemo、filter/map |

467行削除、208行追加でコード量が半分以下になっただけでなく、バグ修正（deleteTask の成功/失敗判定）や型安全性の向上も含まれていた。

## /simplifyが向いているケース

- プロトタイピング後のコード整理
- レビュー前のセルフチェック
- 「動くけど汚い」コードのリファクタリング

逆に、アーキテクチャレベルの設計変更（モノリスをマイクロサービスに分割する等）は `/simplify` のスコープ外で、あくまで「既存の構造の中で、コードの品質を上げる」ためのツールという位置づけである。

## Related Articles

- [[claude-code-cli-computer-use]] - Claude Code CLIのComputer Use機能との関連
- [[claude-integration-github-automation]] - Claudeを使った開発ワークフロー自動化
- [[llm-knowledge-management-workflow]] - LLMを活用した知識管理ワークフロー

<!-- AUTO:Related Articles -->
## Related Articles

- [[claude-code-simplify-refactoring-experiment]]
- [[obsidian-mind-claude-memory-system]]
<!-- /AUTO:Related Articles -->
