## 🚀 GEO-FENCING: Revolutionizing Indian Railways 🌍

Welcome to **GEO-FENCING**, where technology meets the tracks! 🚂 This is **NOT just another repo**—this is the future of **Indian Railways**, powered by **GPS magic 🧙‍♂️**, cutting-edge tech, and a sprinkle of genius 🧠.

---

## 💡 **What is this madness?**

Imagine this:  
You’re on a train, gliding through the countryside, and BOOM! You get a friendly **ping** saying, *“Welcome to New Delhi Station, please prepare to disembark!”*.  

Or maybe you’re chilling, sipping chai 🫖, and suddenly—your GPS-tagged bag *tries to escape*! 🚨 No sweat, our system instantly alerts you: *“Hey, someone’s being naughty with your luggage!”*

This repo makes it all possible with **geo-fencing** technology! 🌐

---

## 🎯 **Mission: Impossible? Not anymore!**

We’ve got two big goals 🚀:
1. **Station Entry Alert**: Notify passengers when a train enters a station’s **1 km GPS radius.**  
2. **Theft Alert**: Detect and alert when a **GPS-tagged object (like your bag 👜)** moves outside the geo-fenced boundary of the train coach.  

---

## 🔥 **Why You’ll Love This**

- **📡 Real-Time Tracking**: Because the future waits for no one.  
- **🛡️ Luggage Protection**: Your bags are safe, even when you’re not looking.  
- **🌍 Precision Matters**: Powered by the **Haversine Formula**—yes, we do math here.  
- **🚉 Scalable Awesomeness**: Multiple trains, stations, and objects? No problem.  
- **💡 Genius Built-In**: FastAPI + MongoDB = backend sorcery.  

---

## 🎛️ **How Does it Work?**

### 🗺️ Geo-Fencing Magic

1. **Station Entry Alert**:  
   - A train’s GPS location is continuously monitored.  
   - When it enters a station’s **1 km radius**, an alert is triggered.  
   - *“Welcome to your destination!”* 🎉

2. **Theft Alert**:  
   - GPS-tagged objects (like bags) are tracked within a train coach.  
   - If an object moves **outside the geo-fenced radius**, an alert is triggered.  
   - *“Hey! Someone’s stealing your bag!”* 🏃‍♂️💨

3. **Haversine Formula**:  
   - Calculates distances between GPS coordinates.  
   - It’s like rocket science, but cooler. 🚀  

---

## 🗂️ **Database: Where the Magic Lives**

We’re using **MongoDB** to store everything that matters.

### 1. **Users** 🙋‍♂️
Stores passenger details and their registered objects.  
```json
{
  "_id": "user_id",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+91-9876543210",
  "registered_objects": ["object_id_1", "object_id_2"]
}
```

### 2. **Stations** 🚉
Tracks station names and GPS coordinates.  
```json
{
  "_id": "station_id",
  "name": "New Delhi Station",
  "coordinates": { "latitude": 28.6139, "longitude": 77.2090 }
}
```

### 3. **Trains** 🚂
Monitors train locations and geo-fencing radius.  
```json
{
  "_id": "train_id",
  "name": "Rajdhani Express",
  "current_location": { "latitude": 28.5562, "longitude": 77.1000 },
  "geo_fenced_radius": 1000  // in meters
}
```

### 4. **Objects** 👜
Tracks GPS-tagged objects like bags.  
```json
{
  "_id": "object_id",
  "name": "Passenger Bag",
  "current_location": { "latitude": 28.5562, "longitude": 77.1000 },
  "train_id": "train_id",  // Associated train
  "geo_fenced_radius": 10  // in meters
}
```

---

## ⚙️ **REST API: Your Command Center**

### 1. Add New Stuff
```http
POST /add-entity/
```
Add stations 🚉, trains 🚂, or objects 👜.

### 2. Update Locations in Real-Time
```http
POST /update-location/
```
Update GPS locations for trains or objects.

### 3. Trigger Alerts
```http
GET /check-alerts/
```
Get alerts for station entry or theft.

### 4. Fetch Details
```http
GET /get-entities/
```
Retrieve details about stations, trains, or objects.

---

## 🛠️ **How to Set It Up**

### Prerequisites:
- 🐍 Python 3.9+  
- 🍃 MongoDB  
- 📦 Python Libraries: `fastapi`, `pymongo`, `geopy`

### Steps:
1. **Clone the repo**:
   ```bash
   git clone https://github.com/advay77/GEO-FENCING.git
   cd GEO-FENCING
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi pymongo geopy
   ```

3. **Run the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Start MongoDB**:
   Make sure MongoDB is up and running locally or via a cloud service.

5. **Test the APIs**:
   Use **Postman** or **cURL** to test the endpoints.

---

## 🤝 **Contributing**

We’re building the future of Indian Railways, and we need YOU!  
- **Fork the repo** 🪝  
- **Create a branch** (`feature/your-idea`) 🌱  
- **Push your code** 🚀  
- **Submit a pull request** ✨  

---

## 📷 DEMO PHOTO


![Screenshot 2025-05-26 163715](https://github.com/user-attachments/assets/c5762b17-e6fd-41bb-ada9-37f5223dc975)


![Screenshot 2025-05-26 163735](https://github.com/user-attachments/assets/897404a0-6ddc-432d-aefc-8254c8f8a0c2)

## 📜 **License**

This project is licensed under the [MIT License](LICENSE). Feel free to use it, improve it, and share it with the world.

---

## 🌟 **Why Stop Here?**

This is just the beginning! Imagine a world where:  
- Trains run on time (okay, maybe not yet, but we’re getting there).  
- Passengers feel safe and informed.  
- Technology powers the tracks like never before.  

Let’s make it happen, one geo-fence at a time. 🌍✨

---

🎉 **GEO-FENCING: Where technology meets the tracks. All aboard!** 🚂
