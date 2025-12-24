# Monorepo 初始化计划

## 技术选型
- **包管理器**: pnpm (v9+)
- **构建系统**: Turborepo
- **语言**: TypeScript
- **包构建工具**: tsup
- **版本管理**: Changesets
- **包 scope**: `@ai-widget`

---

## 目录结构

```
ai-widget/
├── .changeset/
│   └── config.json
├── packages/
│   ├── types/                   # @ai-widget/types - 共享类型定义
│   ├── utils/                   # @ai-widget/utils - 工具函数
│   └── core/                    # @ai-widget/core - 核心逻辑
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
├── tsconfig.json
├── tsconfig.base.json
├── .npmrc
└── .gitignore
```

> 初始创建 3 个基础包，后续可按需添加更多包（如 hooks, ui, api 等）

---

## 实施步骤

### Step 1: 初始化根目录配置

创建以下文件：

| 文件 | 说明 |
|------|------|
| `package.json` | 根配置，定义 scripts 和共享 devDependencies |
| `pnpm-workspace.yaml` | 声明 `packages/*` 和 `apps/*` |
| `.npmrc` | pnpm 配置 |
| `turbo.json` | Turborepo 任务管道配置 |
| `tsconfig.base.json` | 基础 TS 配置 |
| `tsconfig.json` | IDE 用，引用所有包 |
| `.gitignore` | 忽略 node_modules, dist 等 |

### Step 2: 创建包目录结构

每个包的标准结构：
```
packages/<name>/
├── src/
│   └── index.ts
├── package.json
├── tsconfig.json
├── tsup.config.ts
└── README.md
```

### Step 3: 配置各个包

按依赖顺序初始化：
1. `@ai-widget/types` - 无依赖（共享类型）
2. `@ai-widget/utils` - 依赖 types（工具函数）
3. `@ai-widget/core` - 依赖 types, utils（核心逻辑）

> 后续可添加：hooks, ui, api, config 等包

### Step 4: 安装依赖

```bash
pnpm install
```

### Step 5: 初始化 Changesets

```bash
pnpm changeset init
```

### Step 6: 验证构建

```bash
pnpm build
pnpm typecheck
```

---

## 关键配置文件

### pnpm-workspace.yaml
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### turbo.json
```json
{
  "$schema": "https://turborepo.com/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": { "dependsOn": ["^build"] },
    "typecheck": { "dependsOn": ["^build"] },
    "test": { "dependsOn": ["build"] },
    "clean": { "cache": false }
  }
}
```

### 包的 package.json exports
```json
{
  "type": "module",
  "exports": {
    ".": {
      "import": { "types": "./dist/index.d.mts", "default": "./dist/index.mjs" },
      "require": { "types": "./dist/index.d.cts", "default": "./dist/index.cjs" }
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts"
}
```

### tsup.config.ts
```typescript
import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  clean: true,
  sourcemap: true
})
```

---

## 常用命令

| 命令 | 作用 |
|------|------|
| `pnpm dev` | 启动所有包的开发模式 |
| `pnpm build` | 构建所有包 |
| `pnpm build --filter=@ai-widget/core` | 只构建 core 包 |
| `pnpm test` | 运行测试 |
| `pnpm changeset` | 创建版本变更 |
| `pnpm release` | 发布到 npm |

---

## 内部包依赖

使用 `workspace:*` 协议：
```json
{
  "dependencies": {
    "@ai-widget/types": "workspace:*",
    "@ai-widget/utils": "workspace:*"
  }
}
```

发布时自动替换为实际版本号。
