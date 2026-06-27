# Outer Wilds Space Tours

**Live Deployment URL**: [https://moienheydari.pythonanywhere.com/](https://moienheydari.pythonanywhere.com/)

**⚠️ This website is designed and optimized for Desktop screens. ⚠️**

---

## Pre-configured Users

Use the credentials below to log in and test different roles:

### 1. Guides
| Name | Email | Password |
| :--- | :--- | :--- |
| **Jack Black** | `jackblack@gmail.com` | `test123` |
| **Chert Wild** | `cherwild@gmail.com` | `test111` |
| **John Cena** | `youcantseeme@gmail.com` | `wwewwe` |
| **Sam Sung** | `samsung@gmail.com` | `123456789` |
| **Nemo Nobody** | `mrnobody@gmail.com` | `19991999` |

### 2. Participants
| Name | Email | Password |
| :--- | :--- | :--- |
| **Moien Heydari** | `moien@gmail.com` | `test999` |
| **Ali Sams** | `aliali@gmail.com` | `testtest` |
| **John Doe** | `verygood@gmail.com` | `testyes` |
| **Tom Chillie** | `tom@gmail.com` | `123456` |
| **Ali Kaz** | `alikaz@gmail.com` | `123123` |

### 3. Administrator
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `moienheydari@gmail.com` | `admin123` |

---

## Testing Instructions

### 1. Local Setup and Execution
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open your web browser and navigate to the local address (typically `http://127.0.0.1:5000/`).

---

### 2. Testing Scenarios

#### A. Participant Testing
1. **Log in** as a Participant (e.g., `moien@gmail.com` / `test999`).
2. **Book a Tour**:
   - Go to the homepage and click on an upcoming tour card, or use the filters to find a tour.
   - Select a date and time from the available schedule, choose a party size (1–4), and enter guest names if reserving multiple spots.
   - Test validation constraints: you cannot book a tour on dates it is not offered, nor can you book a tour that conflicts (in date, time, and duration) with any of your existing reservations.
3. **Cancel a Reservation**:
   - Go to your **Profile** page.
   - You can cancel any reservation as long as the cancellation is performed at least 24 hours prior to the tour start time. If the tour starts within 24 hours, the cancellation button is disabled.

#### B. Guide Testing
1. **Log in** as a Guide (e.g., `jackblack@gmail.com` / `test123`).
2. **Create a Tour**:
   - Click **Create Tour** in the navigation.
   - Fill in details: title, description, duration, language (restricted to languages you speak), meeting point, weekly schedule days and start times, itinerary stops (minimum 4), and promotional photos.
3. **Edit a Tour**:
   - Go to your **Profile** page and click **Edit** next to one of your tours.
   - If the tour has no reservations, you can edit all details, including essential fields (duration, max capacity, meeting point, schedule, and stops).
   - If the tour has reservations, essential fields are locked and cannot be changed. Only non-essential fields (title, description, and photos) can be edited.
4. **Report a Completed Tour**:
   - Once a tour date has passed, guides must report the actual attendance.
   - Go to your **Profile** page, find the past tour, and click **Report**.
   - Input the actual participant count and upload a proof photo (JPG, JPEG, or PNG) to submit the report.

#### C. Administrator Testing
1. **Log in** as the Admin (`moienheydari@gmail.com` / `admin123`).
2. **Dashboard Overview**:
   - Go to the **Profile** page to access the administrator dashboard.
   - View key metrics: total guides, total participants, total tours, and total reservations.
   - View a breakdown of reservations by language.
   - Inspect the list of all registered guides and their corresponding tours.
   - Click on tours to view their details and the reservations.
