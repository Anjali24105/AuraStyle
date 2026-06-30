# 👗 AuraStyle – Multimodal E-Commerce Fashion & Text-to-Image Trend Matcher

AuraStyle is an AI-powered fashion search application that enables users to discover fashion products using natural language descriptions, uploaded images, or both simultaneously. The project leverages OpenAI's CLIP model to understand the semantic relationship between text and images, providing intelligent and visually relevant product recommendations.

---

## 🚀 Features

* 🔍 Natural Language Fashion Search
* 🖼️ Image-Based Product Search
* 🤖 AI-Powered Multimodal Search using OpenAI CLIP
* 📦 MongoDB Product Catalog
* 📊 Cosine Similarity Ranking
* 💻 Responsive Web Interface
* ⚡ Fast Product Retrieval
* 👗 Fashion Catalog with 96 Products

---

## 🛠️ Technologies Used

### Backend

* Python
* Flask

### Database

* MongoDB

### Artificial Intelligence

* OpenAI CLIP (ViT-B/32)
* PyTorch
* Hugging Face Transformers

### Frontend

* HTML5
* CSS3
* JavaScript

### Libraries

* NumPy
* Pillow
* OpenCV

---

## 📂 Project Structure

```text
AuraStyle/
│── app.py
│── config.py
│── requirements.txt
│── seed_db.py
│── expand_catalog.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   └── index.html
│
└── utils/
    ├── database.py
    ├── embedder.py
    ├── audio.py
    └── __init__.py
```

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/Anjali24105/AuraStyle.git
```

2. Open the project folder

```bash
cd AuraStyle
```

3. Install the required libraries

```bash
pip install -r requirements.txt
```

4. Seed the MongoDB database

```bash
python seed_db.py
```

5. Run the application

```bash
python app.py
```

6. Open your browser

```text
http://127.0.0.1:5000
```

---

## 🧠 How It Works

1. The user enters a text query or uploads a fashion image.
2. The CLIP model generates embedding vectors.
3. Product embeddings stored in MongoDB are compared using cosine similarity.
4. The Top 10 most relevant fashion products are retrieved.
5. Results are displayed through the Flask web interface.

---

## 📊 Project Highlights

* AI-powered semantic fashion search
* Multimodal search (Text + Image)
* Responsive UI
* 96 Fashion Products
* MongoDB Integration
* Flask REST APIs
* CLIP Embedding Generation

---

## 🔮 Future Enhancements

* Voice Search Support
* User Authentication
* Shopping Cart & Wishlist
* Personalized Recommendations
* Cloud Deployment
* Larger Product Catalog

---

## 👩‍💻 Author

**Anjali Yanamadala**

B.Tech – Artificial Intelligence & Machine Learning

Aditya College of Engineering & Technology (ACET)

---

## 📜 License

This project was developed for academic and learning purposes.
