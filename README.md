# PetBusJam Data & Level Generator 🚌🐾

Official lightweight repository for **PetBusJam** (built in Godot 4). It serves two main purposes:
1. **Static Content Server**: Delivers the `levels.json` file via GitHub Raw to update players' levels dynamically without submitting a new app build to Google Play.
2. **Procedural Level Generator**: Python 3 automation tool to generate, validate, and scale puzzle levels.

---

## 📂 Repository Structure

- `levels.json`: The production JSON containing all game levels.
- `generator.py`: Python 3 script responsible for procedural generation and structural validation.
- `.gitignore`: Standard ignore file for Python and IDE artifacts.
- `README.md`: This documentation.

---

## 🐻 Game Rules & Business Logic

- **Animal Species (Colors)**:
  - `brown` (Brown Bear)
  - `white` (Polar Bear)
  - `blue` (Blue Koala)
  - `yellow` (Honey Bear)
  - `pink` (Pink Panda)
- **Bus Capacities**: `4` (Van), `6` (Standard Bus), `8` (Articulated Bus).
- **Parking Directions**: `UP`, `DOWN`, `LEFT`, `RIGHT`.
- **Special Mechanics**:
  - `mystery_indices`: List of passenger queue indices that display a `?` icon and only reveal their color once they reach the front position.
  - `locked_buses`: Buses that start locked (`"unlock_after": N`), requiring N other buses to leave the parking lot before unlocking.
- **Dock Slots**: Default standard of `4` slots.

---

## ⚙️ Python Generator Usage

The generator has **zero external dependencies** (uses only Python standard library: `json`, `random`, `copy`, `sys`, `os`).

### Generate Levels
By default, running the script generates 100 levels:
```bash
python generator.py 100
```
You can specify any target level count:
```bash
python generator.py 250
```

---

## 🎮 Godot 4 Integration (Client Side)

To load levels dynamically in your Godot 4 game via GitHub Raw:

```gdscript
extends Node

const LEVELS_URL = "https://raw.githubusercontent.com/rodrigodeag/petbusjam-data/main/levels.json"

@onready var http_request: HTTPRequest = $HTTPRequest

func _ready() -> void:
    http_request.request_completed.connect(_on_request_completed)
    http_request.request(LEVELS_URL)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if response_code == 200:
        var json = JSON.new()
        var error = json.parse(body.get_string_from_utf8())
        if error == OK:
            var level_data = json.get_data()
            print("Loaded %d levels successfully!" % level_data.get("total_levels", 0))
            # Process levels here
        else:
            print("JSON Parse Error: ", json.get_error_message())
    else:
        print("Failed to download levels. HTTP Code: ", response_code)
```

---

## 🚀 Git & Deployment Workflow

Whenever you generate new levels or update the generator rules:
1. Run `python generator.py 150` (or your desired amount).
2. Commit and push the changes:
   ```bash
   git add .
   git commit -m "feat: update levels.json with new generated stages"
   git push origin main
   ```
3. Your Godot game will instantly have access to the updated levels via the raw URL!

