# Airflow 2 Backfill Plugin - API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Plugin Architecture](#plugin-architecture)
3. [Public APIs](#public-apis)
4. [Core Components](#core-components)
5. [UI Components](#ui-components)
6. [Configuration](#configuration)
7. [Usage Examples](#usage-examples)
8. [Integration Guide](#integration-guide)
9. [Error Handling](#error-handling)
10. [Troubleshooting](#troubleshooting)

## Overview

The Airflow 2 Backfill Plugin provides a web-based interface for triggering DAG backfills directly from the Airflow UI. It eliminates the need to access the Airflow cluster directly via command line, making backfill operations more accessible to DAG owners.

### Key Features

- **Web-based Backfill Interface**: Trigger backfills through an intuitive UI
- **External Links Integration**: Add monitoring dashboard and documentation links
- **Background Processing**: Non-blocking backfill execution
- **Request Logging**: Complete audit trail of backfill operations
- **Input Validation**: Date range and DAG name validation

## Plugin Architecture

```
airflow/plugins/
├── __init__.py                 # Plugin registration and configuration
├── backfill/
│   ├── __init__.py            # Backfill module initialization
│   └── main.py                # Core backfill functionality
└── templates/
    └── backfill_page.html     # Web interface template
```

## Public APIs

### Plugin Class: `AirflowBackfillPlugin`

**Location**: `airflow/plugins/__init__.py`

The main plugin class that registers all components with Airflow.

```python
class AirflowBackfillPlugin(AirflowPlugin):
    name = "backfill_plugin"
    flask_blueprints = [backfill_blueprint]
    appbuilder_views = [v_backfill_package]
    appbuilder_menu_items = [project_document_mitem, airflow_monitoring_mitem]
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin identifier used by Airflow |
| `flask_blueprints` | `List[Blueprint]` | Flask blueprints for template handling |
| `appbuilder_views` | `List[Dict]` | Views added to Airflow's app builder |
| `appbuilder_menu_items` | `List[Dict]` | Menu items added to Airflow UI |

#### Menu Items Configuration

```python
# Documentation link
project_document_mitem = {
    "name": "Project Documentation",
    "href": "https://airflow.apache.org/",
}

# Monitoring link
airflow_monitoring_mitem = {
    "name": "Airflow",
    "href": "https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/index.html",
    "category": "Monitoring",
}
```

### Backfill Class: `Backfill`

**Location**: `airflow/plugins/backfill/main.py`

The core class that handles backfill operations and web interface.

```python
class Backfill(AppBuilderBaseView):
    route_base = "/backfill/"
```

#### Methods

##### `list()` / `base()`

Renders the main backfill interface.

**Parameters**: None

**Returns**: Rendered HTML template

**Usage**:
- `list()`: Used when RBAC is enabled
- `base()`: Used when RBAC is disabled

**Example**:
```python
@app_builder_expose("/")
def list(self):
    return self.render_template(
        "backfill_page.html",
        rbac_authentication_enabled=rbac_authentication_enabled,
    )
```

##### `background()`

Executes backfill operations in the background.

**Parameters** (via URL query string):
- `dag_name` (str): Name of the DAG to backfill
- `start_date` (str): Start date in ISO format (YYYY-MM-DDTHH:mm:00)
- `end_date` (str): End date in ISO format (YYYY-MM-DDTHH:mm:00)

**Returns**: JSON response indicating submission status

**HTTP Method**: GET

**Endpoint**: `/backfill/background`

**Example Request**:
```
GET /backfill/background?dag_name=hello_world&start_date=2023-01-01T00:00:00&end_date=2023-01-02T00:00:00
```

**Example Response**:
```json
{
    "submitted": true
}
```

**Command Executed**:
```bash
airflow tasks clear hello_world -s 2023-01-01T00:00:00 -e 2023-01-02T00:00:00 --yes
```

## Core Components

### File Operations: `file_ops()`

**Location**: `airflow/plugins/backfill/main.py`

Utility function for logging and reading backfill history.

```python
def file_ops(mode, data=None):
    """
    File operators - logging/writing and reading user request
    
    Args:
        mode (str): Operation mode ('r' for read, 'w' for write)
        data (str, optional): Data to write when mode is 'w'
        
    Returns:
        str: File contents when mode is 'r'
        int: 1 when write is successful
        None: When file creation fails
    """
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | `str` | Yes | Operation mode: 'r' (read) or 'w' (write) |
| `data` | `str` | No | Data to write (required when mode='w') |

#### Examples

**Reading log history**:
```python
history = file_ops('r')
print(history)
```

**Writing to log**:
```python
file_ops('w', 'airflow tasks clear my_dag -s 2023-01-01 -e 2023-01-02\n')
```

#### Log File Location

```python
FILE = airflow_home_path + "/logs/backfill_history.txt"
```

### Configuration Variables

#### RBAC Detection

```python
rbac_authentication_enabled = configuration.getboolean("webserver", "RBAC")
```

#### ANSI Escape Sequence Removal

```python
ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
```

Used to clean terminal output before logging.

## UI Components

### Backfill Interface

**Template**: `airflow/plugins/templates/backfill_page.html`

#### Form Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `dag_name` | text | Yes | DAG identifier | Non-empty string |
| `start_date` | datetime-local | Yes | Backfill start time | Must be ≤ current date |
| `end_date` | datetime-local | Yes | Backfill end time | Must be ≤ current date, ≥ start_date |

#### Client-Side Validation

```javascript
// Date range validation (max 31 days)
if (en_date > st_date && en_date.diff(st_date, 'days') > 31) {
    alert('Difference between start and end date should not exceed 30 days');
    return false;
}

// Future date validation
if (td_date < st_date || td_date < en_date ) {
    alert("Start date and End date can't be greater than today's date");
    return false;
}
```

#### UI Features

- **Real-time validation**: Prevents invalid date ranges
- **Confirmation dialog**: User must confirm DAG name before submission
- **Status messages**: Success/error feedback
- **Form state management**: Disables form during processing
- **Responsive design**: Bootstrap 4 based layout

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AIRFLOW_HOME` | Yes | Airflow installation directory | `/opt/airflow` |

### Dependencies

Add to your Docker image or requirements file:

```txt
flask-admin==1.5.7
shelljob==0.5.6
```

### Airflow Configuration

Ensure RBAC is properly configured:

```ini
[webserver]
rbac = True
```

## Usage Examples

### Basic Usage

1. **Navigate to Backfill Page**:
   - Go to Airflow UI
   - Click on "Trigger" under the "Backfill" section

2. **Fill the Form**:
   ```
   DAG Name: my_production_dag
   Start Datetime: 2023-12-01T00:00
   End Datetime: 2023-12-03T23:59
   ```

3. **Submit and Monitor**:
   - Click "Start" button
   - Confirm the DAG name
   - Monitor progress in Airflow UI

### Programmatic Integration

#### Custom Menu Items

```python
# Add custom monitoring dashboards
custom_monitoring_item = {
    "name": "Grafana Dashboard",
    "href": "https://grafana.company.com/airflow",
    "category": "Monitoring",
}

# Add to plugin
class CustomAirflowPlugin(AirflowPlugin):
    name = "custom_plugin"
    appbuilder_menu_items = [custom_monitoring_item]
```

#### Extending the Backfill Class

```python
from backfill.main import Backfill

class ExtendedBackfill(Backfill):
    @expose("/status")
    def status(self):
        """Custom endpoint for backfill status"""
        history = file_ops('r')
        return {"status": "success", "history": history}
```

### Sample DAG for Testing

```python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

dag = DAG(
    'test_backfill_dag',
    description='Test DAG for backfill plugin',
    schedule_interval='0 12 * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False
)

test_task = DummyOperator(
    task_id='test_task',
    dag=dag
)
```

## Integration Guide

### Step 1: Install Dependencies

```bash
pip install flask-admin==1.5.7 shelljob==0.5.6
```

### Step 2: Deploy Plugin

```bash
# Copy plugin files to Airflow plugins directory
cp -r airflow/plugins/* $AIRFLOW_HOME/plugins/
```

### Step 3: Configure Environment

```bash
export AIRFLOW_HOME=/path/to/airflow
export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW_HOME}/dags"
```

### Step 4: Restart Airflow

```bash
# Restart webserver to load plugin
airflow webserver --daemon
```

### Step 5: Verify Installation

1. Check Airflow UI for "Backfill" section
2. Verify menu items appear correctly
3. Test with a simple DAG

## Error Handling

### Common Errors and Solutions

#### Plugin Not Loading

**Error**: Plugin doesn't appear in UI
**Solution**: 
```bash
# Check plugin registration
python -c "from airflow.plugins_manager import AirflowPlugin; print(AirflowPlugin.get_plugin_list())"

# Restart webserver
airflow webserver --daemon
```

#### Permission Errors

**Error**: Cannot write to log file
**Solution**:
```bash
# Ensure log directory exists and is writable
mkdir -p $AIRFLOW_HOME/logs
chmod 755 $AIRFLOW_HOME/logs
```

#### Date Validation Errors

**Error**: "Start date should be less than end date"
**Solution**: Ensure start_date < end_date and both are in the past

### Logging and Debugging

#### View Backfill History

```bash
cat $AIRFLOW_HOME/logs/backfill_history.txt
```

#### Check Webserver Logs

```bash
tail -f $AIRFLOW_HOME/logs/webserver.log
```

## Troubleshooting

### Performance Issues

1. **Large Date Ranges**: Limit backfill to 30 days or less
2. **Concurrent Requests**: Monitor system resources during backfill
3. **Log File Size**: Rotate logs regularly

### Security Considerations

1. **Input Validation**: Always validate DAG names and dates
2. **Access Control**: Use Airflow's RBAC features
3. **Audit Trail**: Monitor backfill_history.txt for unauthorized access

### Best Practices

1. **Test in Development**: Always test backfills in non-production first
2. **Monitor Resources**: Check cluster capacity before large backfills
3. **Use Descriptive Names**: Include purpose in DAG names
4. **Regular Cleanup**: Implement log rotation

## API Reference Summary

| Component | Type | Purpose | Key Methods/Attributes |
|-----------|------|---------|----------------------|
| `AirflowBackfillPlugin` | Plugin Class | Main plugin registration | `name`, `flask_blueprints`, `appbuilder_views` |
| `Backfill` | View Class | Web interface and processing | `list()`, `base()`, `background()` |
| `file_ops()` | Function | Logging operations | `mode`, `data` parameters |
| `backfill_page.html` | Template | User interface | Form validation, AJAX requests |

This documentation provides comprehensive coverage of all public APIs, functions, and components in the Airflow 2 Backfill Plugin, including practical examples and integration instructions.