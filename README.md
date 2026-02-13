# Image Classification API
> FastAPI ML App with ResNet50 CNN

This project implements a microservice-based image classification system that automatically categorizes user-uploaded images into 1,000+ categories using a pre-trained ResNet50 Convolutional Neural Network. The solution consists of a FastAPI backend, Streamlit web UI, and a TensorFlow-based model service communicating through Redis.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Dataset Description](#dataset-description)
- [Modeling Approach](#modeling-approach)
- [Evaluation Metrics](#evaluation-metrics)
- [Results](#results)
- [How to Run](#how-to-run)
- [Architecture Diagram](#architecture-diagram)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)

---

## Problem Statement

Companies with large image collections need to automatically classify images into different categories. Manual classification is time-consuming and error-prone when done by human workers.

### Business Requirements

The solution must:

- **Accept user-uploaded images** via a web interface
- **Preprocess images** automatically (resize, normalize)
- **Classify images** into over 1,000 categories using a Convolutional Neural Network
- **Return predictions** as JSON with predicted class and confidence score
- **Handle errors gracefully** with informative error messages
- **Collect user feedback** on model predictions for continuous improvement

### Technical Requirements

The system is implemented as a distributed microservices architecture:

- **FastAPI backend** for REST API endpoints, user authentication, and database management
- **Streamlit web UI** for user interaction and image upload
- **TensorFlow model service** for running CNN inference
- **Redis** for asynchronous job queue communication between services
- **PostgreSQL** for storing user data and feedback

---

## Dataset Description

### Model Training Data

The system uses a **pre-trained ResNet50 model** with weights trained on the **ImageNet** (ILSVRC) dataset:

- **Dataset**: ImageNet Large Scale Visual Recognition Challenge (ILSVRC)
- **Classes**: 1,000 object categories including animals, objects, vehicles, food items, and scenes
- **Input Format**: RGB images resized to 224×224 pixels
- **Preprocessing**: ImageNet standard preprocessing (pixel normalization and scaling)
- **Source**: [ImageNet](https://www.image-net.org/) - large-scale image dataset used for training and benchmarking CNNs

### Runtime Data

No custom dataset is required to run the service. Users supply images at inference time through the web UI or API endpoints. The system accepts common image formats (JPEG, PNG) and handles preprocessing automatically.

---

## Modeling Approach

### Model Architecture

- **Model**: ResNet50 (Residual Neural Network with 50 layers)
- **Framework**: TensorFlow/Keras `applications.ResNet50`
- **Weights**: Pre-trained ImageNet weights (`weights="imagenet"`)
- **Task**: Single-label classification over 1,000 ImageNet classes

### Inference Pipeline

The classification process follows these steps:

1. **Image Upload**: User uploads image via Streamlit UI or API endpoint
2. **File Storage**: API saves uploaded image to disk and computes file hash
3. **Job Queue**: API creates a prediction job and pushes it to Redis queue
4. **Model Processing**: Model service pulls job from Redis queue
5. **Image Preprocessing**:
   - Load image from disk
   - Resize to 224×224 pixels
   - Convert to numpy array
   - Add batch dimension
   - Apply ImageNet preprocessing (`preprocess_input`)
6. **Inference**: Run ResNet50 model prediction
7. **Decode Results**: Extract top-1 prediction class and confidence score using `decode_predictions`
8. **Response**: Model service writes results back to Redis, API retrieves and returns JSON response

### Deployment Architecture

The model runs in a dedicated **model service** container that:

- Continuously polls Redis for new prediction jobs
- Processes images using the loaded ResNet50 model
- Writes prediction results back to Redis using the original job ID
- Supports horizontal scaling (multiple model instances can process jobs in parallel)

---

## Evaluation Metrics

Since this project uses a pre-trained model, evaluation focuses on **system performance** rather than classification accuracy:

### Performance Metrics

- **Throughput**: Requests per second (RPS) - measures system capacity
- **Latency**: Response time metrics
  - Median response time (ms)
  - Average response time (ms)
  - Broken down by endpoint (`/model/predict` vs `/user/`)
- **Failure Rate**: Percentage of failed requests under load
- **Scaling Performance**: Comparison of single vs multiple model instances

### Testing Methodology

Load testing was performed using **Locust** stress testing framework:

- **Test Scenarios**: 10, 25, 50, and 100 concurrent users
- **Endpoints Tested**: 
  - `GET /user/` - Lightweight database query endpoint
  - `POST /model/predict` - Heavy ML inference endpoint
- **Scaling Comparison**: Performance with 1 model instance vs 2 model instances

---

## Results

### Test Environment

- **CPU**: Intel Core i7-7660U @ 2.50 GHz
- **RAM**: 8 GB
- **OS**: Windows 10
- **Testing Tool**: Locust

### Performance Summary

| Load Level | 1 Model Instance | 2 Model Instances |
|------------|------------------|-------------------|
| **10 users** | 0% failures, 3.3 RPS<br>230 ms predict median | 0% failures, 3.2 RPS<br>320 ms predict median |
| **25 users** | 0% failures, 6.4 RPS<br>830 ms predict median | 0% failures, 5.5 RPS<br>590 ms predict median |
| **50 users** | 1% failures, 5.3 RPS<br>1,700 ms predict median | 4% failures, 1.0 RPS<br>1,700 ms predict median |
| **100 users** | 17% failures, 7.5 RPS<br>2,200 ms predict median | 22% failures, 2.4 RPS<br>1,800 ms predict median |

### Key Findings

- **Single instance performance**: One model instance provides better or equal throughput and lower failure rates in most scenarios
- **Scaling impact**: Two instances showed marginal improvement only at 25 users (29% faster predictions), but performed worse at other load levels
- **Bottleneck analysis**: Under high load (50+ users), the bottleneck shifts from model processing to other components (Redis queue, API workers, or database connections)
- **Recommendation**: Use 1 model instance for optimal throughput and lower failure rates

Detailed stress testing results and analysis are available in [ML_API_STRESS_TESTING_REPORT.md](./ML_API_STRESS_TESTING_REPORT.md).

---

## How to Run

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- Optional: WSL2 on Windows for better Docker performance

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd Sprint_03-Marissa_Singh
```

### Step 2: Environment Setup

```bash
# Copy environment template
cp .env.original .env

# Create Docker network
docker network create shared_network
```

### Step 3: Start All Services

```bash
# Build and start all containers
docker-compose up --build -d
```

### Step 4: Populate Database (First Time Only)

```bash
cd api
cp .env.original .env
docker-compose up --build -d
cd ..
```

### Step 5: Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | `admin@example.com` / `admin` |
| **Web UI** | http://localhost:9090 | `admin@example.com` / `admin` |

**API Usage:**
- Navigate to http://localhost:8000/docs
- Click "Authorize" button
- Enter credentials: `admin@example.com` / `admin`
- Test endpoints interactively

**Web UI Usage:**
- Navigate to http://localhost:9090
- Log in with `admin@example.com` / `admin`
- Upload an image file
- Click "Classify" to get predictions
- Optionally submit feedback on predictions

### Step 6: Stop Services

```bash
docker-compose down
```

### Mac M1 Users

For Apple Silicon Macs, additional configuration is required:

1. Modify `docker-compose.yml` to use `model/Dockerfile.M1` instead of `model/Dockerfile`
2. Remove TensorFlow from `model/requirements.txt` (M1 Dockerfile handles TensorFlow installation separately)
3. Remember to revert these changes before submission

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────────────┐     │
│  │  Streamlit UI    │         │  API Clients              │     │
│  │  (Port 9090)     │         │  (Swagger, curl, etc.)    │     │
│  └──────────────────┘         └──────────────────────────┘     │
│           │                              │                      │
└───────────┼──────────────────────────────┼──────────────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API SERVICE                                │
│                      (FastAPI)                                  │
├─────────────────────────────────────────────────────────────────┤
│  • User Authentication (JWT)                                   │
│  • User Management                                              │
│  • Image Upload & Storage                                       │
│  • Prediction Request Queueing                                  │
│  • Feedback Collection                                          │
└─────────────────────────────────────────────────────────────────┘
            │                              │
            │                              │
            ▼                              ▼
┌──────────────────────┐         ┌──────────────────────────┐
│   Redis Queue        │         │   PostgreSQL Database     │
│   (Job Queue)        │         │   (Users & Feedback)     │
└──────────────────────┘         └──────────────────────────┘
            │
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL SERVICE                                 │
│                    (ResNet50 CNN)                                │
├─────────────────────────────────────────────────────────────────┤
│  • Poll Redis for prediction jobs                               │
│  • Load and preprocess images                                   │
│  • Run ResNet50 inference                                       │
│  • Write results back to Redis                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication Flow

1. **User Request**: User uploads image via UI or API
2. **API Processing**: API saves image, creates job, pushes to Redis queue
3. **Model Processing**: Model service pulls job, runs inference, writes results to Redis
4. **Response**: API retrieves results from Redis, returns JSON to user
5. **Feedback**: User can submit feedback, stored in PostgreSQL

A detailed architecture diagram is available at `System_architecture_diagram.png` in the project root.

---

## Project Structure

```
Sprint_03-Marissa_Singh/
├── api/                              # FastAPI backend service
│   ├── app/
│   │   ├── auth/                     # JWT authentication
│   │   │   ├── jwt.py
│   │   │   ├── router.py
│   │   │   └── schema.py
│   │   ├── feedback/                 # Feedback endpoints
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schema.py
│   │   │   └── services.py
│   │   ├── model/                    # Prediction endpoints
│   │   │   ├── router.py
│   │   │   ├── schema.py
│   │   │   └── services.py
│   │   ├── user/                     # User management
│   │   │   ├── hashing.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   ├── schema.py
│   │   │   ├── services.py
│   │   │   └── validator.py
│   │   ├── db.py                     # Database configuration
│   │   ├── settings.py               # API settings
│   │   └── utils.py                  # Utility functions
│   ├── tests/                        # API unit tests
│   ├── Dockerfile
│   ├── Dockerfile.populate
│   ├── main.py                       # FastAPI application entry
│   ├── populate_db.py                # Database initialization
│   └── requirements.txt
├── model/                             # ML model service
│   ├── tests/                        # Model unit tests
│   ├── Dockerfile
│   ├── Dockerfile.M1                  # M1 Mac support
│   ├── ml_service.py                  # Model inference service
│   ├── settings.py
│   └── requirements.txt
├── ui/                                # Streamlit web UI
│   ├── app/
│   │   ├── image_classifier_app.py   # Main UI application
│   │   └── settings.py
│   ├── tests/                        # UI unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── tests/                             # Integration tests
│   ├── test_integration.py
│   └── requirements.txt
├── stress_test/                      # Load testing
│   ├── locustfile.py                 # Locust test scenarios
│   └── dog.jpeg
├── docker-compose.yml                 # Service orchestration
├── .env.original                      # Environment template
├── README.md                          # This file
├── ML_API_STRESS_TESTING_REPORT.md    # Performance analysis
├── System_architecture_diagram.png     # Architecture visualization
├── fastapi_docs.png                   # API docs screenshot
├── ui_login.png                       # UI login screenshot
└── ui_classify.png                    # UI classification screenshot
```

---

## Technologies Used

- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Streamlit**: Web UI framework for Python applications
- **TensorFlow/Keras**: Deep learning framework for CNN model
- **ResNet50**: Pre-trained convolutional neural network architecture
- **Redis**: In-memory data structure store for job queue
- **PostgreSQL**: Relational database for user and feedback data
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container Docker application orchestration
- **Locust**: Load testing framework for stress testing
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Pytest**: Testing framework
- **Black**: Code formatter
- **isort**: Import statement sorter

---

## Tests & Code Style

### Running Tests

#### Unit Tests (Docker)

```bash
# API tests
cd api
docker build -t fastapi_test --progress=plain --target test .

# Model tests
cd model
docker build -t model_test --progress=plain --target test .

# UI tests
cd ui
docker build -t ui_test --progress=plain --target test .
```

#### Integration Tests

With all services running and Python dependencies installed:

```bash
pip3 install -r tests/requirements.txt
python tests/test_integration.py
```

### Code Formatting

This project uses Black and isort for code formatting:

```bash
isort --profile=black . && black --line-length 88 .
```

---

## License

This project is part of an educational course assignment.

---

## Author

Marissa Singh

---

## Acknowledgments

- ImageNet project for providing the pre-trained ResNet50 model weights
- FastAPI, Streamlit, and TensorFlow communities for excellent documentation
- Docker and Redis for enabling microservices architecture
