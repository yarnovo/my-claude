#!/usr/bin/env npx tsx

/**
 * 创建 Clerk 测试用户
 *
 * 使用方法：
 *   npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts <project-root> [options]
 *
 * 选项：
 *   --email       用户邮箱 (默认: test@example.com)
 *   --password    用户密码 (默认: Test123456!)
 *   --first-name  名 (默认: Test)
 *   --last-name   姓 (默认: User)
 *   --type        用户类型 user/admin (默认: user)
 *   --save-auth   创建后保存认证状态
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options: Record<string, string | boolean> = {
    email: 'test@example.com',
    password: 'Test123456!',
    'first-name': 'Test',
    'last-name': 'User',
    type: 'user',
    'save-auth': false,
  };

  let projectRoot = process.cwd();

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      if (key === 'save-auth') {
        options[key] = true;
      } else if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        options[key] = args[++i];
      }
    } else if (i === 0 && !arg.startsWith('--')) {
      projectRoot = path.resolve(arg);
    }
  }

  return { projectRoot, options };
}

const { projectRoot: PROJECT_ROOT, options } = parseArgs();
const WEB_DIR = path.join(PROJECT_ROOT, 'web');
const ENV_FILE = path.join(WEB_DIR, '.env');
const ENV_LOCAL_FILE = path.join(WEB_DIR, '.env.local');

// 读取环境变量
function loadEnv(): Record<string, string> {
  const env: Record<string, string> = {};

  [ENV_FILE, ENV_LOCAL_FILE].forEach((file) => {
    if (fs.existsSync(file)) {
      const content = fs.readFileSync(file, 'utf8');
      content.split('\n').forEach((line) => {
        const match = line.match(/^([^#=]+)=(.*)$/);
        if (match) {
          let value = match[2].trim();
          // 去掉引号
          if ((value.startsWith('"') && value.endsWith('"')) ||
              (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
          }
          env[match[1].trim()] = value;
        }
      });
    }
  });

  return env;
}

// 更新 .env.local 文件
function updateEnvLocal(key: string, value: string) {
  let content = '';
  if (fs.existsSync(ENV_LOCAL_FILE)) {
    content = fs.readFileSync(ENV_LOCAL_FILE, 'utf8');
  }

  const lines = content.split('\n');
  let found = false;

  const newLines = lines.map((line) => {
    if (line.startsWith(`${key}=`)) {
      found = true;
      return `${key}=${value}`;
    }
    return line;
  });

  if (!found) {
    newLines.push(`${key}=${value}`);
  }

  fs.writeFileSync(ENV_LOCAL_FILE, newLines.join('\n').trim() + '\n');
}

// 调用 Clerk API 创建用户
async function createClerkUser(
  secretKey: string,
  email: string,
  password: string,
  firstName: string,
  lastName: string
): Promise<{ success: boolean; userId?: string; error?: string }> {
  const response = await fetch('https://api.clerk.com/v1/users', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${secretKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email_address: [email],
      password,
      first_name: firstName,
      last_name: lastName,
      skip_password_checks: true,
      skip_password_requirement: false,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    // 检查是否是邮箱已存在的错误
    if (error.errors?.[0]?.code === 'form_identifier_exists') {
      return { success: false, error: 'USER_EXISTS' };
    }
    return { success: false, error: JSON.stringify(error) };
  }

  const user = await response.json();
  return { success: true, userId: user.id };
}

// 查找已存在的用户
async function findUserByEmail(
  secretKey: string,
  email: string
): Promise<string | null> {
  const response = await fetch(
    `https://api.clerk.com/v1/users?email_address=${encodeURIComponent(email)}`,
    {
      headers: {
        Authorization: `Bearer ${secretKey}`,
      },
    }
  );

  if (!response.ok) {
    return null;
  }

  const users = await response.json();
  return users.length > 0 ? users[0].id : null;
}

async function main() {
  const email = options.email as string;
  const password = options.password as string;
  const firstName = options['first-name'] as string;
  const lastName = options['last-name'] as string;
  const userType = options.type as string;
  const saveAuth = options['save-auth'] as boolean;

  console.log('='.repeat(50));
  console.log('🔐 Create Clerk User');
  console.log('='.repeat(50));
  console.log(`   项目: ${PROJECT_ROOT}`);
  console.log(`   用户: ${email}`);
  console.log(`   类型: ${userType}`);
  console.log('='.repeat(50));

  // 1. 检查项目结构
  if (!fs.existsSync(WEB_DIR)) {
    console.error('\n❌ 缺少 web/ 目录');
    process.exit(1);
  }

  // 2. 加载环境变量
  console.log('\n🔍 检查 Clerk 配置...');
  const env = loadEnv();
  const secretKey = env.CLERK_SECRET_KEY;

  if (!secretKey) {
    console.error('   ❌ 缺少 CLERK_SECRET_KEY');
    console.error('   请在 web/.env 中配置 CLERK_SECRET_KEY=sk_test_xxx');
    process.exit(1);
  }
  console.log('   ✅ CLERK_SECRET_KEY 已配置');

  // 3. 检查用户是否已存在
  console.log('\n🔍 检查用户是否存在...');
  const existingUserId = await findUserByEmail(secretKey, email);

  let userId: string;
  if (existingUserId) {
    console.log(`   ⚠️  用户已存在: ${existingUserId}`);
    userId = existingUserId;
  } else {
    // 4. 创建用户
    console.log('\n👤 创建用户...');
    const result = await createClerkUser(
      secretKey,
      email,
      password,
      firstName,
      lastName
    );

    if (!result.success) {
      if (result.error === 'USER_EXISTS') {
        console.log('   ⚠️  用户已存在，跳过创建');
        const id = await findUserByEmail(secretKey, email);
        if (!id) {
          console.error('   ❌ 无法获取用户 ID');
          process.exit(1);
        }
        userId = id;
      } else {
        console.error(`   ❌ 创建失败: ${result.error}`);
        process.exit(1);
      }
    } else {
      userId = result.userId!;
      console.log('   ✅ 用户创建成功！');
      console.log(`   ID: ${userId}`);
      console.log(`   Email: ${email}`);
      console.log(`   Name: ${firstName} ${lastName}`);
    }
  }

  // 5. 更新环境变量
  console.log('\n📝 更新环境变量...');
  const envKey =
    userType === 'admin' ? 'E2E_CLERK_ADMIN_USERNAME' : 'E2E_CLERK_USER_USERNAME';
  updateEnvLocal(envKey, email);
  console.log(`   ✅ ${envKey}=${email}`);

  // 6. 保存认证状态（可选）
  if (saveAuth) {
    console.log('\n🔐 保存认证状态...');
    const saveAuthScript = path.join(
      process.env.HOME || '~',
      '.claude/skills/save-auth-skill/scripts/save-auth.ts'
    );

    if (fs.existsSync(saveAuthScript)) {
      try {
        execSync(`npx tsx "${saveAuthScript}" "${PROJECT_ROOT}" ${userType}`, {
          stdio: 'inherit',
        });
      } catch (error) {
        console.error('   ⚠️  保存认证状态失败，请确保开发服务器正在运行');
      }
    } else {
      console.error('   ⚠️  save-auth 脚本不存在，跳过');
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log('✅ 用户创建完成！');
  console.log('='.repeat(50));
  console.log(`\n📋 下一步：`);
  if (!saveAuth) {
    console.log(`   1. 确保开发服务器正在运行`);
    console.log(
      `   2. 运行 save-auth 保存认证状态：npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts ${PROJECT_ROOT} ${userType}`
    );
  }
  console.log('');
}

main().catch(console.error);
