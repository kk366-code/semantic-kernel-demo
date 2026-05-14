# FastAPI Semantic Kernel MVP

FastAPI, Semantic Kernel, Azure OpenAI, and Postgres + pgvector を段階的に組み合わせるためのサンプルアプリケーションです。最初のマイルストーンでは、開発ルール、Python tooling、最小 REST API、テストを用意しています。

## 現在の範囲

- FastAPI の app factory
- 最小構成の HTMX チャット画面
- `GET /health`
- Semantic Kernel + Azure OpenAI 用の `POST /chat` API
- Azure OpenAI 設定の読み込み
- pytest による API テスト
- Ruff によるフォーマット・リント設定
- `uv` による依存関係管理
- 将来の Postgres/pgvector 用の環境変数プレースホルダー

Azure OpenAI の環境変数を設定すると、`/chat` は Semantic Kernel 経由で chat deployment を呼び出します。RAG、AIエージェント機能、DB migration は次のマイルストーンで追加します。

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

## 起動

```bash
uv run fastapi dev src/semantic_kernel_api/main.py
```

代替コマンド:

```bash
uv run uvicorn semantic_kernel_api.main:app --app-dir src --reload
```

起動後、以下を開きます。

- チャット画面: http://127.0.0.1:8000/
- API ドキュメント: http://127.0.0.1:8000/docs
- ヘルスチェック: http://127.0.0.1:8000/health

## チャット画面

ルートページでは、ブラウザからチャットAPIを試すための最小構成の HTMX フォームを提供します。

```text
http://127.0.0.1:8000/
```

Azure OpenAI が未設定の場合、画面には不足している環境変数が表示され、フォーム送信時には `503` の結果フラグメントが返ります。

## チャットAPI

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

## 品質チェック

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
├── main.py          # FastAPI app factory と API ルート
├── schemas.py       # リクエスト/レスポンスモデル
├── static/
│   └── styles.css   # 最小チャット画面のスタイル
├── templates/       # Jinja2 + HTMX テンプレート
└── services/
    └── chat.py      # Semantic Kernel チャットサービス境界

tests/
├── test_chat.py     # fake service を使ったチャットAPIテスト
├── test_health.py   # HTTPレベルのヘルスチェックテスト
└── test_ui.py       # HTMXページとフラグメントのテスト
```

今後追加する予定のもの:

- Postgres + pgvector による永続化
- ドキュメント投入と RAG チャットエンドポイント

## 環境変数

設定名は `.env.example` を参照してください。実際のシークレット値は、ローカルの `.env` またはデプロイ先のシークレットストアにのみ保存します。

`/chat` に最低限必要な環境変数:

- `AZURE_OPENAI_ENDPOINT` または `AZURE_OPENAI_BASE_URL`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`

### Azure OpenAI の設定手順

1. Azure AI Foundry を開きます。
2. このアプリで使うプロジェクトまたは Azure OpenAI リソースを選択します。
3. リソース詳細またはデプロイ詳細を開き、endpoint またはターゲットURIをコピーします。
   - `AZURE_OPENAI_ENDPOINT` に設定します。
   - `https://<resource-name>.openai.azure.com/` のような形式です。
   - Foundry のデプロイ画面で `https://<resource-name>.cognitiveservices.azure.com/...` 形式のターゲットURIだけが表示される場合は、`AZURE_OPENAI_BASE_URL` に設定します。
4. 同じリソースのキー管理ページを開き、API key を1つコピーします。
   - `AZURE_OPENAI_API_KEY` に設定します。
   - 実際のキーはコミットしないでください。
5. API version を設定します。
   - Microsoft Learn の REST API reference に記載されている GA の inference API version を使います。
   - このサンプルでは、まず `2024-10-21` を使います。
6. **Deployments** または **Model deployments** を開きます。
7. デプロイが存在しない場合は、チャット用モデルのデプロイを作成します。
   - `gpt-4o-mini` などのチャット対応モデルを選びます。
   - `chat` などの deployment name を設定します。
8. deployment name をコピーします。
   - `AZURE_OPENAI_CHAT_DEPLOYMENT` に設定します。
   - これはモデル名ではなく、デプロイ名です。
9. `.env` を変更したら FastAPI サーバーを再起動します。

`.env` の例:

```env
AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_CHAT_DEPLOYMENT=chat
```

`AZURE_OPENAI_BASE_URL` を使わない場合は、`.env` に空行として残さず削除またはコメントアウトしてください。

Foundry のターゲットURIを使う場合:

```env
AZURE_OPENAI_BASE_URL=https://<resource-name>.cognitiveservices.azure.com/openai/deployments/<deployment-name>
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_CHAT_DEPLOYMENT=<deployment-name>
```

`DeploymentNotFound` が出る場合は、以下を確認してください。

- Azure AI Foundry にデプロイが存在すること。
- `AZURE_OPENAI_CHAT_DEPLOYMENT` が deployment name と完全一致していること。
- `AZURE_OPENAI_ENDPOINT` が、そのデプロイを持つ同じリソースを指していること。
- 新しいデプロイを作成した直後の場合、数分待ってから再試行していること。
