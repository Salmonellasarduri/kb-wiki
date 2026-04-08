# わざと汚く書いたコードを /simplify に渡したら半分以下になった

Source: https://zenn.dev/maniizu3110/articles/010-claude-code-simplify-auto-refactor


> わざと汚く書いたコードを /simplify に渡したら半分以下になった


わざと汚く書いたコードを /simplify に渡したら半分以下になった
きっかけ: /simplify って何をしてくれるの？
Claude Code のビルトインスキルに /simplify
というものがあります。「変更したコードをレビューして直してくれる」らしいけど、実際にどこまで直してくれるのか。
そこで、わざと汚いコードを書いた Next.js プロジェクトを用意して、/simplify
がどう修正するかを検証しました。
結果: 7ファイル、467行削除 → 208行追加。コードが半分以下になりました。
/simplify の仕組み
/simplify
は Claude Code のバンドルスキルで、実行すると 3つの専門エージェントが並列で起動 して、最近変更されたコードをレビュー・修正します。
| エージェント | 観点 |
|---|---|
| Code Reuse | コピペされた重複コードの検出・共通化 |
| Code Quality | 型安全性、冗長な記述の改善 |
| Efficiency | アルゴリズムの計算量、不要な再計算の排除 |
3つのエージェントがそれぞれの観点でコードを読み、問題を見つけたら自動で修正してくれます。
実験セットアップ
Next.js（App Router + TypeScript + Tailwind CSS）でタスク管理ダッシュボードを作成。以下の「あるある」な問題を意図的に仕込みました。
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
└── package.json
仕込んだ問題の一覧:
- 同じ
formatDate
関数が4ファイルにコピペ -
if/else
チェーンが延々と続くラベル・カラー判定 - API関数4つに同じヘッダー設定 + エラーハンドリングをコピペ
- バブルソート（O(n²)）でタスク一覧をソート
-
for
ループで手動配列操作（filter/map を使わない） - 毎レンダーで同じ計算を繰り返す（useMemo なし）
-
priority: number
のような緩い型定義
/simplify の実行結果
src/app/dashboard/page.tsx | 78 +++----------
src/components/TaskCard.tsx | 54 ++-------
src/components/TaskList.tsx | 52 +++------
src/components/UserCard.tsx | 35 +-----
src/lib/api.ts | 171 +++++++++------------------
src/lib/utils.ts | 275 ++++++++++++++++----------------------------
src/types/index.ts | 10 +-
7 files changed, 208 insertions(+), 467 deletions(-)
全7ファイルが修正されました。以下、3つの観点ごとに主要な変更を見ていきます。
1. Code Reuse: 重複コードの撲滅
formatDate が4箇所にコピペ → utils.ts に一元化
Before: TaskCard, UserCard, Dashboard にそれぞれ同じ formatDate
がローカル定義されていました。
// src/components/TaskCard.tsx (Before)
// ↓ これとほぼ同じコードが UserCard.tsx, dashboard/page.tsx にもある
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
After: 各コンポーネントからローカル定義を削除し、utils.ts の共通関数を import するだけに。
// src/components/TaskCard.tsx (After)
import {
formatDate,
getPriorityLabel,
getPriorityColor,
getStatusLabel,
getStatusColor,
} from "@/lib/utils";
// ローカルの formatDate, getPriorityLabel, getStatusLabel 等は全削除
getPriorityLabel
, getStatusColor
, getRoleLabel
など、同じパターンで重複していた関数もすべて utils.ts への import に統一されました。
API関数4つの重複 → 共通ヘルパーに集約
Before: fetchTasks
, fetchUsers
, createTask
, deleteTask
に同じヘッダー設定 + エラーハンドリングが丸ごとコピペ。1関数あたり約30行。
// src/lib/api.ts (Before) — fetchTasks と fetchUsers がほぼ同一
export async function fetchTasks() {
try {
const response = await fetch(API_BASE + "/tasks", {
method: "GET",
headers: {
"Content-Type": "application/json",
Authorization: "Bearer " + getToken(),
},
});
if (response.status === 200) {
const data = await response.json();
return data;
} else if (response.status === 401) {
console.log("Unauthorized");
return null;
} else if (response.status === 404) {
console.log("Not found");
return null;
} else if (response.status === 500) {
console.log("Server error");
return null;
} else {
console.log("Unknown error");
return null;
}
} catch (error) {
console.log("Network error");
return null;
}
}
// fetchUsers, createTask, deleteTask もほぼ同じ...
After: 共通の apiRequest
ヘルパーを抽出。各関数は2〜3行のラッパーに。
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
136行 → 75行。 さらに、戻り値が { ok, data }
になったことで、修正前にあった「DELETE 成功時の null
とエラー時の null
を区別できない」というバグも解消されました。
2. Code Quality: 型安全性と明瞭さ
緩い型を union type で制限
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
priority: number
だと priority: 999
がコンパイルを通ってしまいます。Priority = 1 | 2 | 3
にすることで不正な値をコンパイル時に弾けるようになりました。
if/else チェーン → Record ルックアップマップ
// src/lib/utils.ts
-export function getPriorityLabel(priority: number): string {
- if (priority === 1) {
- return "Low";
- } else if (priority === 2) {
- return "Medium";
- } else if (priority === 3) {
- return "High";
- } else {
- return "Unknown";
- }
-}
+const PRIORITY_LABELS: Record<Priority, string> = {
+ 1: "Low", 2: "Medium", 3: "High"
+};
+
+export function getPriorityLabel(priority: Priority): string {
+ return PRIORITY_LABELS[priority] ?? "Unknown";
+}
getStatusLabel
, getStatusColor
, getRoleLabel
, getRoleColor
もすべて同じパターンで書き換えられました。データと処理が分離されて、新しい値の追加も1行で済むようになっています。
onStatusChange の型を string → Task["status"] に
// src/components/TaskCard.tsx
-onStatusChange: (id: number, status: string) => void;
+onStatusChange: (id: number, status: Task["status"]) => void;
string
だと onStatusChange(1, "typo")
が通ってしまいますが、Task["status"]
なら "todo" | "in_progress" | "done"
のみに制限されます。
細かいところも
-{isExpanded === true && (
+{isExpanded && (
=== true
は不要。地味だけど、こういうのを拾ってくれるのは嬉しい。
3. Efficiency: パフォーマンス改善
バブルソート O(n²) → Array.sort() O(n log n)
// src/lib/utils.ts
-export function sortTasks(tasks: any[], sortBy: string, sortOrder: string): any[] {
- const sorted = [...tasks];
- for (let i = 0; i < sorted.length; i++) {
- for (let j = i + 1; j < sorted.length; j++) {
- let shouldSwap = false;
- if (sortBy === "priority") {
- if (sortOrder === "asc") {
- shouldSwap = sorted[i].priority > sorted[j].priority;
- } else {
- shouldSwap = sorted[i].priority < sorted[j].priority;
- }
- }
- // ... title, createdAt も同様に分岐
- if (shouldSwap) {
- const temp = sorted[i];
- sorted[i] = sorted[j];
- sorted[j] = temp;
- }
- }
- }
- return sorted;
-}
+export function sortTasks(tasks: Task[], sortBy: string, sortOrder: string): Task[] {
+ const dir = sortOrder === "asc" ? 1 : -1;
+ return [...tasks].sort((a, b) => {
+ if (sortBy === "priority") return (a.priority - b.priority) * dir;
+ if (sortBy === "title") return a.title.localeCompare(b.title) * dir;
+ return (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) * dir;
+ });
+}
25行 → 7行。O(n²) → O(n log n)。さらに any[]
→ Task[]
に型も強化されています。
useMemo でメモ化
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
修正前はレンダーのたびにフィルタ・ソート・統計をすべて再計算していましたが、依存値が変わった時だけ再計算するようになりました。
Dashboard 側も同様に、17行のインライン統計計算が useMemo(() => calculateTaskStats(tasks), [tasks])
の1行に。未使用だった selectedUser
state と handleUserSelect
関数も削除されました。
for ループ → Array メソッド
// src/components/TaskList.tsx — handleDelete
-const newTasks = [];
-for (let i = 0; i < tasks.length; i++) {
- if (tasks[i].id !== id) {
- newTasks.push(tasks[i]);
- }
-}
-setTasks(newTasks);
+setTasks(tasks.filter((t) => t.id !== id));
// src/components/TaskList.tsx — handleStatusChange
-const newTasks = [];
-for (let i = 0; i < tasks.length; i++) {
- if (tasks[i].id === id) {
- newTasks.push({
- id: tasks[i].id,
- title: tasks[i].title,
- description: tasks[i].description,
- status: newStatus as Task["status"],
- priority: tasks[i].priority,
- createdAt: tasks[i].createdAt,
- assignee: tasks[i].assignee,
- });
- } else {
- newTasks.push(tasks[i]);
- }
-}
-setTasks(newTasks);
+setTasks(tasks.map((t) => (t.id === id ? { ...t, status: newStatus } : t)));
フィールドを1つずつ手動コピーしていたのが、スプレッド構文で変更点だけ上書きする形に。
まとめ
/simplify
が修正した内容を整理するとこうなります。
| 観点 | Before | After |
|---|---|---|
| Code Reuse | formatDate等が4ファイルにコピペ、API関数4つに同じエラー処理 | utils.ts に一元化、apiRequest ヘルパーに集約 |
| Code Quality |
priority: number , role: string で何でも代入可能 |
union type で制限、Record ルックアップマップ |
| Efficiency | バブルソート O(n²)、毎レンダー全計算、手動 for ループ | Array.sort() O(n log n)、useMemo、filter/map |
467行削除、208行追加。 コード量が半分以下になっただけでなく、バグ修正（deleteTask の成功/失敗判定）や型安全性の向上も含まれていました。
/simplify が向いているケース
- プロトタイピング後のコード整理
- レビュー前のセルフチェック
- 「動くけど汚い」コードのリファクタリング
逆に、アーキテクチャレベルの設計変更（モノリスをマイクロサービスに分割する、等）は /simplify
のスコープ外です。あくまで「既存の構造の中で、コードの品質を上げる」ためのツールという位置づけです。
Discussion
いいですね！やってみます！
