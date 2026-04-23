# Cangjie Skill

本を実行可能な AI スキルのセットに蒸留します。

## なぜこれを作ったのか

最近バズったアイデアがあります：同僚を AI スキルに蒸留する。人が離職しても、その人の経験、口調、仕事のスタイルが AI によってある程度再現できる。[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) はまさにこれを行う——イーロン・マスク skill やウォーレン・バフェット skill のような「人間 skill」を生成します。コンパニオンの [darwin-skill](https://github.com/alchaincyf/darwin-skill) はスキルの自動進化を担当します。

人を蒸留することは価値があります——nuwa-skill がすでにそれを証明しています。その人が**書いたもの**を蒸留することは、補完的な次元です：本は長年の熟考の結晶——慎重な反省の後に抽出された真のエッセンスです。人の表現スタイルを真似するのではなく、体系的に出力された方法論を実問題を解決するツールとして抽出することも、同様に価値のあることです。

また、リアルなペインポイントもあります：多くの本を読んでいても、それを活用できない。知識は「読んだ」レベルに留まり、実際の意思決定で活性化されることがない。本がスキルに蒸留されれば、AIエージェントが実際のシナリオでその知識を呼び出してくれる——ノートに埃をかぶせる代わりに。

だから cangjie-skill の目標は一つ：**蒸留する価値のあるすべての本を蒸留し**、それぞれの高価値な本を、独立して呼び出し可能、組み合わせ可能、ストレステスト可能な AI スキルパックに変えること。

## 解決する問題

- 多くの本を読んでいるが活用できない——知識が「読んだ」レベルに留まり、実際の意思決定で活性化されない
- 本の要約や読書メモは圧縮であって、構造化された再利用ではない——「いつ何を使うべきか」が分からないまま
- 本の中で本当にツールになる価値のある内容はごく一部——厳格なフィルタリングが必要で、全部入りではない
- 既存の読書方法論は人間の読者向けで、エージェントの実行者向けではない——実行志向の蒸留が必要

## どう動くか

cangjie-skill は **RIA-TV++** パイプラインを使用して、本を生のテキストから構造化されたスキルのセットに変換します。6段階のプロセスです：

1. **全書理解（Adler分析）** — モーティマー・アドラーの分析方法で、全書を構造・解釈・批判・応用の4ステップで分解し、`BOOK_OVERVIEW.md` を生成
2. **並行抽出** — 5つの専門エクストラクター（フレームワーク、原則、事例、反例、用語）が同時に実行され、原文から候補ユニットを抽出
3. **三重検証** — 各候補は3つのチェックを通過する必要があります：書中に少なくとも2つの独立した裏付けがあるか（クロスドメイン）、新しい質問に答えられるか（予測力）、常識ではないか（独自性）。合格率は通常25〜50%
4. **RIA++ 構築** — 検証済みの内容を6つの次元に構造化：R（原文引用）/ I（自分の言葉での再構築）/ A1（書中の事例）/ A2（将来のトリガーシーン）/ E（実行可能ステップ）/ B（境界と盲点）
5. **ツェッテルカステン連携** — スキル間の依存、対比、構成関係を特定し、参照グラフ付きの `INDEX.md` を生成
6. **ストレステスト** — 各スキルに囮問題を含むテストプロンプトを設計。不合格は全面的に再構築

RIA-TV++ の名前の由来：
- **RIA**：趙周のブックマーク法（Reading / Interpretation / Appropriation）
- **TV**：Triple Verification（三重検証）
- **++**：エージェント実行向けの拡張——E（Execution）+ B（Boundary）

## 効果例

### 例1：本からスキルパックへ

**ユーザーの要望**

「本のコア方法論を再利用可能な AI スキルにしたい。読書要約ではなく。」

**cangjie-skill の判断**

- 元資料に再利用可能な方法論ユニットがあるか確認
- スタンドアロンのスキルに値するものと背景情報を区別
- 単一の要約ではなく、構造化されたスキルリポジトリを出力

**出力例**

> 結果は1つの要約ファイルではなく、`BOOK_OVERVIEW.md`、`INDEX.md`、複数の `*/SKILL.md`、トリガー検証用の `test-prompts.json` を含む multi-skill リポジトリになります。

### 例2：圧縮ではなく、構造化再利用

**ユーザーの要望**

「長い説明文が欲しいのではなく、エージェントが再利用できるスキルパックが欲しい。」

**cangjie-skill の判断**

- 目標は構造化再利用であり、物語の圧縮ではない
- トリガー可能、組み合わせ可能、テスト可能なスキルユニットを優先
- スタンドアロンのスキルに値しない素材は落とす

**出力例**

> システムはトリガー条件、境界、実行パターン、関連スキルリンクを持つ複数のスキルモジュールを生成します——全体を1つの汎用的なノートに平坦化するのではなく。

## 生成済みスキルパック

| リポジトリ | 元資料 | スキル数 |
|------------|--------|----------|
| [buffett-letters-skill](https://github.com/kangarooking/buffett-letters-skill) | バフェットの株主への手紙（1957-2023） | 20 |
| [cognitive-dividend-skill](https://github.com/kangarooking/cognitive-dividend-skill) | 認知の红利 | 15 |
| [duan-yongping-skill](https://github.com/kangarooking/duan-yongping-skill) | 段永平の投資Q&A（ビジネス+投資ロジック） | 15 |
| [poor-charlies-almanack-skill](https://github.com/kangarooking/poor-charlies-almanack-skill) | 貧しきチャーリーの格言 | 12 |
| [no-rules-rules-skill](https://github.com/kangarooking/no-rules-rules-skill) | No Rules Rules | 10 |
| 黄帝内経・素問（本プロジェクト内） | 『黄帝内経・素問』 | 10 |
| 黄帝内経・霊枢（本プロジェクト内） | 『黄帝内経・霊枢』 | 8 |

より多くの高価値な本の蒸留を計画中。

追加の外部ソース（著者本人の許可を得て掲載）：

- 元リポジトリ: [ace3000chao/book2startup](https://github.com/ace3000chao/book2startup)
- 書目: 『リーン・スタートアップ』『孫子兵法』『荘子』『易経』

## リポジトリ構造

```text
cangjie-skill/
├── README.md              ← 今見ているファイル
├── README.en.md           ← 英語版
├── README.ja.md           ← 日本語版
├── LICENSE                ← MIT
├── SKILL.md               ← メタスキル定義（book2skill の完全な実行仕様）
├── methodology/           ← RIA-TV++ の段階別方法論ドキュメント
├── extractors/            ← 5つの並行エクストラクターのプロンプト定義
└── templates/             ← SKILL.md / INDEX.md / BOOK_OVERVIEW.md テンプレート
```

## エコシステム

cangjie-skill はより大きなスキルエコシステムの一部です：

- [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) — 人を蒸留する（思考スタイル、表現 DNA）
- **cangjie-skill**（このリポジトリ）— 本を蒸留する（方法論、フレームワーク、原則）
- [darwin-skill](https://github.com/alchaincyf/darwin-skill) — 任意のスキルを進化させる

これらは連携しています：nuwa は人を蒸留し、cangjie は本を蒸留し、darwin はそれらを進化させ続けます。

## More Skills

- [Buffett Letters Skill](https://github.com/kangarooking/buffett-letters-skill) — バフェットの60年以上の株主への手紙から抽出した20個の投資判断スキル
- [Poor Charlie's Almanack Skill](https://github.com/kangarooking/poor-charlies-almanack-skill) — チャーリー・マンガーのコア思考法から抽出した12個の意思決定・判断スキル
- [No Rules Rules Skill](https://github.com/kangarooking/no-rules-rules-skill) — ネットフリックスの自由と責任の文化から抽出した10個の組織設計スキル
- [Cognitive Dividend Skill](https://github.com/kangarooking/cognitive-dividend-skill) — 『認知の红利』から抽出した15個の認知ツールスキル
- [Duan Yongping Skill](https://github.com/kangarooking/duan-yongping-skill) — 段永平の投資Q&Aから抽出した15個のビジネス・投資スキル
- Huangdi Neijing Suwen Skill（本プロジェクト内）— 『黄帝内経・素問』から抽出した10個の中医観察・調整スキル
- Huangdi Neijing Lingshu Skill（本プロジェクト内）— 『黄帝内経・霊枢』から抽出した8個の心身調整・弁証スキル

External Source（著者本人の許可を得て掲載）:

- [book2startup](https://github.com/ace3000chao/book2startup) — 『リーン・スタートアップ』『孫子兵法』『荘子』『易経』を蒸留した skills を含む

## 作者について

**袋鼠帝 kangarooking** — AI ブロガー、インディー開発者。AI Top 公式アカウント「袋鼠帝 AI 客栈」主宰

Volcengine ナビゲーション KOL、Baidu Qianfan 開発者アンバサダー、GLM エバンジェリスト、Trae 昆明初代 Fellow

| プラットフォーム | リンク |
|------------------|--------|
| 𝕏 Twitter | https://x.com/aikangarooking |
| 小紅書 | https://xhslink.com/m/5YejKvIDBbL |
| 抖音 | https://v.douyin.com/hYpsjphuuKc |
| WeChat 公式アカウント | 袋鼠帝 AI 客栈 |
| WeChat ビデオチャンネル | AI 袋鼠帝 |

WeChat 公式アカウント「袋鼠帝 AI 客栈」QR コード:

![](https://raw.githubusercontent.com/kangarooking/cangjie-skill/main/assets/kangarooking-gzh.png)

## License

MIT. See [LICENSE](./LICENSE).
