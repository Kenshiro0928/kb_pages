---
id: doc-2025-08-17-kb-sop-v-1-0
title: "kb運用sop_v_1_0_｜フォルダ設計・呼び出し手順・フィードバック_更新サイクル（実装ブループリント）"
confidentiality: internal
route_hint: Balanced
source: { published_at: 2025-08-17 }
---

# KB運用SOP v1.0｜フォルダ設計・呼び出し手順・フィードバック/更新サイクル（実装ブループリント）

> 目的：AI（12人格）が実務で使う知識を **ファイル/フォルダ** として管理し、**いつ/どの手順で/どのファイルを呼び出すか**、**どうフィードバックしてアップデートするか** を“再現可能”にする。

---

## 1. リポジトリ構成（Docs-as-Code）

```
kb/
  README.md
  CHANGELOG.md
  LICENSE (任意)
  .kbconfig.yml                 # 全体設定（ルート）
  schemas/                      # JSON/YAML Schema群（front matter検証）
    doc.schema.json
    metric.schema.json
    persona.schema.json
    sop.schema.json
  personas/                     # 人格定義（12コア＋支援）
    00-index.md
    persona-cfo.md
    persona-integrator.md
    persona-meta-critic.md
    ...
  workflows/                    # SOP/手順書（目的別）
    sop-sales-intake.md
    sop-pricing-change.md
    sop-contract-review.md
    sop-ir-letter.md
  playbooks/                    # ドメイン別プレイブック（不動産/FC/研修/投資）
    realestate-masterlease.md
    franchise-bd.md
    training-on-the-job.md
    investor-ir.md
  decisions/                    # 意思決定ログ（ADR/DR）
    dr-2025-08-16-pricing-revision.md
  metrics/                      # 指標定義とData Contract
    catalog.yml
    data-contracts.yml
  okr/                          # 会社/部門OKR
    2025H2-company.yml
    2025H2-sales.yml
  prompts/                      # プロンプト部品（system/task/checklist）
    system/standard.md
    task/sales-intake.md
    checklist/legal-redteam.md
  templates/                    # ひな型（1‑Pager/提案/IR/契約赤入れ等）
    onepager.md
    proposal.md
    faq.md
  glossaries/                   # 用語/タグ/命名規約
    taxonomy.yml
  automation/                   # レビュー/リマインド/公開用
    review.ics                  # RRULE集（例）
  scripts/                      # CLI/ビルド/検証
    build_index.py              # index.json生成
    validate.py                 # schema検証
    search_cli.py               # 簡易検索
  index.json                    # 自動生成（検索/参照用メタ）
```

**命名規則**（一例）：

- ファイルID＝`<カテゴリ>-<YYYY-MM-DD>-<slug>`（例：`dr-2025-08-16-pricing-revision.md`）
- Front matterの`version: semver`、`status: draft/active/deprecated`、`owners: [...]`、`review_cycle: RRULE` を必須化。

---

## 2. Front Matter（YAML）標準スキーマ

**共通**（全ドキュメント）：

```yaml
---
id: dr-2025-08-16-pricing-revision
title: 価格改定の意思決定
type: [decision, finance]
version: 1.0.0
status: active
created_at: 2025-08-16
updated_at: 2025-08-16
owners: ["CFO人格", "統合応答人格"]
reviewers: ["メタ批判人格", "法務オブザーバ人格"]
review_cycle: "FREQ=MONTHLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0;BYSECOND=0"
tags: [pricing, finance, decision]
confidentiality: internal
links:
  - rel: source
    href: ../metrics/catalog.yml#pricing
  - rel: sop
    href: ../workflows/sop-pricing-change.md
---
```

**SOP（例）**：

```yaml
---
id: sop-pricing-change
title: 価格改定の意思決定SOP
version: 1.1.0
status: active
owners: ["CFO人格"]
reviewers: ["戦略人格", "メタ批判人格"]
preconditions:
  data_freshness_hours: 24
  data_completeness_pct: 99.5
inputs:
  - name: elasticity_estimate
    requirement: required
  - name: cac_ltv
    requirement: required
  - name: competitor_prices
    requirement: recommended
outputs:
  - new_price_table
  - rollout_plan
  - faq
quality_criteria:
  - name: revenue_impact_simulated
    threshold: "±10%以内"
  - name: churn_risk_segmented
    threshold: "ハイリスク層に対策策定"
---
```

**メトリクス（例）**：

```yaml
---
id: mrr_growth
name: MRR Growth
formula: (MRR_t - MRR_{t-1}) / MRR_{t-1}
grain: monthly
source: billing_system
owner: CFO人格
reviewers: データ科学人格
slo:
  freshness_hours: 24
  completeness_pct: 99.5
change_log:
  - 2025-08-16: 初版
---
```

---

## 3. index.json の生成（自動）

`/scripts/build_index.py`（擬似コード抜粋）：

```python
#!/usr/bin/env python3
import os, re, json, hashlib, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ["personas", "workflows", "playbooks", "decisions", "metrics", "okr", "prompts", "templates", "glossaries"]

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

def parse_front_matter(text: str):
    m = FM_RE.match(text)
    if not m:
        return {}
    import yaml  # pyyaml想定
    return yaml.safe_load(m.group(1)) or {}

def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

records = []
for d in TARGETS:
    base = ROOT / d
    if not base.exists():
        continue
    for p in base.rglob("*.md") | base.rglob("*.yml") | base.rglob("*.yaml"):
        try:
            txt = p.read_text(encoding="utf-8")
            meta = parse_front_matter(txt) if p.suffix == ".md" else (yaml.safe_load(txt) or {})
            rec = {
                "id": meta.get("id") or p.stem,
                "title": meta.get("title") or p.stem,
                "type": meta.get("type") or [d],
                "status": meta.get("status", "active"),
                "tags": meta.get("tags", []),
                "owners": meta.get("owners", []),
                "updated_at": meta.get("updated_at") or datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d"),
                "path": str(p.relative_to(ROOT)),
                "etag": file_hash(p),
                "confidentiality": meta.get("confidentiality", "public"),
            }
            records.append(rec)
        except Exception as e:
            print(f"WARN: {p}: {e}")

(Path(ROOT)/"index.json").write_text(json.dumps({"generated_at": datetime.datetime.utcnow().isoformat()+"Z", "items": records}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK: {len(records)} items")
```

**補足**：`validate.py` で `schemas/*.json` による検証を実行（`jsonschema`）。CIで `build_index.py`→`validate.py` を必須化。

---

## 4. 呼び出し手順（When/Which/How）

**タスク→必要ファイルの決定ロジック（擬似・言語非依存）**

```
INPUT: task_type, domain, risk_level, context (customer, product, market)
1) マッピング表で task_type→必須SOP を解決
2) SOP.front matter の inputs/outputs を読み、足りない前提データをチェック
3) SOP.links から関連 playbook / persona / prompts / templates を列挙
4) risk_level に応じて reviewers（メタ批判/法務）を追加
5) prompts/system + prompts/task + checklist を結合して実行プロンプトを構築
6) 出力テンプレ（templates/*）に差し込んで成果物を生成
7) decisions/ へDR作成。index.json を更新
```

**例：新規商談一次対応（sales-intake）**

- 参照：`workflows/sop-sales-intake.md` → `prompts/task/sales-intake.md` → `templates/onepager.md` → `personas/persona-sales.md`
- 生成：メール草案、30分アジェンダ、確認質問10、CRM入力項目。

**例：価格改定**

- 参照：`sop-pricing-change.md` → `metrics/catalog.yml`（弾力性、CAC/LTV）→ `playbooks/investor-ir.md`（周知）→ `checklist/legal-redteam.md`
- 生成：新価格表、ロールアウト計画、FAQ、IR/CS向け要旨。

---

## 5. フィードバック→アップデートサイクル（Issue→PR→レビュー→リリース）

**Issue分類**：`bug（誤り） / enhance（改善） / data（指標定義変更） / sop（手順変更） / persona（責任変更）`

**PRテンプレ**（`.github/pull_request_template.md`）

```
### 変更概要
- どのSOP/指標/人格に影響？

### 根拠データ
- 出典・更新日・メトリクス（鮮度/完全性SLO）

### リスク&対策
- 逆因果/リーク/プライバシー/非弁回避

### チェック
- [ ] schema検証通過  - [ ] index.json更新  - [ ] reviewers承認  - [ ] 既存テンプレ互換
```

**レビュー規約**：

- 重大（risk\_level ≥ M）：**統合応答A**＋**メタ批判C**の二重レビュー必須。法務関連は**法務Obs**をCに追加。
- 軽微：オーナー承認で可。週次でまとめて`CHANGELOG.md`を発行。

**リリース**：

- `CHANGELOG.md` にセマンティックバージョニングで追記。ETag更新→`index.json`再生成。
- `automation/review.ics` のRRULEで、レビュー周期をカレンダー配信（例：毎月第1月曜10:00）。

---

## 6. 検索・参照（CLI）

`/scripts/search_cli.py`（擬似）：

```python
# usage: python scripts/search_cli.py --tag pricing --type sop --status active
# index.jsonから絞り込み→パスを列挙
```

**検索軸**：`type / tags / status / owners / updated_at（範囲）/ confidentiality`

---

## 7. プロンプト組立（Context Builder）

**結合順序**：

1. `prompts/system/standard.md`（制約・役割）
2. タスク固有 `prompts/task/*.md`（入出力仕様/チェックリスト）
3. 参照 `workflows/*`（SOPの期待品質/失敗モード）
4. `personas/*`（RACI/判断ハンドル）
5. `metrics/*`（定義・閾値）

**出力**：実行プロンプト（下書き）＋成果物テンプレへの差し込み結果。

---

## 8. 具体テンプレ（抜粋）

**templates/onepager.md**

```md
---
id: tpl-onepager
version: 1.0.0
---
# 1‑Pager｜${title}
- 目的 / 背景
- 決定が必要な論点
- 推奨案（利点/欠点/前提）
- 代替案
- KPIへの影響（測定方法/期間）
- 次アクション（RACI・期限）
```

**prompts/task/sales-intake.md**（短縮）

```md
目的：初回接点で「課題仮説→価値提案→明確なCTA」を提示し、30分ミーティングに合意させる。
入力：会社/役職/業界/過去接点/想定課題/提供価値
出力：メール草案（100–150語）/アジェンダ/確認質問10/CRM項目
品質：返信率・商談化率・所要時間（15分以内）
```

---

## 9. レビュースケジュール（例：ICS）

`automation/review.ics`（抜粋）：

```
BEGIN:VCALENDAR
BEGIN:VEVENT
RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=16;BYMINUTE=30;BYSECOND=0
DESCRIPTION: WBR後のKB反映タイム（進化統括主導）
END:VEVENT
BEGIN:VEVENT
RRULE:FREQ=MONTHLY;BYDAY=MO;BYSETPOS=1;BYHOUR=10;BYMINUTE=0;BYSECOND=0
DESCRIPTION: 月次MBRに向けたSOP/指標の棚卸し
END:VEVENT
END:VCALENDAR
```

---

## 10. 運用ガードレール

- **プライバシー/機密**：`confidentiality` を `public/internal/secret` で分類。publicのみ外部公開。
- **非弁行為の回避**：法務は“論点整理/条項比較/赤入れ案”まで。最終は弁護士レビュー必須。
- **説明責任**：すべての意思決定は`decisions/`にDRを残す。データ出典・更新日を明記。

---

## 11. 学習ループ（WBR→KB反映）

1. WBR（毎週）：KGI/KRの逸脱を検知→根因仮説→対策案→担当RACIを割り当て。
2. KB反映（毎週）：SOP/指標/プレイブックの差分PR→レビュー→CHANGELOG→index再生成。
3. MBR（毎月）：RACI/バックログ/資源配分の見直し→DRに記録。
4. QBR（四半期）：ポートフォリオ/価格/資本政策を再設計→主要プレイブックを更新。

---

## 12. 導入ステップ（最短3日）

- **Day1**：この構成で空リポ作成→`schemas/*`→`scripts/*`配置→`index.json`自動生成確認。
- **Day2**：12人格（personas/*）と主要SOP4本（workflows/*）の初期版を投入。
- **Day3**：OKR/metrics/automationを接続→WBRで反映ルーティン開始。

---

## 13. 参考系統（学術プロベナンス/短縮）

- **Knowledge Management**：ISO 30401、Nonaka-Takeuchi（SECIモデル）、FAIR原則（Findable/Accessible/Interoperable/Reusable）
- **Docs-as-Code**：CI/CD・スキーマ駆動・セマンティックバージョニング
- **Experimentation/因果**：CRISP-DM、実験計画法、Pearl/Rubin

---

## 14. 付録：最小ファイル雛形（コピペ用）

- `personas/persona-integrator.md`（統合応答人格）
- `workflows/sop-sales-intake.md`（新規商談一次対応）
- `decisions/dr-YYYY-MM-DD-*.md`（意思決定ログ）
- `metrics/catalog.yml`（指標カタログ）

> これらを起点に、`scripts/build_index.py` を走らせれば `index.json` が生成され、ChatGPT側の“コンテキストビルド”に使えます。

