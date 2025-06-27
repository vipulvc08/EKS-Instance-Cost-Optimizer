# 🚀 EKS Spot Instance Cost Optimizer

This project helps you dynamically identify the **cheapest EC2 instance types** for Amazon EKS clusters to reduce costs using Spot Instances. It supports multiple strategies:

- ✅ Preferred instance types
- ✅ Minimum and maximum vCPU range
- ✅ Public EC2 data from [instances.vantage.sh](https://instances.vantage.sh) (no AWS credentials required)

> This project is fully DIY and does **not rely on Karpenter** or managed autoscalers. You can integrate it with your own controller logic to update node groups or launch templates.

---

## 📁 Project Structure

```
.
├── config.yaml                        # Configuration file
├── fetch_cheapest_by_machine_type.py # Pick cheapest from preferred instance types
├── fetch_cheapest_by_min_max.py      # Pick cheapest using min and max CPU
├── fetch_cheapest_by_vantage.py      # Use public Vantage API to pick cheapest
├── Dockerfile                         # Optional Docker support
├── requirements.txt                  # Python requirements
└── README.md                         # This file
```

---

## ⚙️ Requirements

- Python 3.8 or newer
- AWS CLI configured (for boto3-based scripts)
- Python packages listed in `requirements.txt`:

### Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧾 config.yaml Example

This file controls all three scripts:

```yaml
region: ap-south-1

# CPU filter (used in fetch_cheapest_by_min_max)
min_cpu: 2
max_cpu: 4
include_burstable: true

# Preferred instance types (used in fetch_cheapest_by_machine_type)
preferred_instance_types:
  - t3.large
  - m6i.large
  - c5.large
  - c6i.large
```

---

## 🚀 How to Use

### 1️⃣ Fetch cheapest from preferred instance types

```bash
AWS_PROFILE=your-profile python3 fetch_cheapest_by_machine_type.py
```

---

### 2️⃣ Fetch cheapest by CPU range

```bash
AWS_PROFILE=your-profile python3 fetch_cheapest_by_min_max.py
```

---

### 3️⃣ Fetch cheapest from public vantage.sh data (no AWS access required)

```bash
python3 fetch_cheapest_by_vantage.py
```

---

## 🐳 Run via Docker (Optional)

### Build the image

```bash
docker build -t eks-spot-controller .
```

### Run one of the scripts

```bash
docker run --rm eks-spot-controller python3 fetch_cheapest_by_vantage.py
```

---

## ✅ Next Steps

You can extend this project to:
- Automatically update an EKS Launch Template or ASG
- Trigger a nodegroup refresh to launch cost-optimized nodes
- Add taints or labels to dynamically scheduled nodes

---

## 👤 Author

**Vipul Chaudhary**  
GitHub: [@vipulvc08](https://github.com/vipulvc08)

---

## 📜 License

MIT License
