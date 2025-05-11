from datetime import datetime

app_start_time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
output_dir = f"app-{app_start_time}"
comments = ""
test_reports = ""
error_summary = ""