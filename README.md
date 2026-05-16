# sn-geo-political-simulator

地政学的な国家間の戦略的意思決定を再現する、ターン制マルチエージェントシミュレーションゲーム。

- **Epic Issue**: [#1](https://github.com/sotanengel/sn-geo-political-simulator/issues/1)
- **Stack**: Python 3.12 (FastAPI) / Next.js 15 (Three.js) / Stable-Baselines3 / Docker Compose

## クイックスタート

```bash
# 依存関係
cd backend && pip install -e ".[dev]"
cd ../frontend && npm install
cd ../rl-pipeline && pip install -e ".[dev]"

# テスト
cd backend && pytest tests/unit -v
cd ../frontend && npm test
cd ../rl-pipeline && pytest tests -v

# Docker Compose
docker compose up --build
```

- Game Engine: http://localhost:8000/health
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Takumi Guard（Shisho）

[クイックスタート](https://shisho.dev/docs/ja/t/guard/quickstart/index.md) に従い設定してください。

```bash
# メール認証トークン（tg_anon_...）は環境変数で渡す（コードに書かない）
export SHISHO_TOKEN=tg_anon_YOUR_TOKEN

cp .npmrc.example .npmrc
# .npmrc の ${SHISHO_TOKEN} を設定

# 確認: 403 でブロックされること
npm install @panda-guard/test-malicious
```

PyPI:

```bash
pip config set global.index-url "https://token:${SHISHO_TOKEN}@pypi.flatt.tech/simple/"
```

## pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## プロジェクト構成

```
backend/       # Game engine (FastAPI + domain logic)
frontend/      # Next.js + Three.js
rl-pipeline/   # Gymnasium + SB3
config/        # Game & victory presets
docs/          # Requirements epic body
```

## 性能ベンチマーク

```bash
cd backend && python ../scripts/benchmark_turn.py
```

## 本番（AWS）

[Cognito メール認証方針](docs/aws-production.md) を参照。

## Ray RLlib（マルチエージェント）

```bash
cd rl-pipeline
python train_rllib.py --num-nations 8
# pip install 'ray[rllib]' でフルトレーニング可能
```

## ライセンス

Apache License 2.0 — see [LICENSE](LICENSE).
