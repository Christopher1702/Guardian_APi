# AI-Powered Weekly Scheduler and Meal Planner API

This project is a FastAPI backend that integrates with Google Gemini AI and Firebase to enable intelligent weekly schedule management, meal planning, and image-based class schedule extraction. It includes endpoints for uploading schedules, editing daily agendas, generating meals with images, and storing everything in Firestore.

## Features

- 🔍 **Text-based schedule editing** via Gemini AI
- 🖼️ **Image upload for class schedule recognition**
- 🍽️ **AI-generated meals** with auto-fetched images from Pexels
- 🔥 **Firestore integration** for persistent user storage
- 🌐 **CORS-enabled API** for frontend compatibility

---

## Endpoints Overview

### `GET /`
Simple health check to confirm the server is running.

### `POST /save`
Updates a user's schedule based on natural language input. Requires the day of the week to be mentioned in the request.

### `POST /read`
Retrieves the user's class schedule for a given day (nested in `Every_Week` Firestore subcollections).

### `POST /agenda`
Retrieves the user's daily agenda from the main schedule.

### `POST /school_class_schedule`
Uploads an image of a weekly class schedule, extracts day-wise data using Gemini AI, and stores it in Firestore.

### `POST /meal_build`
Generates a full recipe and meal name from user input, saves it to Firestore, and fetches an image link from Pexels.

### `GET /fetch_recipe`
Returns the stored meal recipe for Monday.

### `GET /meal_img_link`
Returns the stored image URL for the Monday meal.
