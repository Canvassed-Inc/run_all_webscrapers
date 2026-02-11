from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional
import boto3
from botocore.exceptions import ClientError


def _get_env(*names: str) -> Optional[str]:
    """Return the first non-empty env var from `names`."""
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return None


@dataclass
class AWSBatchJob:
    job_definition: str                 # ARN or name:revision
    job_queue: str                      # ARN or name
    job_name: str                       # friendly name for the run

    # Optional config (if None, pulled from env)
    region: Optional[str] = None
    array_size: Optional[int] = None    # set to int to submit an array job

    # Container overrides
    override_command: Optional[list[str]] = None
    envs: dict[str, str] = field(default_factory=dict)
    vcpu_override: Optional[int] = None
    memory_override_mb: Optional[int] = None

    # AWS creds (if None, pulled from env; otherwise boto3 default chain still works)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None  # optional, e.g., for SSO/STS creds

    def _resolve_aws_config(self) -> tuple[Optional[str], Optional[str], Optional[str], str]:
        """
        Resolve creds/region from explicitly passed values, else environment variables.
        Falls back to boto3's default credential chain if keys are not present.
        """
        access_key = self.aws_access_key_id or _get_env("AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY")
        secret_key = self.aws_secret_access_key or _get_env("AWS_SECRET_ACCESS_KEY", "AWS_SECRET_KEY")
        session_token = self.aws_session_token or _get_env("AWS_SESSION_TOKEN")

        region = (
            self.region
            or _get_env("AWS_REGION", "AWS_DEFAULT_REGION")
            or "us-east-1"
        )

        return access_key, secret_key, session_token, region

    def _build_container_overrides(self) -> dict:
        overrides: dict = {}

        if self.override_command:
            overrides["command"] = self.override_command

        if self.envs:
            overrides["environment"] = [{"name": k, "value": str(v)} for k, v in self.envs.items()]

        # Works for many job defs; some Fargate setups use resourceRequirements instead.
        if self.vcpu_override is not None:
            overrides["vcpus"] = int(self.vcpu_override)

        if self.memory_override_mb is not None:
            overrides["memory"] = int(self.memory_override_mb)

        return overrides

    def build_submit_args(self) -> dict:
        args: dict = {
            "jobName": self.job_name,
            "jobQueue": self.job_queue,
            "jobDefinition": self.job_definition,
        }

        container_overrides = self._build_container_overrides()
        if container_overrides:
            args["containerOverrides"] = container_overrides

        if self.array_size is not None:
            args["arrayProperties"] = {"size": int(self.array_size)}

        return args

    def submit(self) -> str:
        """
        Submits the job to AWS Batch.
        Returns: jobId
        """
        access_key, secret_key, session_token, region = self._resolve_aws_config()

        # If keys aren't present, boto3 will fall back to its normal credential chain
        # (profiles, IAM role, etc.). If keys ARE present, we use them explicitly.
        client_kwargs = {"region_name": region}
        if access_key and secret_key:
            client_kwargs.update(
                {
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret_key,
                }
            )
            if session_token:
                client_kwargs["aws_session_token"] = session_token

        batch = boto3.client("batch", **client_kwargs)
        args = self.build_submit_args()

        try:
            resp = batch.submit_job(**args)
        except ClientError as e:
            raise RuntimeError(f"AWS Batch submit_job failed: {e}") from e

        return resp["jobId"]