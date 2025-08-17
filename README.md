# KB Pages (Ultra Hardened)
最終更新: 2025-08-17

**“手当ゼロ・事故ゼロ”**を目標に、CIで次を自動化：
- 個人メモ除外・その他は**自動公開**（不足FM注入）
- Obsidianの**[[wikilinks]] をMarkdownへ**解決（未解決はテキスト化）
- **Liquid/リンク**：全角→ASCII、擬似Liquid補正、絶対パス→relative_url
- **画像最適化**（JPEG/PNG）
- **検索インデックス**（permalink優先）
- **url/baseurl自動生成**（env override可）
- **内部リンク断/大小文字衝突/シークレット漏洩**のブロック
- **10MB超アセット警告**（`ASSET_LIMIT_MB` 環境変数で変更）
