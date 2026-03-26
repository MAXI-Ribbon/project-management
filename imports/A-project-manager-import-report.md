# A.xls → project-manager 导入转换报告

- 源文件：`/Users/haiyuechen/Desktop/A.xls`
- 导出文件：`/Users/haiyuechen/.openclaw/workspace/project-manager/imports/A-project-manager-import.json`
- 桌面副本：`/Users/haiyuechen/Desktop/A-project-manager-import.json`
- 生成时间：`2026-03-26T13:13:57+10:00`
- 项目数量：**61**
- 识别出总金额：**28**
- 识别出结构化付款：**20**
- 从“安装时间安排”成功匹配：**0** 条
- “安装时间安排”未可靠匹配：**43** 条

## 映射规则

- 项目名称：直接取 `2026` 工作表“项目名称”列。
- 当前阶段：按分组标题映射：`已报价→报价`、`图纸阶段→画图`、`准备生产→排产`、`已安排生产/等取货/等安装→组装`。
- 总金额：只在金额表达比较明确时才写入；不明确的保留在 `description` 里，避免误填。
- 付款情况：尽量抽成 `progressPayments`；抽不准的原文保留在 `description`。
- 无法可靠匹配到项目的安装安排，不强塞进项目，统一列在本报告末尾供人工看。

## 项目预览（前 20 个）

### 42 Riversdale Rd Oxenford-0311-Rita-Joe
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Akira-southport-0213
- 阶段：`0`
- 预计日期：``
- 总金额：`11900.0`
- 付款条目数：`0`

### Alex-30-40 Loxley Chase Forestdale-0105
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Alex-346 Richmond
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`1`

### Besa-39 Point Avenue-0316
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### bingge-lot4 405 -0202
- 阶段：`0`
- 预计日期：``
- 总金额：`8450.0`
- 付款条目数：`0`

### Connie-77 Woolley st-0202
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Derry-32 Jennifer st-0922
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Eric-0310
- 阶段：`0`
- 预计日期：``
- 总金额：`1150.0`
- 付款条目数：`0`

### Finn Hooper-Robe-0105
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Jay-0119
- 阶段：`0`
- 预计日期：``
- 总金额：`9300.0`
- 付款条目数：`0`

### Joe-0317
- 阶段：`0`
- 预计日期：``
- 总金额：`21600.0`
- 付款条目数：`0`

### linfei-0306
- 阶段：`0`
- 预计日期：``
- 总金额：`6500.0`
- 付款条目数：`0`

### liuyang-0317
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### liuyang-0319
- 阶段：`0`
- 预计日期：``
- 总金额：`5050.0`
- 付款条目数：`0`

### liuzhi-breadtop-1212
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### lot 1- 2 Delungra St Broadbeach water
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### lot 2- 2 Delungra St Broadbeach water
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### lot2-qige-0123
- 阶段：`0`
- 预计日期：``
- 总金额：``
- 付款条目数：`0`

### Mars-0320
- 阶段：`0`
- 预计日期：``
- 总金额：`5000.0`
- 付款条目数：`0`

## 安装时间安排中未可靠匹配的条目

- 2025-01-06：9211 peter senior drive
- 2025-01-08：125 oriel RD
- 2025-01-09：wangzhigang 0106
- 2025-01-10：125 oriel RD
- 2025-01-10：Besa office refurb 各半天
- 2025-01-13：6 kenneth st tarragnidi
- 2025-01-14：3950
- 2025-01-15：6 kenneth st tarragnidi
- 2025-01-16：zhangjing-lot8-0106
- 2025-01-17：songjie  0106
- 2025-01-20：lot 15 Cessnock
- 2025-01-20：9205 补一个门
- 2025-01-20：U4 17-19 Egerton st 维修
- 2025-01-21：miss zhao-0106-kitchen
- 2025-01-21：lot6
- 2025-01-22：Besa office
- 2025-01-23：Besa office
- 2025-01-24：3 Hampton CI Carindale
- 2025-01-27：holiday
- 2025-01-28：holiday
- 2025-01-29：holiday
- 2025-01-30：miss zhao-0106-laundry
- 2025-01-31：9211 peter senior drive
- 2025-01-31：9205 peter senior drive
- 2025-01-31：lot 103
- 2025-02-02：10 CLARINA ST CAAPEL HILL
- 2025-02-03：luo-tang-1119
- 2025-02-04：3 Hampton CI Carindale
- 2025-02-05：David-20012025
- 2025-02-06：89 59A Moolabar St Morningside-Besa-1114
- 2025-02-10：89 59A Moolabar St Morningside-Besa-1114
- 2025-02-11：89 59A Moolabar St Morningside-Besa-1114
- 2025-02-12：Vivian-23 oakley st carindale
- 2025-02-13：wangzhigang-0204
- 2025-02-14：125 orial
- 2025-02-17：lot3
- 2025-02-18：125 orial
- 2025-02-19：lot3
- 2025-02-20：9205/9211/130/500/158
- 2025-02-21：9205/9211/130/500/158
- 2025-02-24：89 59A Moolabar St Morningside-Besa-1114
- 2025-02-24：松姐
- 2025-02-25：125 orial，2Houston st-0220
