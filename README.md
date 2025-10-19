# Musafir

![Getting Started](./images/Musafir.jpg)

**Musafir**: which means *“traveler”* in Arabic — is an AI-powered travel assistant designed to make exploring the world smarter and easier.  
It helps users discover destinations, plan trips, and get personalized travel insights using intelligent recommendations and real-time information.  

Built with modern AI technologies, **Musafir** combines conversational intelligence, data retrieval, and user feedback to create a seamless travel experience.  
Whether you're planning a weekend getaway or a global adventure, Musafir guides you every step of the way — from inspiration to itinerary.

## Problem Description & Motivation

Planning a trip can be overwhelming, travelers often spend hours searching across multiple platforms for information about destinations, attractions, accommodation, safety tips, and local experiences.  
The challenge is not the lack of data, but rather **information overload** and **fragmentation** across countless sources.

Traditional travel guides and search engines provide static results, while AI chatbots often generate generic answers without reliable or contextually relevant data.  
This creates a gap between **information availability** and **personalized, trustworthy recommendations**.

### Why Musafir?

**Musafir** was built to address these challenges by combining **retrieval-based search** and **AI-driven reasoning**.  
It delivers accurate, context-aware, and dynamic travel insights powered by real data.

Key goals include:
- 🧭 Centralizing travel knowledge from reliable sources like **Wikivoyage**.  
- 💬 Enabling **interactive conversations** with an AI assistant that understands context and preferences.  
- ⚙️ Providing **real-time retrieval** from structured data to generate personalized travel recommendations.  
- 📊 Allowing continuous improvement through a **feedback loop** that learns from user interactions.  
- 🧠 Bridging the gap between **AI creativity** and **authentic travel data** through a RAG architecture.

In short, **Musafir** transforms the way people plan their journeys — turning scattered travel data into meaningful, personalized experiences.


## Project Overview

**Musafir** is a Retrieval-Augmented Generation (RAG) application designed to assist users with their travel plans through intelligent, data-driven insights.

The main use cases include:
- 🗺️ **Destination Discovery:** Get personalized suggestions for destinations based on preferences, budget, and travel goals.  
- ✈️ **Trip Planning Assistance:** Generate step-by-step itineraries, including attractions, activities, and local recommendations.  
- 🏨 **Accommodation & Food Insights:** Retrieve useful information about hotels, restaurants, and hidden gems at your chosen location.  
- 💬 **Conversational Travel Assistant:** Interact naturally with an AI assistant to ask travel-related questions and receive context-aware answers.  

## Dataset

The dataset used in **Musafir** is retrieved from **Wikivoyage**, an open travel guide built and maintained by volunteers.  
For the current version, the application focuses on four major cities:

- 🏙️ **Cairo**  
- 🌆 **London**  
- 🏛️ **Rome**  
- 🌉 **Seoul**

Only selected sections from each city page have been ingested to ensure concise and relevant travel information.  
The extracted sections include:

`"districts"`, `"see"`, `"buy"`, `"eat"`, `"drink"`, `"sleep"`, and `"stay safe"`

If you wish to extend the dataset by adding more sections or cities, you can easily customize the ingestion process in: [notebooks/1. Ingest data.ipynb](notebooks/1.%20Ingest%20data.ipynb)
 
This notebook is a Python script customized to extract relevant data from Wikivoyage. It can be easily modified to specify which cities and sections to scrape, preparing the content for indexing in the retrieval pipeline.

The collected data is organized into two stages:
- **Raw data:** stored in [data/raw_data](data/raw_data)  
- **Processed and combined data:** stored in [data/processed_data/all_cities_combined_clean.csv](data/processed_data/all_cities_combined_clean.csv)

## Tech Stack

### Core Components

- **Programming Language:** Python  
- **Application Framework:** Streamlit — for building an interactive and user-friendly interface  
- **Containerization:** Docker & Docker Compose — for seamless deployment and environment management  

### Search & Retrieval

Musafir supports multiple retrieval backends for flexibility and experimentation:

1. **MinSearch** — A lightweight text search index using **TF-IDF** and **cosine similarity** for text fields, plus exact matching for keyword fields.  
2. **Elasticsearch** — Combines **text-based search** with **vector similarity search** for hybrid retrieval.  
3. **Qdrant** — A high-performance **vector database** for semantic retrieval and scalable RAG systems.

### AI & Language Model

- **LLM Models:** Supports free Mistralai models such as `mistralai/Mistral-7B-Instruct` and `mistralai/mistral-medium`.  
- **RAG Pipeline:** Integrates document retrieval with context-aware text generation.

### Data & Storage

- **Data Source:** A python script has been written to extract data from Wikivoyage website (specific sections for selected cities).  
- **Database:** PostgreSQL — used to store user conversations, RAG responses, and feedback.  

### Monitoring & Analytics

- **Grafana:** Used for real-time monitoring and visualization of application performance, conversation logs, and feedback metrics.
---

## Installation & Setup

Follow the steps below to set up and run **Musafir** on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/HagerAhmed/Musafir.git
cd Musafir
```
### 2. Create and Activate a Virtual Environment
#### For Linux / macOS:
```bash
python -m venv venv
source venv/bin/activate
```
#### For Windows (PowerShell):
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Run with Docker
```bash
docker compose up
```

### 5. Environment Variables
Create a .env file in the project root directory and add the following keys:

#### Mistral API Key (get yours here: https://admin.mistral.ai/organization/api-keys)
MISTRAL_API_KEY=your_mistral_api_key_here

#### PostgreSQL Configuration
- POSTGRES_USER=your_username

- POSTGRES_PASSWORD=your_password

### 6. Using OpenAI Instead of Mistral (Optional)
If you want to switch from Mistral to OpenAI, modify your LLM function as follows:
```bash
def llm(prompt):
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```
Add your OpenAI key to the .env file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 7. Run the Application
```bash
streamlit run app.py
```