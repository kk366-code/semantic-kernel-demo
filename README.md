# FastAPI Semantic Kernel MVP

FastAPI、Semantic Kernel、Azure OpenAI、Postgres + pgvector を段階的に組み合わせるためのサンプルアプリケーションです。最初のマイルストーンでは、開発ルール、Python ツール設定、最小 REST API、テストを用意しています。

## 現在の範囲

- FastAPI のアプリケーションファクトリ
- 最小限の HTMX チャット・エージェント画面
- `GET /health`
- Semantic Kernel + Azure OpenAI 用の `POST /chat` API
- Semantic Kernel `ChatCompletionAgent` 用の `POST /agent` API
- Azure OpenAI 設定ローダー
- pytest による API テスト
- Ruff によるフォーマット・lint 設定
- `uv` ベースの依存関係管理
- 将来の Postgres/pgvector 用の環境変数プレースホルダー

Azure OpenAI の環境変数を設定すると、`/chat` は Semantic Kernel 経由でチャット用デプロイを呼び出します。`/agent` は `ProjectGuideAgent` を使って、このサンプルアプリの API、開発コマンド、品質確認、現在の構成を案内します。RAG、DB マイグレーション、Azure CLI を実行するエージェントツール、複数エージェント連携は今後のマイルストーンで追加します。

## 必要なもの

- Python 3.12 以上
- `uv`

## セットアップ

```bash
uv sync
cp .env.example .env
uv run pre-commit install
```

このプロジェクトでは、pre-commit の秘密情報スキャナーとして Gitleaks を使います。hook をインストールする前に `gitleaks` CLI をインストールしてください。

```bash
brew install gitleaks
```

## 起動方法

```bash
uv run fastapi dev src/semantic_kernel_api/main.py
```

別の起動方法:

```bash
uv run uvicorn semantic_kernel_api.main:app --app-dir src --reload
```

起動後、以下を開きます。

- チャット・エージェント画面: http://127.0.0.1:8000/
- API ドキュメント: http://127.0.0.1:8000/docs
- ヘルスチェック: http://127.0.0.1:8000/health

## チャット・エージェント画面

ルートページには、通常のチャットエンドポイントと `ProjectGuideAgent` をブラウザで試すための最小限の HTMX フォームがあります。

```text
http://127.0.0.1:8000/
```

Azure OpenAI が設定されていない場合、ページには不足している環境変数が表示されます。各フォームは `503` の結果 fragment を表示します。

## チャット API

Azure OpenAI の設定がある場合:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "content-type: application/json" \
  -d '{"message":"Semantic Kernelとは何ですか？"}'
```

レスポンス:

```json
{
  "answer": "..."
}
```

Azure OpenAI の設定が足りない場合は `503 Service Unavailable` を返し、不足している環境変数名を `missing_settings` に含めます。

## エージェント API

`/agent` は、Semantic Kernel の `ChatCompletionAgent` と読み取り専用の小さな `ProjectGuidePlugin` を使います。最初のエージェントは、このサンプルプロジェクトのアプリ案内役です。現在のエンドポイント、開発コマンド、品質確認、現在のアーキテクチャについて回答できます。この MVP では Azure CLI コマンド、RAG、複数エージェント連携は実行しません。

Azure OpenAI の設定がある場合:

```bash
curl -X POST http://127.0.0.1:8000/agent \
  -H "content-type: application/json" \
  -d '{"message":"このアプリで試せるAPIを教えて"}'
```

レスポンス:

```json
{
  "answer": "...",
  "agent_name": "ProjectGuideAgent"
}
```

`/chat` と `/agent` の違いは、`/chat` が単純な Semantic Kernel チャットサービスに 1 メッセージを送るのに対し、`/agent` は名前、指示、読み取り専用のプロジェクト案内ツールを持つ `ChatCompletionAgent` を使う点です。

## 品質確認

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run pre-commit run --all-files
```

## 初期アーキテクチャ

```text
src/semantic_kernel_api/
├── __init__.py
├── config.py        # pydantic-settings ベースのアプリ設定
├── main.py          # FastAPI アプリファクトリと API ルート
├── schemas.py       # リクエスト/レスポンスモデル
├── static/
│   └── styles.css   # 最小限のチャット・エージェント画面スタイル
├── templates/       # Jinja2 + HTMX テンプレート
└── services/
    ├── agent.py     # Semantic Kernel ChatCompletionAgent と案内プラグイン
    └── chat.py      # Semantic Kernel チャットサービス境界

tests/
├── test_agent.py    # フェイクサービスを使った agent エンドポイントテスト
├── test_chat.py     # フェイクサービスを使った chat エンドポイントテスト
├── test_health.py   # HTTP レベルの health エンドポイントテスト
└── test_ui.py       # HTMX ページと fragment テスト
```

今後の追加予定:

- Postgres + pgvector の永続化
- ドキュメント取り込みと RAG チャットエンドポイント

## 環境変数

予定している設定名は `.env.example` を参照してください。実際の秘密情報は、ローカルの `.env` ファイルまたはデプロイ先のシークレットストアにのみ保存してください。

`/chat` と `/agent` に必要な最小変数:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`: 任意。ただし Azure リソースが特定の API バージョンを必要とする場合は設定を推奨します。
