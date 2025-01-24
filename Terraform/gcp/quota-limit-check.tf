# Fetch quotas for the project in the specified region
data "google_project_quotas" "region_quotas" {
  project = var.project_id
  region  = var.region
}

# Precheck: Ensure sufficient quota for CPUs
resource "null_resource" "precheck" {
  provisioner "local-exec" {
    command = <<EOT
    python3 <<PYTHON
import sys

# Quota usage data
quotas = ${jsonencode(data.google_project_quotas.region_quotas.metric)}
cpu_quota = next((q for q in quotas if q["metric"] == "compute.googleapis.com/cpus"), None)

if cpu_quota:
    available = cpu_quota["limit"] - cpu_quota["usage"]
    if available < ${var.node_count}:
        print(f"Insufficient CPU quota in region '{var.region}'. Needed: {var.node_count}, Available: {available}")
        sys.exit(1)
    else:
        print("Quota check passed for CPUs.")
else:
    print("CPU quota metric not found.")
PYTHON
    EOT
  }
}
