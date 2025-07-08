# Airflow 2 Backfill Plugin - Quick Reference Guide

## 🚀 Quick Start

### Installation Commands
```bash
# Install dependencies
pip install flask-admin==1.5.7 shelljob==0.5.6

# Copy plugin to Airflow
cp -r airflow/plugins/* $AIRFLOW_HOME/plugins/

# Restart webserver
airflow webserver --daemon
```

### Access the Plugin
1. Open Airflow UI: `http://localhost:8080`
2. Navigate to: **Backfill > Trigger**
3. Fill form and submit

## 📋 Essential API Reference

### Core Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `AirflowBackfillPlugin` | Plugin registration | `name`, `flask_blueprints`, `appbuilder_views` |
| `Backfill` | Main functionality | `list()`, `base()`, `background()` |
| `file_ops()` | Logging utility | Read: `file_ops('r')`, Write: `file_ops('w', data)` |

### HTTP Endpoints

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/backfill/` | GET | Main interface | None |
| `/backfill/background` | GET | Execute backfill | `dag_name`, `start_date`, `end_date` |

### Request Format
```
GET /backfill/background?dag_name=my_dag&start_date=2023-01-01T00:00:00&end_date=2023-01-02T00:00:00
```

### Response Format
```json
{
    "submitted": true
}
```

## 🛠️ Common Operations

### Basic Backfill
```
DAG Name: production_etl_dag
Start Date: 2023-12-01T00:00
End Date: 2023-12-03T23:59
```

### Check Backfill History
```bash
cat $AIRFLOW_HOME/logs/backfill_history.txt
```

### Monitor Logs
```bash
tail -f $AIRFLOW_HOME/logs/webserver.log
```

## 🔧 Configuration

### Environment Variables
```bash
export AIRFLOW_HOME=/path/to/airflow
export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW_HOME}/dags"
```

### RBAC Settings
```ini
# airflow.cfg
[webserver]
rbac = True
```

### File Locations
- Plugin: `$AIRFLOW_HOME/plugins/`
- Templates: `$AIRFLOW_HOME/plugins/templates/`
- Logs: `$AIRFLOW_HOME/logs/backfill_history.txt`

## ⚠️ Validation Rules

| Field | Validation | Error Message |
|-------|------------|---------------|
| Start Date | Must be ≤ current date | "Start date can't be greater than today's date" |
| End Date | Must be ≤ current date, ≥ start date | "End date can't be greater than today's date" |
| Date Range | Max 31 days | "Difference should not exceed 30 days" |
| DAG Name | Non-empty string | User must confirm DAG name |

## 🐛 Troubleshooting

### Plugin Not Visible
```bash
# Check plugin registration
python -c "from airflow.plugins_manager import AirflowPlugin; print([p.name for p in AirflowPlugin.get_plugin_list()])"

# Restart webserver
airflow webserver --daemon
```

### Permission Errors
```bash
# Check log directory permissions
ls -la $AIRFLOW_HOME/logs/
chmod 755 $AIRFLOW_HOME/logs/

# Create log file if missing
touch $AIRFLOW_HOME/logs/backfill_history.txt
chmod 644 $AIRFLOW_HOME/logs/backfill_history.txt
```

### Form Not Submitting
1. Check browser console for JavaScript errors
2. Verify jQuery and moment.js are loaded
3. Check network tab for failed AJAX requests

### Backfill Not Executing
```bash
# Check if airflow command is available
which airflow

# Test manual execution
airflow tasks clear test_dag -s 2023-01-01 -e 2023-01-02 --yes

# Check scheduler status
airflow scheduler
```

## 🚨 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Plugin not found" | Plugin not loaded | Restart webserver |
| "Permission denied" | Log file permissions | `chmod 755 $AIRFLOW_HOME/logs/` |
| "DAG not found" | Invalid DAG name | Check DAG exists in Airflow |
| "Date validation failed" | Invalid date range | Check date format and range |
| "Form disabled" | Previous request pending | Wait or refresh page |

## 📊 Command Examples

### Airflow Commands Generated
```bash
# Basic backfill
airflow tasks clear my_dag -s 2023-01-01T00:00:00 -e 2023-01-02T00:00:00 --yes

# With timezone
airflow tasks clear my_dag -s 2023-01-01T00:00:00+00:00 -e 2023-01-02T00:00:00+00:00 --yes
```

### Log File Format
```
2023-12-01 10:30:45.123456: airflow tasks clear my_dag -s 2023-01-01T00:00:00 -e 2023-01-02T00:00:00 --yes
2023-12-01 10:30:46.789012: my_dag ===> [2023-12-01 10:30:46,789] {clear.py:123} INFO - Clearing tasks...
```

## 🔐 Security Best Practices

### Access Control
- Use RBAC to restrict access
- Validate all user inputs
- Monitor backfill_history.txt for unauthorized access

### Input Sanitization
```python
# Sanitize DAG names
dag_name = re.sub(r'[^a-zA-Z0-9_-]', '', dag_name)

# Validate date format
datetime.fromisoformat(date_string.replace('T', ' '))
```

## 📈 Performance Tips

### Optimal Usage
- Limit backfill to 30 days or less
- Monitor system resources during execution
- Use off-peak hours for large backfills

### Resource Management
```python
# Check system load before backfill
import os
load_avg = os.getloadavg()
if load_avg[0] > 2.0:
    # Defer backfill or alert user
```

## 🔄 Extension Examples

### Custom Menu Item
```python
custom_item = {
    "name": "Custom Dashboard",
    "href": "https://dashboard.company.com",
    "category": "Monitoring",
}
```

### Enhanced Validation
```python
def validate_dag_exists(dag_name):
    from airflow.models import DagBag
    dagbag = DagBag()
    return dag_name in dagbag.dags
```

### Status Endpoint
```python
@expose("/status")
def status(self):
    return {"status": "ok", "history": file_ops('r')}
```

## 📝 Testing Commands

### Unit Tests
```bash
python -m pytest tests/test_backfill.py -v
```

### Integration Tests
```bash
python -m pytest tests/test_integration.py -v
```

### Coverage Report
```bash
pytest --cov=airflow.plugins --cov-report=html
```

## 🏗️ Development Workflow

### Local Setup
```bash
# 1. Create virtual environment
python3.7 -m venv ~/venvs/airflow-dev
source ~/venvs/airflow-dev/bin/activate

# 2. Install dependencies
pip install apache-airflow==2.2.5 flask-admin==1.5.7 shelljob==0.5.6

# 3. Set environment
export AIRFLOW_HOME=$(pwd)/airflow

# 4. Initialize
airflow db init
airflow standalone
```

### Code Quality
```bash
# Format code
black airflow/plugins/ --line-length=88

# Lint code
flake8 airflow/plugins/ --max-line-length=88

# Type checking (optional)
mypy airflow/plugins/
```

## 📞 Support & Resources

### Log Locations
- Webserver: `$AIRFLOW_HOME/logs/webserver.log`
- Scheduler: `$AIRFLOW_HOME/logs/scheduler.log`  
- Backfill: `$AIRFLOW_HOME/logs/backfill_history.txt`

### Configuration Files
- Main config: `$AIRFLOW_HOME/airflow.cfg`
- Plugin code: `$AIRFLOW_HOME/plugins/`

### Useful Commands
```bash
# Check Airflow version
airflow version

# List DAGs
airflow dags list

# Test DAG
airflow dags test my_dag 2023-01-01

# Check plugin status
airflow plugins
```

## 🎯 Quick Checklist

### Before Using Plugin
- [ ] Dependencies installed
- [ ] Plugin files copied to correct location
- [ ] Webserver restarted
- [ ] RBAC configured (if needed)
- [ ] Log directory writable

### Before Backfill
- [ ] DAG name verified
- [ ] Date range validated (≤ 30 days)
- [ ] System resources checked
- [ ] Business approval obtained

### After Backfill
- [ ] Check backfill_history.txt
- [ ] Monitor DAG execution in UI
- [ ] Verify data quality
- [ ] Update stakeholders

---

**💡 Pro Tip**: Always test backfills in development environment first!

**⚡ Quick Access**: Bookmark `/backfill/` in your browser for quick access to the plugin.