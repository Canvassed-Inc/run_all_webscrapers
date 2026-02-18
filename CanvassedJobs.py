from AWSBatchJob import AWSBatchJob


kidder_matthews = AWSBatchJob(
    job_definition="scraper_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/fargate_on_demand_queue",
    job_name="Kidder Matthews",
    override_command=["python", "kidder_matthews.py"],
    vcpu_override=8,
    memory_override_mb=32768,
)

colliers = AWSBatchJob(
    job_definition="colliers_worker_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/fargate_on_demand_queue",
    job_name="Colliers",
    envs={"MODE": "MASTER"},
    vcpu_override=4,
    memory_override_mb=16384,
)

coldwell = AWSBatchJob(
    job_definition="scraper_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/fargate_on_demand_queue",
    job_name="Coldwell",
    override_command=["python", "coldwell_commercial.py"],
    vcpu_override=8,
    memory_override_mb=32768,
)

cbre = AWSBatchJob(
    job_definition="scraper_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/fargate_on_demand_queue",
    job_name="CBRE",
    override_command=["python","/app/Requests/cbre_requests.py"],
    vcpu_override=4,
    memory_override_mb=32768,
)

cw = AWSBatchJob(
    job_definition="scraper_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/fargate_on_demand_queue",
    job_name="Cushman",
    override_command=["python","/app/Requests/cushman_and_wakefield/cw.py"],
    vcpu_override=4,
    memory_override_mb=32768,
)

run_all = AWSBatchJob(
    job_definition="scraper_definition",
    job_queue="arn:aws:batch:us-east-1:362644105056:job-queue/webscraper_queue",
    job_name="Run_All",
    override_command=["python", "dispatch.py"],
    array_size=600
)

class CanvassedJobs:
    def __init__(self):
        self.jobs_list = [run_all,
                          colliers,
                          cbre,
                          cw,
                          kidder_matthews,
                          coldwell]
