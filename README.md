# FocusFlow Mobile 🚀

FocusFlow is an offline productivity, task management, and timetable generator application built entirely in Python using the **Flet** framework.  This project has evolved into a fully functional, cross-platform mobile application utilizing background asynchronous processing.

## 📱 Features

* **Task Management:** Create, delete, and track tasks with persistent offline storage (`.json`).
* **Smart Logging:** Tasks are automatically stamped with the day and date of creation.
* **One-Tap Cleanup:** Instantly wipe out completed tasks to keep your workspace clean.
* **Custom Pomodoro Timer:** Set personalized focus sessions using a native numeric keypad input.
* **Android-Native Asynchronous Execution:** The timer utilizes `asyncio` and Flet's `run_task()` to communicate directly with the Android OS. This prevents UI thread blocking and ensures the timer survives aggressive mobile battery-saving states.
* **Pause & Resume Memory:** Pause the timer at any exact second and resume seamlessly without resetting the loop.

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **UI Framework:** Flet (Flutter-based Python GUI)
* **Concurrency:** `asyncio` for non-blocking mobile execution
* **CI/CD:** GitHub Actions (Automated cloud compilation of the Android APK)

## ⚙️ Architecture Challenges Solved

Building Python for native Android presented unique thread-blocking challenges. Standard `time.sleep()` operations freeze the mobile UI, and standard `threading` fails to sync with Android's visual refresh rates. FocusFlow solves this by implementing an absolute-time tracking system synchronized via an asynchronous event loop, allowing the app to perfectly render background updates on mobile devices.

## 📥 Installation

Because FocusFlow is compiled natively via cloud actions, you can install it directly on your Android device!

1. Navigate to the **Actions** tab of this repository.
2. Click on the latest successful **Build Android APK** workflow run.
3. Scroll down to **Artifacts** and download the `FocusFlow-Mobile-App.zip` file.
4. Extract the `.apk` file, transfer it to your Android device, and install.

## 🚀 Local Development

To run this app locally on your machine:

```bash
# Clone the repository
git clone [https://github.com/Vivoboy11/focusflow.git](https://github.com/YOUR_USERNAME/focusflow.git)

# Install dependencies
pip install flet

# Run the app
flet run main.py