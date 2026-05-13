# Git 协作开发完全指南

> 适用于 Django 项目的团队协作流程

---

## 目录

1. [日常开发流程](#一日常开发流程)
2. [处理 Pull Request](#二处理-pull-request)
3. [解决合并冲突](#三解决合并冲突)
4. [数据库迁移管理](#四数据库迁移管理)
5. [常见问题排查](#五常见问题排查)

---

## 一、日常开发流程

### 1.1 开始工作前 - 更新代码

```bash
# 1. 确保在主分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 检查是否有数据库迁移需要执行
git diff HEAD~1 --name-only | grep migration
# 如果有输出，执行：
python manage.py migrate
```

### 1.2 创建功能分支

```bash
# 创建并切换到新分支（分支名要描述清楚功能）
git checkout -b feature/add-user-profile

# 或者修复 bug
git checkout -b fix/login-error
```

### 1.3 提交代码

```bash
# 查看修改了哪些文件
git status

# 添加修改的文件
git add apps/users/models.py
git add apps/users/views.py

# 或者添加所有修改
git add .

# 提交（写清楚的提交信息）
git commit -m "feat: 添加用户个人资料功能

- 新增 UserProfile 模型
- 添加头像上传功能
- 更新用户资料 API"

# 推送到远程
git push origin feature/add-user-profile
```

### 1.4 提交 Pull Request

1. 打开 GitHub 仓库页面
2. 点击 **"Pull requests"** → **"New pull request"**
3. 选择你的分支 → 选择要合并到的目标分支（通常是 main）
4. 填写 PR 标题和描述
5. 点击 **"Create pull request"**

---

## 二、处理 Pull Request

### 2.1 查看待审查的 PR

**在 GitHub 上：**
- 进入仓库 → **Pull requests** 标签
- 可以看到所有待审查的 PR

**在本地查看：**

```bash
# 获取 PR 列表（需要安装 GitHub CLI）
gh pr list

# 或者查看远程分支
git branch -r
```

### 2.2 在本地测试 PR

```bash
# 1. 获取 PR 到本地（假设 PR 编号是 #1）
git fetch origin pull/1/head:pr-1

# 2. 切换到 PR 分支
git checkout pr-1

# 3. 查看修改内容
git diff main...pr-1

# 4. 查看修改了哪些文件
git diff --name-status main...pr-1

# 5. 检查是否有数据库迁移
git diff main...pr-1 --name-only | grep -E "(models\.py|migrations/)"
```

### 2.3 合并 PR（无冲突）

```bash
# 1. 切回主分支
git checkout main

# 2. 确保主分支是最新的
git pull origin main

# 3. 合并 PR 分支
git merge pr-1

# 4. 推送到远程
git push origin main

# 5. 删除本地 PR 分支
git branch -d pr-1
```

### 2.4 使用 GitHub CLI 简化操作

```bash
# 安装 GitHub CLI 后：

# 查看 PR 列表
gh pr list

# 检出 PR 到本地
gh pr checkout 1

# 在浏览器中查看 PR
gh pr view 1 --web

# 批准 PR
gh pr review 1 --approve

# 合并 PR
gh pr merge 1
```

---

## 三、解决合并冲突

### 3.1 什么情况下会产生冲突

- 两个人同时修改了同一文件的同一部分
- 你的分支和主分支都修改了相同的代码

### 3.2 识别冲突

执行合并时出现：

```
Auto-merging apps/testcases/views.py
CONFLICT (content): Merge conflict in apps/testcases/views.py
Automatic merge failed; fix conflicts and then commit the result.
```

### 3.3 解决冲突步骤

#### 步骤 1：查看冲突文件

```bash
git status
```

会显示：
```
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   apps/testcases/views.py
```

#### 步骤 2：打开冲突文件

冲突标记格式：

```python
def some_function():
<<<<<<< HEAD
    # 这是当前分支（main）的代码
    return "main branch version"
=======
    # 这是要合并的 PR 分支的代码
    return "pr branch version"
>>>>>>> pr-1
```

#### 步骤 3：手动编辑解决冲突

选择保留的代码，删除冲突标记：

```python
def some_function():
    # 合并后的代码（根据需求选择或整合两边）
    return "merged version"
```

#### 步骤 4：标记冲突已解决

```bash
# 添加解决冲突后的文件
git add apps/testcases/views.py

# 如果所有冲突都解决了，完成合并
git commit -m "Merge pull request #1 and resolve conflicts"

# 推送
git push origin main
```

### 3.4 冲突解决示例

**场景：** 两个人都修改了 `models.py` 的同一个模型

```python
# 冲突前：
class TestCase(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

# 冲突标记：
class TestCase(models.Model):
    name = models.CharField(max_length=200)
<<<<<<< HEAD
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)  # 你添加的
=======
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)  # PR 分支添加的
>>>>>>> pr-1

# 解决后（保留两边）：
class TestCase(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    tags = models.JSONField(default=list)
```

### 3.5 放弃合并（如果冲突太复杂）

```bash
# 放弃当前合并，回到合并前的状态
git merge --abort

# 然后可以重新尝试，或者让提交者解决冲突后重新提交 PR
```

---

## 四、数据库迁移管理

### 4.1 什么时候需要迁移

| 场景 | 是否需要迁移 | 操作 |
|------|-------------|------|
| 修改 `models.py`（增删改字段） | ✅ 需要 | `makemigrations` + `migrate` |
| 新增/修改迁移文件 | ✅ 需要 | `migrate` |
| 只改 `views.py`/`serializers.py` | ❌ 不需要 | 无需操作 |
| 只改前端代码 | ❌ 不需要 | 无需操作 |
| 修改业务逻辑 | ❌ 不需要 | 无需操作 |

### 4.2 检查是否需要迁移

```bash
# 方法 1：查看最近提交是否包含迁移文件
git diff HEAD~1 --name-only | grep migration

# 方法 2：查看是否有未执行的迁移
python manage.py showmigrations

# 方法 3：检查模型变更（如果有输出，需要 makemigrations）
python manage.py makemigrations --check --dry-run
```

### 4.3 执行迁移的标准流程

#### 拉取更新后：

```bash
# 1. 检查是否有新的迁移文件
git diff HEAD~1 --name-only | grep migration

# 2. 如果有，执行迁移
python manage.py migrate

# 3. 验证迁移状态
python manage.py showmigrations
```

### 4.4 自己修改模型后的流程

```bash
# 1. 修改 models.py 后，生成迁移文件
python manage.py makemigrations

# 2. 查看生成的迁移文件
ls apps/testcases/migrations/
# 会看到类似 0003_auto_20240513_1234.py

# 3. 查看迁移内容（确认是否正确）
cat apps/testcases/migrations/0003_auto_20240513_1234.py

# 4. 执行迁移
python manage.py migrate

# 5. 提交迁移文件到 git
git add apps/testcases/migrations/0003_auto_20240513_1234.py
git commit -m "feat: 添加测试用例优先级字段

- 新增 priority 字段
- 生成数据库迁移"
```

### 4.5 迁移冲突处理

**场景：** 两个人同时修改模型，都生成了 `0002_xxx.py`

```
app/migrations/
    0001_initial.py
    0002_auto_20240510.py    ← 你生成的
    0002_auto_20240511.py    ← 同事生成的（文件名冲突！）
```

#### 解决步骤：

```bash
# 1. 回滚到共同版本（假设共同版本是 0001）
python manage.py migrate testcases 0001

# 2. 删除冲突的迁移文件（保留 0001_initial.py）
rm apps/testcases/migrations/0002_auto_20240510.py
rm apps/testcases/migrations/0002_auto_20240511.py

# 3. 重新生成迁移（合并两边的模型变更）
python manage.py makemigrations testcases

# 4. 执行迁移
python manage.py migrate

# 5. 提交新的迁移文件
```

### 4.6 迁移命令速查表

| 命令 | 作用 |
|------|------|
| `python manage.py showmigrations` | 查看所有应用的迁移状态 |
| `python manage.py migrate` | 执行所有待执行的迁移 |
| `python manage.py migrate app_name` | 只迁移指定应用 |
| `python manage.py migrate app_name 0001` | 迁移到指定版本 |
| `python manage.py migrate app_name zero` | 回滚应用的所有迁移 |
| `python manage.py makemigrations` | 根据 models 变化生成迁移文件 |
| `python manage.py makemigrations app_name` | 只生成指定应用的迁移 |
| `python manage.py sqlmigrate app_name 0001` | 查看迁移的 SQL 语句 |
| `python manage.py makemigrations --check --dry-run` | 检查是否需要迁移（不生成文件） |

### 4.7 迁移注意事项

⚠️ **重要提醒：**

1. **永远不要删除已经执行的迁移文件**
   - 如果删除了，其他开发者的数据库会混乱

2. **迁移文件必须提交到 git**
   ```bash
   git add apps/testcases/migrations/0002_auto_xxxx.py
   git commit -m "添加迁移文件"
   ```

3. **生产环境迁移前备份数据**
   ```bash
   python manage.py dumpdata > backup.json
   ```

4. **不要修改已经执行过的迁移文件**
   - 如果需要修改，先回滚再修改

---

## 五、常见问题排查

### 5.1 无法连接到 GitHub

**现象：**
```
fatal: unable to access 'https://github.com/...': Failed to connect
```

**解决：**
```bash
# 1. 检查网络
ping github.com

# 2. 配置代理（如果公司有代理）
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy http://proxy.company.com:8080

# 3. 或者使用 SSH 方式
git remote set-url origin git@github.com:username/repo.git

# 4. 取消代理
# git config --global --unset http.proxy
# git config --global --unset https.proxy
```

### 5.2 本地有未提交的修改，无法拉取

**现象：**
```
error: Your local changes would be overwritten by merge
```

**解决：**
```bash
# 方法 1：暂存修改
git stash push -m "临时保存"
git pull origin main
git stash pop  # 恢复修改

# 方法 2：提交修改
git add .
git commit -m "保存本地修改"
git pull origin main

# 方法 3：放弃修改（谨慎使用）
git checkout -- .
git pull origin main
```

### 5.3 迁移执行失败

**现象：**
```
django.db.utils.OperationalError: table already exists
```

**解决：**
```bash
# 1. 检查迁移状态
python manage.py showmigrations

# 2. 标记为已执行（假执行）
python manage.py migrate app_name --fake

# 3. 或者回滚后重新迁移
python manage.py migrate app_name zero
python manage.py migrate
```

### 5.4 忘记创建分支，直接在 main 上修改了

**解决：**
```bash
# 1. 暂存修改
git stash

# 2. 创建并切换到新分支
git checkout -b feature/my-feature

# 3. 恢复修改
git stash pop

# 4. 提交
git add .
git commit -m "xxx"
```

### 5.5 提交错了分支

**解决：**
```bash
# 1. 撤销最后一次提交（保留修改）
git reset HEAD~1

# 2. 切换到正确分支
git checkout correct-branch

# 3. 重新提交
git add .
git commit -m "xxx"
```

---

## 六、完整工作流程图

```
开始工作
    ↓
git checkout main
    ↓
git pull origin main
    ↓
检查迁移文件？
    ├── 是 → python manage.py migrate
    └── 否 → 继续
    ↓
git checkout -b feature/xxx
    ↓
编写代码...
    ↓
git add . && git commit -m "xxx"
    ↓
git push origin feature/xxx
    ↓
在 GitHub 创建 Pull Request
    ↓
代码审查
    ↓
合并到 main
    ↓
git checkout main && git pull origin main
    ↓
检查迁移文件？
    ├── 是 → python manage.py migrate
    └── 否 → 完成
```

---

## 七、Git 命令速查表

| 命令 | 作用 |
|------|------|
| `git status` | 查看当前状态 |
| `git add <file>` | 添加文件到暂存区 |
| `git add .` | 添加所有修改 |
| `git commit -m "msg"` | 提交修改 |
| `git push origin <branch>` | 推送到远程 |
| `git pull origin <branch>` | 拉取远程更新 |
| `git checkout <branch>` | 切换分支 |
| `git checkout -b <branch>` | 创建并切换分支 |
| `git branch` | 查看本地分支 |
| `git branch -r` | 查看远程分支 |
| `git log --oneline -10` | 查看最近 10 条提交 |
| `git diff` | 查看未暂存的修改 |
| `git diff --cached` | 查看已暂存的修改 |
| `git stash` | 暂存当前修改 |
| `git stash pop` | 恢复暂存的修改 |
| `git merge <branch>` | 合并分支 |
| `git merge --abort` | 放弃合并 |

---

**文档版本：** v1.0  
**适用项目：** Django + GitHub 协作开发  
**最后更新：** 2026-05-13
