from CanvassedJobs import CanvassedJobs
import time

for job in CanvassedJobs().jobs_list:
    job.submit()
    print(f"✅ Submitted: {job.job_name} | queue={job.job_queue} | def={job.job_definition}")

    time.sleep(10)

    #Wait for them to finish

    # Kick off post processing