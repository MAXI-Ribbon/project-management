# 生产项目管理

一个纯前端、单文件的项目管理工具，用于跟踪项目列表、阶段进度、日历安排、进度款记录、临时工作和修改日志。页面包含“项目列表”“看板视图”“日历视图”“添加项目”“导出数据”“导入备份”“清空”等入口，并提供“添加新项目”“添加当日临时工作”“修改日志”等弹窗功能。 [oai_citation:0‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

## 功能简介

本项目适合用于轻量级的生产/施工/项目进度管理，核心能力包括：

- 项目列表管理
- 看板视图管理
- 日历视图查看
- 新增项目
- 导出数据备份
- 导入备份数据
- 清空数据
- 添加当日临时工作
- 记录修改日志
- 录入项目名称、创建日期、预期完成日期、各阶段计划日期、当前阶段、项目总金额、进度款和备注/联系人信息等字段。 [oai_citation:1‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

## 项目特点

- **纯前端单文件**：核心页面为 `index.html`
- **无需后端**：适合本地打开或静态托管
- **轻量易部署**：可直接部署到 GitHub Pages、Netlify、Vercel 或任意静态服务器
- **适合内部使用**：适合个人、小团队或现场项目追踪
- **支持本地数据备份**：可导出/导入项目数据，便于迁移和恢复。页面中已提供“导出数据”和“导入备份”入口。 [oai_citation:2‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

## 版本与备份

- 当前正式版基线：`1.0.1`
- 当前页面迭代版：见页面右上角版本显示
- 本地备份目录：`backups/`
- 备份脚本：`./scripts/backup_version.sh <版本号> "备注"`
- 版本迭代规则与备份流程：见 `VERSIONING.md`

## 页面结构

### 1. 项目列表
用于集中查看全部项目。

### 2. 看板视图
用于按阶段或状态查看项目，方便拖拽式或流程式管理。

### 3. 日历视图
用于按月份查看项目安排，并支持切换上个月 / 下个月。 [oai_citation:3‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

### 4. 添加新项目
可录入以下信息：

- 项目名称/地址
- 创建日期
- 预期完成日期
- 各阶段计划日期
- 当前所处阶段
- 项目总金额
- 进度款（最多 5 笔）
- 已付总额
- 未付总额
- 备注 / 联系人信息。 [oai_citation:4‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

### 5. 添加当日临时工作
用于登记当天新增的临时任务，包括：

- 工作标题
- 备注。 [oai_citation:5‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

### 6. 修改日志
用于记录项目更新或操作痕迹。 [oai_citation:6‡GitHub](https://raw.githubusercontent.com/MAXI-Ribbon/project-management/refs/heads/main/index.html)

## 使用方式

### 本地运行

1. 下载项目文件
2. 确保目录中包含 `index.html`
3. 直接用浏览器打开 `index.html` 即可使用

### 静态部署

可部署到任意静态托管平台，例如：

- GitHub Pages
- Netlify
- Vercel
- Nginx / Apache 静态站点目录

## 推荐目录结构

```text
project-management/
├── index.html
└── README.md
