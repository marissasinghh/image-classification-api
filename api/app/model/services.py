import json
import time
from uuid import uuid4

import redis

from .. import settings

# Connect to Redis
db = db = redis.Redis(
    host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID
)


async def model_predict(image_name):
    print(f"Processing image {image_name}...")
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    image_name : str
        Name for the image uploaded by the user.

    Returns
    -------
    prediction, score : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    prediction = None
    score = None

    # Assign an unique ID
    job_id = str(uuid4())

    # Create a dict with the job data we will send through Redis
    job_data = {
        "id": job_id,
        "image_name": image_name,
    }

    # Send the job to the model service using Redis
    db.lpush(settings.REDIS_QUEUE, json.dumps(job_data))

    # Loop until we received the response from our ML model
    while True:
        try:
            output = db.get(job_id)
        except Exception as e:
            print(f"Error getting output from Redis: {e}")
            continue

        # Check if the text was correctly processed by our ML model
        if output is not None:
            output = json.loads(output.decode("utf-8"))
            prediction = output["prediction"]
            score = output["score"]

            db.delete(job_id)
            break

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

    return prediction, score
