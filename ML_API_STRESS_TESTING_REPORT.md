## ML API Stress Testing Report

### System Specs
- CPU: Intel(R) Core(TM) i7-7660U CPU @ 2.50GHz 
- RAM: 8502935552
- OS: Windows 10
- Test Tool: Locust

### What We Tested
Ran load tests on two API endpoints with different numbers of concurrent users. Compared performance with 1 model instance vs 2 model instances.

**Endpoints Tested:**
- GET `/user/` - Lightweight database query (index endpoint)
- POST `/model/predict` - Heavy ML inference (ResNet50)

**Test Setup:**
- Users tested: 10, 25, 50, 100
- Spawn rate: 5 users/second
- Duration: 2-3 minutes per test


### Results

**1 Model Instance (Baseline)**
- 10 Users: 489 requests, 0% failures, 12ms median response, 3.3 RPS
  - /model/predict: 230ms median, 361ms avg
  - /user/: 9ms median, 14ms avg
- 25 Users: 1,029 requests, 0% failures, 45ms median response, 6.4 RPS
  - /model/predict: 830ms median, 970ms avg
  - /user/: 19ms median, 131ms avg
- 50 Users: 835 requests, 1% failures, 1,100ms median response, 5.3 RPS
  - /model/predict: 1,700ms median, 2,425ms avg
  - /user/: 310ms median, 2,057ms avg
- 100 Users: 672 requests, 17% failures, 1,500ms median response, 7.5 RPS
  - /model/predict: 2,200ms median, 4,531ms avg
  - /user/: 1,100ms median, 5,065ms avg

**2 Model Instances (Scaled)**
- 10 Users: 484 requests, 0% failures, 17ms median response, 3.2 RPS
  - /model/predict: 320ms median, 1,062ms avg
  - /user/: 11ms median, 176ms avg
- 25 Users: 1,125 requests, 0% failures, 43ms median response, 5.5 RPS
  - /model/predict: 590ms median, 675ms avg
  - /user/: 21ms median, 122ms avg
- 50 Users: 634 requests, 4% failures, 1,200ms median response, 1.0 RPS
  - /model/predict: 1,700ms median, 2,549ms avg
  - /user/: 470ms median, 2,535ms avg
- 100 Users: 387 requests, 22% failures, 1,500ms median response, 2.4 RPS
  - /model/predict: 1,800ms median, 5,485ms avg
  - /user/: 1,100ms median, 6,799ms avg

### Key Takeaways

**Performance Comparison: 1 vs 2 Model Instances**

**10 Users:**
- 1 instance: 0% failures, 3.3 RPS, 230ms predict median
- 2 instances: 0% failures, 3.2 RPS, 320ms predict median
- **Winner: 1 instance** (28% faster predictions, similar throughput)

**25 Users:**
- 1 instance: 0% failures, 6.4 RPS, 830ms predict median
- 2 instances: 0% failures, 5.5 RPS, 590ms predict median
- **Winner: 2 instances** (29% faster predictions, though 14% lower throughput)

**50 Users:**
- 1 instance: 1% failures, 5.3 RPS, 1,700ms predict median
- 2 instances: 4% failures, 1.0 RPS, 1,700ms predict median
- **Winner: 1 instance** (same speed, 4x better throughput, 75% fewer failures)

**100 Users:**
- 1 instance: 17% failures, 7.5 RPS, 2,200ms predict median
- 2 instances: 22% failures, 2.4 RPS, 1,800ms predict median
- **Winner: 1 instance** (3x better throughput, lower failures, though 2 instances have slightly faster predictions)

**Interesting Finding:**
Scaling to 2 instances showed marginal improvement only at 25 users (29% faster predictions), and performed similarly at 100 users (18% faster predictions but 3x worse throughput). At other load levels (10 and 50 users), single instance consistently outperformed. This suggests the bottleneck shifts under high load from model processing to other components (Redis queue, API workers, or database connections).

### Recommendations

**For All Load Levels:**
- **Use 1 model instance** - outperforms or matches 2 instances in most key metrics
- At 10 users: 1 instance is 28% faster (230ms vs 320ms)
- At 25 users: 2 instances performs better (29% faster predictions)
- At 50 users: 1 instance has 5x better throughput and 75% fewer failures
- At 100 users: 1 instance has 3x better throughput and 23% fewer failures

**Bottom Line:**
Use 1 model instance for optimal throughput and lower failure rates. While 2 instances can provide marginally faster individual predictions at certain loads (25 users), the tradeoff in overall system throughput (3x worse at 100 users) and higher failure rates makes it inefficient. 