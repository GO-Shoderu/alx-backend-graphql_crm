from datetime import datetime


def log_crm_heartbeat():
    """
    Logs a heartbeat every 5 minutes to confirm CRM health.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message)
