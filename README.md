# KB + GitHub Pages 一体スタータ
最終更新: 2025-08-17

- `kb/`: Obsidian用のフルVault（internal/secret含む）
- `docs/`: GitHub Pages公開サイト（**publicのみ**が入る）
- `.github/workflows/publish_public.yml`: Actionsで `kb/` → `docs/kb/` に **publicだけ同期**して公開
- `scripts/`: 公開同期・簡易検索インデックス生成スクリプト

## 使い方
1. このリポジトリをGitHubへpush
2. GitHub → **Settings > Pages > Build and deployment** を **GitHub Actions** に設定
3. `main` にpushするとActionsが走り、**publicだけ**公開されます

### 公開の判定
各MarkdownのFront Matterで `confidentiality: public|internal|secret` を必ず指定。
- `public` だけが `docs/kb/` にコピーされます（個人メモは `internal`/`secret` に）

### Project Pages（ユーザー.github.io ではない通常リポジトリ）のとき
`docs/_config.yml` の `url` と `baseurl` を設定してください（コメントを外して値を入れる）。

---
