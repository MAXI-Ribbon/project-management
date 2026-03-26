#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import xlrd

BASE_DIR = Path('/Users/haiyuechen/.openclaw/workspace/project-manager')
DEFAULT_SOURCE = Path('/Users/haiyuechen/Desktop/A.xls')
DEFAULT_OUTPUT = BASE_DIR / 'imports' / 'A-project-manager-import.json'
DEFAULT_REPORT = BASE_DIR / 'imports' / 'A-project-manager-import-report.md'
DEFAULT_DESKTOP_COPY = Path('/Users/haiyuechen/Desktop/A-project-manager-import.json')

STATUS_TO_STAGE = {
    '已报价': 0,
    '图纸阶段': 1,
    '准备生产': 4,
    '已安排生产': 5,
    '等取货': 5,
    '等安装': 5,
}
SECTION_HEADERS = set(STATUS_TO_STAGE)


def text(value) -> str:
    if value is None:
        return ''
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    return str(value).strip()


def normalize_name(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '').lower().strip()
    value = value.replace('orial', 'oriel')
    value = value.replace(' ci ', ' cl ').replace(' ci', ' cl').replace('ci ', 'cl ')
    value = re.sub(r'[^\w\u4e00-\u9fff]+', '', value)
    return value


def stable_project_id(name: str) -> int:
    digest = hashlib.sha1(normalize_name(name).encode('utf-8')).hexdigest()[:12]
    return 1000000000 + (int(digest, 16) % 900000000)


def money_values(raw: str) -> list[float]:
    raw = (raw or '').replace(',', '')
    values: list[float] = []
    for match in re.finditer(r'\$\s*([0-9]+(?:\.[0-9]+)?)', raw):
        values.append(float(match.group(1)))
    return values


def parse_total_amount(quote: str, payment: str, total_col: str) -> tuple[float | None, str | None]:
    total_col = text(total_col)
    quote = text(quote)
    payment = text(payment)

    if total_col:
        vals = money_values(total_col)
        if len(vals) == 1:
            return vals[0], '总价列'
        numeric_total = re.fullmatch(r'\s*([0-9]+(?:\.[0-9]+)?)\s*', total_col.replace(',', ''))
        if numeric_total:
            return float(numeric_total.group(1)), '总价列'

    for raw, source in [(quote, '报价'), (payment, '付款情况')]:
        match = re.search(r'总价[^\d$]*\$?\s*([0-9]+(?:\.[0-9]+)?)', raw.replace(',', ''), re.I)
        if match:
            return float(match.group(1)), source

    qvals = money_values(quote)
    if len(qvals) == 1 and not any(marker in quote for marker in ['；', ';', '\n', '利润', '石头$', '外加', 'A:', 'B:', 'C:']):
        return qvals[0], '报价'

    pvals = money_values(payment)
    if len(pvals) == 1 and '已付' not in payment and 'paid' not in payment.lower() and 'INV-' not in payment.upper():
        return pvals[0], '付款情况'

    return None, None


def parse_payment_lines(raw: str) -> list[dict]:
    raw = text(raw)
    if not raw:
        return []

    results: list[dict] = []
    for line in [part.strip() for part in re.split(r'\n+', raw) if part.strip()]:
        percent = None
        amount = None

        percent_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%', line)
        if percent_match:
            percent = float(percent_match.group(1))

        amount_match = re.search(r'已付[^\d$]*\$?\s*([0-9]+(?:\.[0-9]+)?)', line)
        if amount_match:
            amount = float(amount_match.group(1))
        elif re.search(r'\bpaid\b', line, re.I):
            generic_amount = re.search(r'\$\s*([0-9]+(?:\.[0-9]+)?)', line)
            if generic_amount:
                amount = float(generic_amount.group(1))

        paid = bool(re.search(r'已付|\bpaid\b', line, re.I))

        if percent is None and amount is None and not paid:
            if not re.search(r'INV|差|账单|现金|付款|未发|周期|已付|paid', line, re.I):
                continue

        results.append({
            'percent': percent,
            'amount': amount,
            'note': line,
            'paid': paid,
        })

        if len(results) >= 5:
            break

    return results


def excel_date_to_str(value, datemode: int) -> str:
    if not isinstance(value, (float, int)) or not value:
        return ''
    try:
        year, month, day, *_ = xlrd.xldate_as_tuple(value, datemode)
        return f'{year:04d}-{month:02d}-{day:02d}'
    except Exception:
        return ''


@dataclass
class ProjectRecord:
    name: str
    current_stage: int
    id: int = field(init=False)
    create_date: str = ''
    expected_date: str = ''
    total_amount: float | None = None
    progress_payments: list[dict] = field(default_factory=list)
    description_lines: list[str] = field(default_factory=list)
    source_statuses: list[str] = field(default_factory=list)
    schedule_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.id = stable_project_id(self.name)

    def add_unique_lines(self, lines: Iterable[str]) -> None:
        for line in lines:
            line = line.strip()
            if line and line not in self.description_lines:
                self.description_lines.append(line)

    def add_status(self, status: str | None) -> None:
        if status and status not in self.source_statuses:
            self.source_statuses.append(status)

    def merge_payment_items(self, items: list[dict]) -> None:
        for item in items:
            if len(self.progress_payments) >= 5:
                break
            if item not in self.progress_payments:
                self.progress_payments.append(item)

    def as_project_json(self, updated_at: str) -> dict:
        description_lines = self.description_lines[:]
        if self.schedule_notes:
            description_lines.append('安装安排（按表格可识别部分）：' + '； '.join(self.schedule_notes))
        return {
            'id': self.id,
            'name': self.name,
            'createDate': self.create_date,
            'expectedDate': self.expected_date,
            'description': '\n'.join(description_lines).strip(),
            'currentStage': self.current_stage,
            'totalAmount': self.total_amount,
            'stageDates': {str(i): '' for i in range(7)},
            'progressPayments': self.progress_payments[:5],
            'logs': [
                {
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'action': '导入A.xls',
                    'detail': '由 A.xls / 2026 工作表转换生成',
                }
            ],
            'version': 1,
            'updatedAt': updated_at,
            'sourceStatuses': self.source_statuses,
        }


def score_match(schedule_text: str, project_name: str) -> float:
    schedule_norm = normalize_name(schedule_text)
    project_norm = normalize_name(project_name)
    if len(schedule_norm) < 4 or len(project_norm) < 4:
        return 0.0
    if schedule_norm == project_norm:
        return 1.0

    best = 0.0
    if schedule_norm in project_norm or project_norm in schedule_norm:
        shorter = min(len(schedule_norm), len(project_norm))
        longer = max(len(schedule_norm), len(project_norm))
        if shorter >= 6:
            best = max(best, 0.86 * shorter / longer + 0.14)

    tokens_a = set(re.findall(r'[a-z]+|\d+|[\u4e00-\u9fff]+', schedule_norm))
    tokens_b = set(re.findall(r'[a-z]+|\d+|[\u4e00-\u9fff]+', project_norm))
    stop = {'st', 'rd', 'lot', 'no', 'u1', 'u2', 'u3', 'u4'}
    tokens_a = {token for token in tokens_a if token not in stop and len(token) >= 2}
    tokens_b = {token for token in tokens_b if token not in stop and len(token) >= 2}

    if tokens_a and tokens_b:
        overlap = tokens_a & tokens_b
        if overlap:
            overlap_score = len(overlap) / max(len(tokens_a), len(tokens_b))
            if any(token.isdigit() and len(token) >= 3 for token in overlap):
                overlap_score += 0.15
            if any(token.isalpha() and len(token) >= 5 for token in overlap):
                overlap_score += 0.10
            best = max(best, overlap_score)

    return round(best, 4)


def convert(source: Path = DEFAULT_SOURCE, output: Path = DEFAULT_OUTPUT, report_path: Path = DEFAULT_REPORT, desktop_copy: Path | None = DEFAULT_DESKTOP_COPY) -> dict:
    workbook = xlrd.open_workbook(str(source))
    sheet_2026 = workbook.sheet_by_name('2026')

    projects: dict[str, ProjectRecord] = {}
    current_status: str | None = None

    for row_index in range(1, sheet_2026.nrows):
        row = [text(sheet_2026.cell_value(row_index, column)) for column in range(4)]
        name, quote, payment, total_col = row

        if name in SECTION_HEADERS and not any([quote, payment, total_col]):
            current_status = name
            continue
        if not name:
            continue

        key = normalize_name(name)
        total_amount, total_source = parse_total_amount(quote, payment, total_col)
        payment_items = parse_payment_lines(payment)

        description_lines = []
        if current_status:
            description_lines.append(f'来源状态：{current_status}')
        if quote:
            description_lines.append(f'报价：{quote}')
        if payment:
            description_lines.append(f'付款情况：{payment}')
        if total_col and (total_amount is None or total_source != '总价列'):
            description_lines.append(f'总价列原文：{total_col}')
        description_lines.append(f'来源：A.xls / 2026 / 第 {row_index + 1} 行')

        if key not in projects:
            project = ProjectRecord(
                name=name,
                current_stage=STATUS_TO_STAGE.get(current_status, 0),
                total_amount=total_amount,
            )
            project.add_status(current_status)
            project.add_unique_lines(description_lines)
            project.merge_payment_items(payment_items)
            projects[key] = project
        else:
            project = projects[key]
            project.current_stage = max(project.current_stage, STATUS_TO_STAGE.get(current_status, project.current_stage))
            project.add_status(current_status)
            project.add_unique_lines(description_lines)
            if project.total_amount is None and total_amount is not None:
                project.total_amount = total_amount
            project.merge_payment_items(payment_items)

    sheet_schedule = workbook.sheet_by_name('安装时间安排')
    unmatched_schedule: list[dict] = []
    schedule_matches = 0

    for row_index in range(1, sheet_schedule.nrows, 2):
        if row_index + 1 >= sheet_schedule.nrows:
            break

        date_row = [sheet_schedule.cell_value(row_index, column) for column in range(1, sheet_schedule.ncols)]
        task_row = [text(sheet_schedule.cell_value(row_index + 1, column)) for column in range(1, sheet_schedule.ncols)]

        for column_index, raw_task in enumerate(task_row):
            if not raw_task or raw_task == '-':
                continue

            date_str = excel_date_to_str(date_row[column_index], workbook.datemode)
            task_parts = [part.strip() for part in re.split(r'[\n；;]+', raw_task) if part.strip() and part.strip() != '-']
            for task_part in task_parts:
                best_project = None
                best_score = 0.0
                for project in projects.values():
                    score = score_match(task_part, project.name)
                    if score > best_score:
                        best_project = project
                        best_score = score

                if best_project and best_score >= 0.82:
                    note = f'{date_str}：{task_part}' if date_str else task_part
                    if note not in best_project.schedule_notes:
                        best_project.schedule_notes.append(note)
                    if date_str and not best_project.expected_date:
                        best_project.expected_date = date_str
                    schedule_matches += 1
                else:
                    unmatched_schedule.append({'date': date_str, 'text': task_part, 'bestScore': best_score})

    updated_at = datetime.now().astimezone().isoformat(timespec='seconds')
    output_projects = [project.as_project_json(updated_at) for project in projects.values()]
    output_projects.sort(key=lambda item: (item['currentStage'], item['name'].lower()))

    payload = {
        'appVersion': '1.0.1-r3',
        'baseReleaseVersion': '1.0.1',
        'sourceFile': str(source),
        'generatedBy': 'convert_a_xls_to_project_manager.py',
        'projects': output_projects,
        'tempWorks': [],
        'exportTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'exportTimestamp': updated_at,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    if desktop_copy:
        desktop_copy.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    report_lines = [
        '# A.xls → project-manager 导入转换报告',
        '',
        f'- 源文件：`{source}`',
        f'- 导出文件：`{output}`',
        f'- 桌面副本：`{desktop_copy}`' if desktop_copy else '- 桌面副本：未生成',
        f'- 生成时间：`{updated_at}`',
        f'- 项目数量：**{len(output_projects)}**',
        f'- 识别出总金额：**{sum(1 for item in output_projects if item["totalAmount"] is not None)}**',
        f'- 识别出结构化付款：**{sum(1 for item in output_projects if any(item["progressPayments"]))}**',
        f'- 从“安装时间安排”成功匹配：**{schedule_matches}** 条',
        f'- “安装时间安排”未可靠匹配：**{len(unmatched_schedule)}** 条',
        '',
        '## 映射规则',
        '',
        '- 项目名称：直接取 `2026` 工作表“项目名称”列。',
        '- 当前阶段：按分组标题映射：`已报价→报价`、`图纸阶段→画图`、`准备生产→排产`、`已安排生产/等取货/等安装→组装`。',
        '- 总金额：只在金额表达比较明确时才写入；不明确的保留在 `description` 里，避免误填。',
        '- 付款情况：尽量抽成 `progressPayments`；抽不准的原文保留在 `description`。',
        '- 无法可靠匹配到项目的安装安排，不强塞进项目，统一列在本报告末尾供人工看。',
        '',
        '## 项目预览（前 20 个）',
        '',
    ]

    for item in output_projects[:20]:
        report_lines.extend([
            f'### {item["name"]}',
            f'- 阶段：`{item["currentStage"]}`',
            f'- 预计日期：`{item["expectedDate"] or ""}`',
            f'- 总金额：`{item["totalAmount"] if item["totalAmount"] is not None else ""}`',
            f'- 付款条目数：`{len([p for p in item["progressPayments"] if p])}`',
            '',
        ])

    report_lines.extend([
        '## 安装时间安排中未可靠匹配的条目',
        '',
    ])
    for row in unmatched_schedule:
        label = f'{row["date"]}：{row["text"]}' if row['date'] else row['text']
        report_lines.append(f'- {label}')

    report_path.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')

    return {
        'output': str(output),
        'desktopCopy': str(desktop_copy) if desktop_copy else None,
        'report': str(report_path),
        'projectCount': len(output_projects),
        'scheduleMatched': schedule_matches,
        'scheduleUnmatched': len(unmatched_schedule),
    }


if __name__ == '__main__':
    result = convert()
    print(json.dumps(result, ensure_ascii=False, indent=2))
