#!/usr/bin/env npx tsx

/**
 * 保存 Playwright 认证状态（使用 Clerk Testing）
 *
 * 使用方法：
 *   npx tsx ~/.claude/skills/save-auth/scripts/save-auth.ts <project-root> [user-type]
 *
 * 参数：
 *   project-root: 项目根目录
 *   user-type: 可选，指定用户类型 (user, admin, 或 all)
 *              默认为 all，会创建所有配置的用户认证
 *
 * 项目约定：
 *   - 结构: <root>/web/ (Next.js 应用)
 *   - 配置: <root>/.claude/config.local.json
 *   - 环境: <root>/web/.env.local
 *     - E2E_CLERK_USER_USERNAME=test@example.com → .auth/user.json
 *     - E2E_CLERK_ADMIN_USERNAME=admin@example.com → .auth/admin.json
 *   - 认证: <root>/.auth/*.json
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const PROJECT_ROOT = path.resolve(process.argv[2] || process.cwd());
const USER_TYPE = process.argv[3] || 'all'; // user, admin, or all

// 用户类型映射：环境变量名 → 输出文件名
interface UserConfig {
  envKey: string;
  fileName: string;
  displayName: string;
}

const USER_CONFIGS: UserConfig[] = [
  { envKey: 'E2E_CLERK_USER_USERNAME', fileName: 'user.json', displayName: '普通用户' },
  { envKey: 'E2E_CLERK_ADMIN_USERNAME', fileName: 'admin.json', displayName: '管理员' },
];

// 项目约定检查
function checkProjectConventions() {
  console.log('\n🔍 检查项目约定...\n');

  const errors: string[] = [];
  const warnings: string[] = [];

  // 1. 检查项目根目录
  if (!fs.existsSync(PROJECT_ROOT)) {
    errors.push(`项目目录不存在: ${PROJECT_ROOT}`);
  }

  // 2. 检查 web/ 目录结构
  const webDir = path.join(PROJECT_ROOT, 'web');
  if (!fs.existsSync(webDir)) {
    errors.push('缺少 web/ 目录（约定：Next.js 应用在 web/ 下）');
  }

  // 3. 检查 package.json
  const packageJson = path.join(webDir, 'package.json');
  if (fs.existsSync(webDir) && !fs.existsSync(packageJson)) {
    errors.push('缺少 web/package.json');
  } else if (fs.existsSync(packageJson)) {
    const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf8'));
    const deps = { ...pkg.dependencies, ...pkg.devDependencies };

    // 检查技术栈
    if (!deps['next']) {
      warnings.push('未检测到 Next.js（约定：使用 Next.js 框架）');
    }
    if (!deps['@playwright/test']) {
      warnings.push('未安装 @playwright/test（将自动安装）');
    }
    if (!deps['@clerk/testing']) {
      warnings.push('未安装 @clerk/testing（将自动安装）');
    }
  }

  // 4. 检查配置文件
  const configFile = path.join(PROJECT_ROOT, '.claude/config.local.json');
  if (!fs.existsSync(configFile)) {
    warnings.push('缺少 .claude/config.local.json（将使用默认端口 3000）');
  } else {
    try {
      const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
      if (!config.ports?.dev) {
        warnings.push('config.local.json 缺少 ports.dev（将使用默认端口 3000）');
      } else {
        console.log(`   ✅ 端口配置: ${config.ports.dev}`);
      }
    } catch {
      errors.push('.claude/config.local.json 格式错误');
    }
  }

  // 5. 检查环境变量（检查 .env 和 .env.local）
  const envFile = path.join(webDir, '.env');
  const envLocalFile = path.join(webDir, '.env.local');

  let envContent = '';
  if (fs.existsSync(envFile)) {
    envContent += fs.readFileSync(envFile, 'utf8');
  }
  if (fs.existsSync(envLocalFile)) {
    envContent += fs.readFileSync(envLocalFile, 'utf8');
  }

  if (!envContent) {
    errors.push('缺少 web/.env 或 web/.env.local');
  } else {
    // 检查是否至少有一个用户配置
    const hasAnyUser = USER_CONFIGS.some(c => envContent.includes(c.envKey));
    if (!hasAnyUser) {
      errors.push('缺少任何 E2E 用户配置（E2E_CLERK_USER_USERNAME 或 E2E_CLERK_ADMIN_USERNAME）');
    } else {
      USER_CONFIGS.forEach(config => {
        if (envContent.includes(config.envKey)) {
          console.log(`   ✅ ${config.envKey} 已配置 (${config.displayName})`);
        }
      });
    }
    if (!envContent.includes('CLERK_SECRET_KEY')) {
      errors.push('缺少 CLERK_SECRET_KEY');
    } else {
      console.log('   ✅ CLERK_SECRET_KEY 已配置');
    }
  }

  // 6. 检查 .auth 目录
  const authDir = path.join(PROJECT_ROOT, '.auth');
  if (!fs.existsSync(authDir)) {
    console.log('   📁 .auth/ 目录不存在，将自动创建');
  } else {
    console.log('   ✅ .auth/ 目录存在');
  }

  // 输出检查结果
  if (errors.length > 0) {
    console.log('\n❌ 项目不符合约定：\n');
    errors.forEach(e => console.log(`   • ${e}`));
    console.log('\n📋 约定要求：');
    console.log('   • 项目结构: <root>/web/ (Next.js 应用)');
    console.log('   • 配置文件: <root>/.claude/config.local.json');
    console.log('   • 环境变量: web/.env.local');
    console.log('     - E2E_CLERK_USER_USERNAME=test@example.com');
    console.log('     - CLERK_SECRET_KEY=sk_test_xxx');
    console.log('   • 认证保存: <root>/.auth/user.json');
    console.log('');
    process.exit(1);
  }

  if (warnings.length > 0) {
    console.log('\n⚠️  警告：\n');
    warnings.forEach(w => console.log(`   • ${w}`));
  }

  console.log('\n✅ 项目约定检查通过\n');
}

// 检查并安装依赖
function checkDependencies() {
  const webDir = path.join(PROJECT_ROOT, 'web');
  const packageJson = path.join(webDir, 'package.json');

  const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf8'));
  const deps = { ...pkg.dependencies, ...pkg.devDependencies };

  const missing: string[] = [];
  if (!deps['@playwright/test']) missing.push('@playwright/test');
  if (!deps['@clerk/testing']) missing.push('@clerk/testing');
  if (!deps['dotenv']) missing.push('dotenv');

  if (missing.length > 0) {
    console.log(`📦 安装缺失依赖: ${missing.join(', ')}...\n`);
    execSync(`npm install -D ${missing.join(' ')}`, { cwd: webDir, stdio: 'inherit' });
  }

  // 检查浏览器是否安装
  try {
    execSync('npx playwright install chromium', { cwd: webDir, stdio: 'inherit' });
  } catch {
    // 忽略，可能已安装
  }
}

// 执行检查
checkProjectConventions();
checkDependencies();

// 动态加载项目依赖
const webDir = path.join(PROJECT_ROOT, 'web');
const nodeModules = path.join(webDir, 'node_modules');

const { chromium } = require(path.join(nodeModules, '@playwright/test'));
const { clerkSetup, clerk, setupClerkTestingToken } = require(path.join(nodeModules, '@clerk/testing/playwright'));
const dotenv = require(path.join(nodeModules, 'dotenv'));

const CONFIG_FILE = path.join(PROJECT_ROOT, '.claude/config.local.json');
const AUTH_DIR = path.join(PROJECT_ROOT, '.auth');

// 加载环境变量
dotenv.config({ path: path.join(webDir, '.env') });
dotenv.config({ path: path.join(webDir, '.env.local') });

// 调试：检查 CLERK_SECRET_KEY 是否加载
const hasClerkKey = !!process.env.CLERK_SECRET_KEY;
if (!hasClerkKey) {
  console.error('❌ CLERK_SECRET_KEY 未加载');
  process.exit(1);
}

// 读取端口配置
function getPort(): number {
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    return config.ports?.dev || 3000;
  } catch {
    return 3000;
  }
}

// 获取需要处理的用户列表
function getUsersToProcess(): UserConfig[] {
  if (USER_TYPE === 'all') {
    return USER_CONFIGS.filter(c => process.env[c.envKey]);
  }
  const config = USER_CONFIGS.find(c => c.fileName.startsWith(USER_TYPE));
  if (config && process.env[config.envKey]) {
    return [config];
  }
  return [];
}

// 登录单个用户并保存认证状态
async function loginAndSave(
  browser: any,
  baseUrl: string,
  userConfig: UserConfig
): Promise<boolean> {
  const email = process.env[userConfig.envKey];
  const authFile = path.join(AUTH_DIR, userConfig.fileName);

  console.log(`\n${'─'.repeat(40)}`);
  console.log(`👤 ${userConfig.displayName}: ${email}`);
  console.log(`${'─'.repeat(40)}`);

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 设置 Clerk Testing Token
    await setupClerkTestingToken({ page });

    // 导航到登录页面（带语言前缀避免重定向）
    await page.goto(`${baseUrl}/zh/sign-in`, { waitUntil: 'domcontentloaded' });

    // 使用 Clerk 登录
    console.log('   🔐 正在登录...');
    await clerk.signIn({
      page,
      signInUrl: `${baseUrl}/zh/sign-in`,
      emailAddress: email,
    });
    console.log('   ✅ signIn 完成');

    // 导航到受保护页面验证登录
    console.log('   📍 验证登录状态...');
    await page.goto(`${baseUrl}/zh/chat`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    const currentUrl = page.url();
    if (currentUrl.includes('sign-in')) {
      throw new Error('登录失败：被重定向回登录页');
    }

    console.log('   ✅ 登录成功！');

    // 保存认证状态
    await context.storageState({ path: authFile });

    const stats = fs.statSync(authFile);
    const sizeKB = Math.round(stats.size / 1024);

    console.log(`   📁 已保存: ${authFile} (${sizeKB}KB)`);
    return true;

  } catch (error) {
    console.error(`   ❌ 登录失败: ${error}`);
    return false;
  } finally {
    await context.close();
  }
}

async function main() {
  const port = getPort();
  const baseUrl = `http://localhost:${port}`;
  const usersToProcess = getUsersToProcess();

  if (usersToProcess.length === 0) {
    console.error('❌ 没有找到可处理的用户配置');
    console.error('   请在 web/.env.local 中配置:');
    console.error('   - E2E_CLERK_USER_USERNAME=test@example.com');
    console.error('   - E2E_CLERK_ADMIN_USERNAME=admin@example.com');
    process.exit(1);
  }

  console.log('='.repeat(50));
  console.log('🔐 Save Auth - Clerk Testing 自动认证');
  console.log('='.repeat(50));
  console.log(`   项目: ${PROJECT_ROOT}`);
  console.log(`   端口: ${port}`);
  console.log(`   用户: ${usersToProcess.length} 个`);
  usersToProcess.forEach(u => {
    console.log(`         - ${u.displayName}: ${process.env[u.envKey]}`);
  });
  console.log('='.repeat(50));

  // 确保 .auth 目录存在
  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  // 配置 Clerk
  await clerkSetup();

  // 启动浏览器（headless 模式，全自动）
  console.log('\n🚀 启动浏览器...');
  const browser = await chromium.launch({ headless: true });

  const results: { user: string; success: boolean }[] = [];

  try {
    for (const userConfig of usersToProcess) {
      const success = await loginAndSave(browser, baseUrl, userConfig);
      results.push({ user: userConfig.displayName, success });
    }
  } finally {
    await browser.close();
  }

  // 输出汇总
  console.log('\n');
  console.log('='.repeat(50));
  console.log('📊 认证保存结果:');
  console.log('');
  results.forEach(r => {
    const icon = r.success ? '✅' : '❌';
    console.log(`   ${icon} ${r.user}`);
  });
  console.log('='.repeat(50));

  const failCount = results.filter(r => !r.success).length;
  if (failCount > 0) {
    console.error(`\n❌ ${failCount} 个用户登录失败`);
    process.exit(1);
  }

  console.log('\n✅ 所有用户认证状态已保存！\n');
}

main().catch(console.error);
