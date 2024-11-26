#/usr/bin/python
# Lightweight Python script using the Kubernetes Python client that 
# acts as a controller to monitor unhealthy pods 
# (e.g., in CrashLoopBackOff) and ensure they are recreated on a different node.

# pip install kubernetes
# How It Works
# Pod Monitoring:

# The script continuously monitors all pods in the cluster.
# If a pod enters the CrashLoopBackOff state, it triggers the handle_unhealthy_pod function.
# Pod Deletion:

# The unhealthy pod is deleted.
# Node Avoidance:

# The node where the unhealthy pod was running is tainted with a custom taint (no-schedule-unhealthy).
# This prevents new pods from being scheduled on the same node.
# Pod Rescheduling:

# Kubernetes automatically recreates the pod using the ReplicaSet/Deployment, which is now likely to be scheduled on a different node.
# Optional Enhancements
# Add logic to remove the taint after a cooldown period if the node is healthy again.
# Extend the script to include notifications (e.g., send alerts via email or Slack when pods fail).
  

from kubernetes import client, config, watch

# Load kubeconfig or in-cluster configuration
config.load_kube_config()  # Use config.load_incluster_config() if running inside a pod

# Initialize API clients
v1 = client.CoreV1Api()

def watch_pods():
    print("Starting to watch pods...")
    w = watch.Watch()
    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']
        event_type = event['type']
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace
        pod_status = pod.status

        # Check for CrashLoopBackOff state
        if pod_status and pod_status.container_statuses:
            for container_status in pod_status.container_statuses:
                state = container_status.state
                if state.waiting and state.waiting.reason == "CrashLoopBackOff":
                    print(f"Detected pod in CrashLoopBackOff: {pod_name} in namespace {pod_namespace}")
                    handle_unhealthy_pod(pod)

def handle_unhealthy_pod(pod):
    pod_name = pod.metadata.name
    pod_namespace = pod.metadata.namespace
    node_name = pod.spec.node_name

    print(f"Deleting pod: {pod_name} on node: {node_name}")
    
    # Add an annotation to avoid scheduling on the same node
    annotation_key = "avoid-node-scheduling"
    annotation_value = node_name

    # Delete the pod
    v1.delete_namespaced_pod(name=pod_name, namespace=pod_namespace)

    # Taint the node to avoid future scheduling (optional)
    taint_node(node_name)

    print(f"Pod {pod_name} deleted. Node {node_name} tainted to prevent rescheduling.")

def taint_node(node_name):
    try:
        node = v1.read_node(node_name)
        taint = client.V1Taint(
            key="no-schedule-unhealthy",
            value="true",
            effect="NoSchedule"
        )
        if node.spec.taints is None:
            node.spec.taints = []
        node.spec.taints.append(taint)
        v1.patch_node(node_name, {"spec": {"taints": node.spec.taints}})
        print(f"Node {node_name} tainted successfully.")
    except Exception as e:
        print(f"Failed to taint node {node_name}: {e}")

if __name__ == "__main__":
    try:
        watch_pods()
    except KeyboardInterrupt:
        print("Stopped watching pods.")
