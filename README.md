

# YOLOv8 Object Detection Dashboard

## Introduction

This project is a web-based dashboard for YOLOv8 object detection and road quality assessment. It provides a user-friendly interface for uploading images or videos, detecting objects using the YOLOv8 model, and mapping road quality on a map with corresponding coordinates.

## Features

- **Image and Video Upload**: Upload images or videos for object detection.
- **Object Detection**: Utilizes YOLOv8 for detecting objects in uploaded media.
- **Road Quality Mapping**: Visual representation of road quality on a map, categorized by quality levels.
- **Interactive Map**: Users can interact with the map to add markers and create routes.
- **Route Analysis**: Provides distance calculations and segments routes based on road quality.

## Setup

### Prerequisites

- Python 3.8 or above
- Flask
- OpenCV
- TomTom Maps SDK
- Other dependencies listed in `requirements.txt`

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/YOLOv8-Object-Detection-Dashboard.git
   cd YOLOv8-Object-Detection-Dashboard
   ```

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys:**

   Replace `APIKEY` in the `main.py` and the HTML files with your TomTom API key.

4. **Run the application:**

   ```bash
   python main.py
   ```

   The application will be available at `http://localhost:5000`.

## Usage

1. **Upload Media:**
   - Navigate to the upload section and choose an image or video file.
   - Click "Upload" to start the object detection process.

2. **View Results:**
   - The detected objects will be displayed on the same page.
   - The road quality information will be shown below the detected objects.

3. **Map Interaction:**
   - Use the map to visualize the route and road quality.
   - Add markers by clicking on the map or by entering coordinates.
   - Create a route by selecting the "Create Route" option.
   - Choose the travel mode (car, motorcycle, truck, pedestrian, bicycle) to get the route.

## Code Overview

### `main.py`

The main backend logic, handling the Flask server, route definitions, and object detection using YOLOv8. It also includes functions for road quality assessment and mapping.

### `templates/base.html`

The base HTML file, providing the structure for the web application. It includes the necessary CSS and JS files and defines the layout.

### `templates/dashboard.html`

The main dashboard page, containing the content for image/video upload, object detection results, and the interactive map.

### `static/assets/`

Contains static files like CSS, JS, and images used in the application.

## Contributing

Feel free to fork this repository and contribute by submitting a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [YOLOv8](https://github.com/ultralytics/yolov8) for object detection.
- [TomTom Maps SDK](https://developer.tomtom.com/maps-sdk-web) for map integration.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Bootstrap](https://getbootstrap.com/) for front-end design.

---

You can copy and paste this `README.md` content into your GitHub repository. Adjust any specific details as needed.
