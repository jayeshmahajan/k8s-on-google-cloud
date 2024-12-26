helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana-agent grafana/agent \
  --namespace monitoring \
  --create-namespace
