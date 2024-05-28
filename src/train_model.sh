AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=kestra1cvops;AccountKey=Yrz/3SUhQUxToFl2x68UZvHnIh0hVXsj6BZvoEyCjdgbtGSFwdSrZJlgR9tJPIIo1c39t0iiSW8j+AStAW2TPA==;EndpointSuffix=core.windows.net"
ACCOUNT_NAME="kestra1cvops"
KESTRA_SERVER="http://48.216.240.225:8080"
TRAIN_NAMESPACE="model"
TRAIN_ID="train"

upload_data () {
    local tag=$1
    local container=$2
    local data_path=$3

    if [ -z "$tag" ]; then
        tag="test"
    fi

    echo "Uploading preprocessed data to Azure Blob"
    az storage container create -n "$container" --connection-string "$AZURE_CONNECTION_STRING"
    az storage blob upload-batch -s "$data_path" --account-name "$ACCOUNT_NAME" -d "$container" --overwrite --connection-string "$AZURE_CONNECTION_STRING"
}

create_kestra_train_workflow() {
    local tag=$1
    local container=$2

    curl --request POST -sL \
         --url "$KESTRA_SERVER/api/v1/executions/$TRAIN_NAMESPACE/$TRAIN_ID" \
         --form "tag=$tag" \
         --form "unprocessed_data_container=$container"
    printf "\n"
}

tag=$1
data_path=$2
if [ ! -d "$data_path" ]; then
    echo "Data path does not exist"
    exit 1
fi
container="data-preprocessed-$tag"

upload_data "$tag" "$container" "$data_path"
create_kestra_train_workflow "$tag" "$container"