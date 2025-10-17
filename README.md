# Open Threat Situational Awareness (Mini)

一个最小可运行的态势感知平台：日志采集/接入、存储、检测（规则+情报）、告警、简单UI。

## 功能
- 日志接入：`/ingest/events` 与 `/ingest/bulk/events`
- 存储：SQLite + SQLAlchemy 模型（事件、规则、情报、告警）
- 检测：
  - 规则引擎（equals/contains/regex/in/in_cidr/gt/lt）
  - 情报匹配（IP/Domain/URL/Hash 到事件常用字段）
  - 后台任务在事件入库后自动执行
- 告警：持久化并通过简单通知器打印到控制台
- 查询：`/search/events` 与 `/search/alerts`
- 管理：`/admin/intel` 添加/查看情报；`/admin/rules` 查看规则（启动时从 `data/rules` 加载）
- UI：`/` 首页，快速发送示例事件并展示最新告警

## 运行
```bash
make install      # 安装依赖（无法创建 venv 时使用用户级 pip）
make run          # 或 make dev
# 直接使用 uvicorn（用户级安装位置）
~/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

打开浏览器访问 `http://localhost:8000/` 或 Swagger 文档 `http://localhost:8000/docs`。

## 示例
- 规则与情报在 `data/rules/*.yaml` 和 `data/intel/*.yaml`，程序启动时自动加载。
- 首页“发送示例日志”会触发 `sysmon` 规则 `Suspicious PowerShell EncodedCommand`，几百毫秒后在“Recent Alerts”看到告警。
- 你也可以通过 `curl` 手动发送：
```bash
curl -X POST http://localhost:8000/ingest/events \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "suricata",
    "event_time": "2024-01-01T00:00:00Z",
    "raw": {
      "event_type": "dns",
      "dns": {"rrtype":"TXT", "rrname":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.example.com"},
      "src_ip":"10.0.0.1","dest_ip":"203.0.113.66"
    }
  }'
```

## 目录结构
```text
app/
  main.py, db.py, models.py, schemas.py, parsers.py, utils.py
  routers/ (ingest, search, admin, alerts, ui)
  detection/engine.py
  intel/loader.py, intel/matcher.py
  alerting/notifier.py
static/, templates/
data/
  rules/*.yaml, intel/*.yaml
```

## 声明
- 本项目为教学演示用的最小实现，不等同于商用产品。
- 请勿将其作为唯一检测手段，生产使用需补充鉴权、分布式采集、时序/搜索引擎（如 ClickHouse/ES）、多租户、审计、HA 等能力。
