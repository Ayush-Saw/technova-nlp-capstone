"""Small MLflow alias helper. Register an evaluated model before assigning aliases."""
import mlflow
from mlflow.tracking import MlflowClient

def promote(model_name: str, version: str, alias: str):
    if alias not in {"champion","challenger"}: raise ValueError("Alias must be champion or challenger")
    client=MlflowClient()
    client.set_registered_model_alias(model_name,alias,version)
    return f"{model_name}@{alias} -> version {version}"
