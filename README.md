# KB + GitHub Pages（Hardened 自動配信）
最終更新: 2025-08-17

この構成は、よく出るバグを**事前に防ぐ/自動で修復**します。

## 防ぐもの
- `confidentiality: public` の**誤配置/未設定**（lintでfail）
- Liquidの**全角引用符**や `/kb/` 直書き等 → **自動でASCII化/relative_url化**
- **baseurl未設定**（リポジトリから自動検出してJekyllに統合）
- **index.md欠落**（公開抽出時に index.md のstubを自動生成）
- **内部リンク切れ**（ビルド後に _site をクロールしてチェック）
- **巨大アセット**（>10MBはwarning）

## 使い方
1. リポジトリ直下にこの内容を展開して上書き
2. GitHub → Settings → Pages → **Build and deployment = GitHub Actions**
3. `main` にpush → lint→抽出→整形→索引→Jekyll→リンク検査→デプロイ の順で自動実行
