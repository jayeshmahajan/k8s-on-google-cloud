gcloud container clusters update <CLUSTER_NAME> \
    --workload-pool=<PROJECT_ID>.svc.id.goog

kubectl create serviceaccount gke-workload-sa

gcloud iam service-accounts create my-gcp-sa \
    --project=<PROJECT_ID>

gcloud projects add-iam-policy-binding <PROJECT_ID> \
    --member="serviceAccount:my-gcp-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
    --role="<ROLE_NAME>"

gcloud iam service-accounts add-iam-policy-binding \
    my-gcp-sa@<PROJECT_ID>.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:<PROJECT_ID>.svc.id.goog[<NAMESPACE>/gke-workload-sa]"

kubectl annotate serviceaccount \
    gke-workload-sa \
    iam.gke.io/gcp-service-account=my-gcp-sa@<PROJECT_ID>.iam.gserviceaccount.com \
    --namespace=<NAMESPACE>
