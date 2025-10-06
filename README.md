# GreenCompanion
Green Companion: A smart gardening web app that detects soil type, recommends plants, tracks growth, and provides weather-based care tips. Users can save their garden, log plant progress, and manage everything with Firebase authentication and storage.
Green Companion is a web application that helps users identify soil types, select suitable plants, and track the growth of their garden with tailored care advice. It integrates weather data and provides guidance on watering, pest control, and seasonal care.

Features
Soil Detection: Upload a photo of your soil, and the app predicts its type using a trained ML model.
Plant Recommendations: Get a curated list of plants suitable for your soil type, along with care tips and optimal growing seasons.
Garden Management: Save selected plants to your personal garden and track their growth over time.
Growth Logging: Add notes, dates, and care activities for each plant and view detailed growth logs.
Weather Integration: Automatic or manual city-based weather updates with advice on watering and care.
User Authentication: Secure login and registration powered by Firebase, with personalized data storage.
Responsive Dashboard: Central hub for garden management, growth tracking, and weather monitoring.


Technology Stack
Backend: Python, Flask
Frontend: HTML, CSS (responsive design)
Database: Firebase Firestore
Machine Learning: TensorFlow Keras (soil classification model)
APIs: OpenWeatherMap for live weather data

Usage
1. Register or log in to access your personal dashboard.
2. Upload soil images to classify the soil type.
3. Add recommended plants to your garden.
4. Track growth and add notes for each plant.
5. Check the weather and follow care advice automatically.



Folder Structure
app.py – Main Flask application
soil_classifier.py – Soil classification ML logic
data_loader.py – Loads plant, tip, and season data
templates/ – HTML templates for frontend
static/ – CSS, images, and uploads
soil_model.h5 – Pre-trained soil classification model
class_indices.json – Mapping of soil classes


Copyright (c) 2025 [Rushil]. All rights reserved.

This source code and all associated files are proprietary. Viewing is permitted for educational and demonstration purposes only. Copying, modifying, redistributing, or using this project in any form without explicit permission is strictly prohibited.
