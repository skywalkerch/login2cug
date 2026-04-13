# 中国地质大学校园网自动登录
两个使用不同方法自动登录中国地质大学校园网的Python脚本。

## 概述

本仓库包含两个独立的校园网自动登录脚本：

1. **`cug.py`** - 使用SRUN3000认证协议（XXTEA加密）直接进行API登录
2. **`playwright.py`** - 使用Playwright浏览器自动化填写登录表单

两个脚本目的相同但技术实现不同。基于API的方法（`cug.py`）更快更可靠，而浏览器自动化方法（`playwright.py`）在网页界面变更时或用于教学目的时更有用。

## 功能特点

### cug.py
- 直接与校园网认证服务器进行HTTP API通信
- 实现SRUN3000加密协议（XXTEA + 自定义Base64）
- 无需浏览器，无头运行
- 包含用于调试的载荷解密工具
- 支持用户名/密码命令行参数

### playwright.py
- 使用Playwright进行浏览器自动化
- 填写用户名/密码字段并点击登录按钮
- 支持无头模式
- 易于适配网站变更

## 安装

###  prerequisites
- Python 3.13 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理器（推荐）或 pip

### 设置步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/cug-auto-login.git
   cd cug-auto-login
   ```

2. 使用uv安装依赖：
   ```bash
   uv sync
   ```

   或使用pip：
   ```bash
   pip install -r requirements.txt
   ```

3. 对于playwright.py，安装浏览器二进制文件：
   ```bash
   playwright install chromium
   ```

## 使用方法

### 使用cug.py（API方法）

```bash
python cug.py --username 你的学号 --password 你的密码
```

示例：
```bash
python cug.py --username 20210001 --password mypassword123
```

脚本将：
1. 从认证服务器获取挑战令牌
2. 使用XXTEA算法计算加密载荷
3. 发送带有正确校验和的登录请求
4. 显示成功或错误信息

### 使用playwright.py（浏览器自动化）

1. 编辑脚本设置你的凭据：
   ```python
   User = '你的学号'
   Password = '你的密码'
   ```

2. 同时更新`page.goto('')`中的登录页面URL

3. 运行脚本：
   ```bash
   python playwright.py
   ```

### 配置

对于`cug.py`，你可能需要修改`Login`类中的以下常量：
- `HOST`：认证服务器URL（默认：``）
- `AC_ID`：访问控制器ID（默认：``）

## 技术细节

### SRUN3000认证协议
`cug.py`脚本实现了许多中国大学网络使用的SRUN3000认证协议：

1. **挑战请求**：从服务器获取令牌和客户端IP
2. **载荷加密**：
   - 创建包含用户名、密码、IP等信息的JSON对象
   - 使用XXTEA算法以令牌为密钥进行加密
   - 使用自定义Base64字母表编码
3. **校验和计算**：连接参数的SHA1哈希
4. **登录请求**：将所有参数发送到认证端点

`Decryptor`类提供逆向工程工具，用于调试时解密加密载荷。

### 文件结构
```
.
├── cug.py              # SRUN3000 API认证脚本
├── playwright.py       # 浏览器自动化脚本
├── pyproject.toml     # Python项目配置
├── uv.lock            # 依赖锁定文件
└── README.md          # 本文件
```

## 安全注意事项

- **切勿将真实凭据提交**到版本控制
- 考虑使用环境变量或配置文件存储敏感数据
- 本脚本仅用于教育和个人用途
- 仅在你被授权访问的网络中使用

## 故障排除

### cug.py问题
- **"无法获取 Token"**：检查`HOST` URL和网络连接
- **"服务器返回异常响应"**：验证用户名/密码和AC_ID
- **加密错误**：确保Python版本兼容性

### playwright.py问题
- **找不到浏览器**：运行`playwright install chromium`
- **找不到元素**：如果登录页面变更，请更新CSS选择器
- **超时**：检查网络连接和登录页面URL

## 贡献

欢迎提交issue或pull request：
- 错误修复
- 新功能
- 文档改进
- 支持其他校园网络

## 许可证

本项目仅用于教育目的。使用风险自负。

## 免责声明

本脚本仅限授权使用。用户需遵守所在机构的网络政策和服务条款。
