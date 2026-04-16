# Cangjie Skill

本を再利用可能な AI skill に変換するための生成ワークフローです。

`cangjie-skill` は、このワークスペース内の skill pack リポジトリを生み出す上流システムです。主にエンドユーザー向けの単体 skill ではなく、長文の材料から構造化された skill を生成するための制作ワークフローです。

## できること

- 原則、フレームワーク、事例、反例、用語を抽出する
- standalone skill にする前に候補を絞り込む
- 選ばれた単位を統一された `SKILL.md` 形式へ変換する
- 関連 skill をグラフとして接続する
- `BOOK_OVERVIEW.md`、`INDEX.md`、`test-prompts.json` を生成する

## パイプライン

1. Stage 0: 本全体の理解
2. Stage 1: 並列抽出
3. Stage 1.5: 検証と絞り込み
4. Stage 2: RIA++ skill 構築
5. Stage 3: グラフ連結
6. Stage 4: 圧力テスト

## すでに生成したもの

- `poor-charlies-almanack-skill`
- `no-rules-rules-skill`

## 効果例

### 例 1

**ユーザーの要望**

「本を長い要約ではなく、再利用可能な AI skill にしたい」

**cangjie-skill がどう判断するか**

- 元資料に再利用できる方法論単位があるか確認する
- standalone にすべき skill と背景情報を分ける
- 単一の要約ではなく構造化された skill リポジトリを出力する

**最終出力の例**

「結果は 1 つの要約ファイルではなく、`BOOK_OVERVIEW.md`、`INDEX.md`、複数の `*/SKILL.md`、そしてトリガー検証用の `test-prompts.json` を含む multi-skill repository になります。」

### 例 2

**ユーザーの要望**

「agent が何度も再利用できるものがほしい」

**cangjie-skill がどう判断するか**

- 説明文の圧縮ではなく構造化再利用を優先する
- trigger 可能で、組み合わせ可能で、テスト可能な unit を優先する
- 独立 skill に値しない材料は落とす

**最終出力の例**

「システムは trigger 条件、適用境界、実行パターン、関連 skill リンクを持つ複数の skill module を生成し、1 本の汎用的な要約にはしません。」

## リポジトリ構成

```text
cangjie-skill/
├── README.md
├── README.en.md
├── README.ja.md
├── LICENSE
├── GITHUB_REPO.md
├── SKILL.md
├── methodology/
├── extractors/
└── templates/
```

## More Skills

- `poor-charlies-almanack-skill`
  `https://github.com/kangarooking/poor-charlies-almanack-skill`
- `no-rules-rules-skill`
  `https://github.com/kangarooking/no-rules-rules-skill`

## License

MIT. 詳しくは [LICENSE](./LICENSE) を参照してください。
