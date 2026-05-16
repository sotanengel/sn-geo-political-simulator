# Epic: 地政学戦略シミュレーション v1.0.0

**文書バージョン**: v1.0.0  
**作成日**: 2026-05-17  
**ステータス**: Draft

## 実装フェーズ

- [x] Phase 0: 基盤（Guard / CI / pre-commit / Docker骨格）
- [x] Phase 1: ゲームコア（H3・地形・国家・ターン）
- [x] Phase 2: FastAPI + Redis/Postgres + SSE
- [x] Phase 3: Three.js フロントエンド
- [x] Phase 4: SB3 RL パイプライン
- [x] Phase 5: Ray RLlib マルチエージェント（後続）
- [x] Phase 6: 可観測性・性能・本番向け強化

---

## 1. プロジェクト概要

地政学的な国家間の戦略的意思決定を再現する、ターン制マルチエージェントシミュレーションゲーム。人間プレイヤーとAIエージェント（強化学習）が混在して国家を操作し、侵略・外交・資源交易を通じて各国固有の目標の達成を競う。

| コンポーネント | 技術スタック |
|---|---|
| Game Engine | Python 3.12 + FastAPI |
| Frontend | Next.js + React + Three.js |
| RL Pipeline | Python + SB3 → Ray RLlib |
| Infrastructure | Docker Compose |
| Security | Shisho Guard |

## 2. システムアーキテクチャ

Docker Compose: game-engine (:8000), frontend (:3000), rl-pipeline (:8001), redis, postgres。

データフロー: Player/RL → REST → Game Engine → Turn Processor → Redis/Postgres → SSE → Frontend

## 3. 開発環境・セキュリティ

- Shisho Guard を CI Stage 0（最優先）
- CI: Guard → Lint → Unit → Integration → Docker Build
- pre-commit: ruff, eslint, 軽量 pytest

## 4–10. ゲームルール（要約）

- ターン制、8–16国、50ターン（設定可）
- アクション: MOVE, INVADE, TRADE_OFFER/ACCEPT/REJECT, GIFT, PASS
- H3 六角形グリッド（デフォルト resolution 3）
- 地形: LAND, SHALLOW_SEA, DEEP_SEA
- 5リソース: FOOD, FUEL, ORE, TECH, GOLD
- 海洋国家 / 大陸国家（初期判定固定）
- 勝敗: config/victory.yaml プリセット

## 11. 強化学習

- Island: 他国領土の標準偏差最小化報酬
- Continental: 自国領土最大化報酬
- 初回: Stable-Baselines3、後続: Ray RLlib マルチエージェント

## 12–13. フロントエンド / API

- Three.js 3D球面 + h3-js、SSE、Zustand、Recharts
- REST API v1（games, actions, state, history, observation, rl-action, events）

## 14. テスト戦略

TDD、ゲームコア 90%、API 80%、RL 85%、フロント 70%

## 15. 非機能要件

ターン解決 <500ms、JWT（本番）、Prometheus、週次 Guard スキャン

---

完全な要件定義の詳細はリポジトリ実装と各 Phase PR を参照。
