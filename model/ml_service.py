import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# Connect to Redis 
db = redis.Redis(
    host=settings.REDIS_IP,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_ID
)

# Load ML model 
model = ResNet50(include_top=True, weights="imagenet")
model.summary()


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    class_name = None
    pred_probability = None

    # Load the image
    try:
        img_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
        img = image.load_img(img_path, target_size=(224, 224))
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

    # -- Apply preprocessing -- 
    
    # Convert to numpy array 
    x = image.img_to_array(img)

    # Add an extra dimension to the array (model expects a batch of images)
    x_batch = np.expand_dims(x, axis=0)
    
    # Scale pixels values
    x_batch = preprocess_input(x_batch)

    # Get predictions
    preds = model.predict(x_batch, batch_size=256)
    
    # Decode TOP 1 prediction
    _, class_name, pred_probability = decode_predictions(preds, top=1)[0][0]

    # Convert probabilities to float and round it
    pred_probability = float(pred_probability)
    pred_probability = round(pred_probability, 4)

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:

        # Take a new job from Redis
        job = db.brpop(settings.REDIS_QUEUE)

        # Note: job is a tuple with the format (queue_name, job_data)
        job_data = json.loads(job[1])
        image_name = job_data["image_name"]

        # Get the original job ID
        job_id = job_data["id"]

        # Run the loaded ml model (use the predict() function)
        class_name, pred_probability = predict(image_name)

        # Prepare a new JSON with the results
        output = {"prediction": class_name, "score": pred_probability}

        # Store the job results on Redis 
        db.set(job_id, json.dumps(output))

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
