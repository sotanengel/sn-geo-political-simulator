# AWS 本番デプロイ（Phase 6）

## 認証（Amazon Cognito）

本番環境では PC コーディング標準に従い、**メールアドレス認証**（Cognito User Pool + メール確認）を API 前段に配置する。

- 開発環境: JWT 検証省略可（要件 15.3）
- 本番: API Gateway + Cognito Authorizer、または FastAPI で JWT 検証ミドルウェア

シークレットは Secrets Manager / SSM Parameter Store で管理し、コードに直書きしない。

## 推奨構成

- ECS Fargate: game-engine, frontend
- ElastiCache Redis: ゲーム状態
- RDS PostgreSQL: 履歴ログ
- CloudFront + ALB

## 関連

- Epic Issue: https://github.com/sotanengel/sn-geo-political-simulator/issues/1
