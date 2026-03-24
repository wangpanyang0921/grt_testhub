# 项目开发环境启动说明

## 1. 启动前准备

```bash
# 进入项目根目录
cd /Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub

# 激活虚拟环境（如果尚未激活）
source venv/bin/activate
```

## 2. 启动MySQL数据库服务

```bash
# 检查MySQL是否已运行
ps aux | grep mysql

# 如果未运行，可以使用以下命令启动（如果安装了brew）：
brew services start mysql
```

## 3. 启动后端服务（Django）

```bash
# 在项目根目录下运行
cd /Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub
source venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

## 4. 启动前端服务（Vite）

```bash
# 在前端目录下运行
cd /Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub/frontend
npm run dev
```

## 5. 服务访问地址

- **前端服务**：http://localhost:3000
- **后端服务**：http://localhost:8000
- **数据库服务**：默认端口3306（已运行）

## 6. 停止服务

- 前端服务：在终端按 `Ctrl+C` 停止
- 后端服务：在终端按 `Ctrl+C` 停止
- MySQL服务：`brew services stop mysql`

## 7. 注意事项

1. 确保虚拟环境已激活，否则Django相关命令会报错
2. 建议同时开启两个终端分别启动前后端服务
3. 如果遇到端口占用问题，可以修改端口号
4. 首次启动前请确保已安装所有依赖包