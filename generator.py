#!/usr/bin/env python3
"""
PetBusJam Procedural Level Generator & Validator
Author: Senior Software Engineer (Automation & Puzzle Algorithms)
Description: Generates, validates, and updates lightweight levels.json for PetBusJam.
"""

import json
import random
import copy
import sys
import os

COLORS = ["brown", "white", "blue", "yellow", "pink"]
BUS_CAPACITIES = [4, 6, 8]
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
DOCK_SLOTS_DEFAULT = 4
LEVELS_FILE = "levels.json"

def get_difficulty_for_level(level_id):
    if level_id <= 20: return "easy"
    elif level_id <= 60: return "medium"
    elif level_id <= 100: return "hard"
    else: return "expert"

def generate_level(level_id):
    difficulty = get_difficulty_for_level(level_id)
    if difficulty == "easy":
        w, h, num_buses = 6, 6, random.randint(2, 4)
    elif difficulty == "medium":
        w, h, num_buses = 7, 7, random.randint(4, 6)
    elif difficulty == "hard":
        w, h, num_buses = 8, 8, random.randint(6, 8)
    else:
        w, h, num_buses = 9, 9, random.randint(8, 12)

    bus_colors = [random.choice(COLORS) for _ in range(num_buses)]
    passenger_queue = []
    buses = []
    occupied = set()

    for i in range(num_buses):
        bus_id = i + 1
        color = bus_colors[i]
        capacity = random.choice(BUS_CAPACITIES)
        for _ in range(capacity):
            passenger_queue.append(color)

        dir_choice = random.choice(DIRECTIONS)
        placed, attempts = False, 0
        while not placed and attempts < 50:
            attempts += 1
            if dir_choice == "UP": x, y = random.randint(0, w - 1), 0
            elif dir_choice == "DOWN": x, y = random.randint(0, w - 1), h - 1
            elif dir_choice == "LEFT": x, y = 0, random.randint(0, h - 1)
            else: x, y = w - 1, random.randint(0, h - 1)
            if (x, y) not in occupied:
                occupied.add((x, y))
                placed = True
        if not placed:
            x, y = 0, i % h
            occupied.add((x, y))

        unlock_after = 0
        if difficulty in ["hard", "expert"] and i >= 2 and random.random() < 0.4:
            unlock_after = random.randint(1, min(3, i))

        buses.append({
            "id": bus_id, "color": color, "capacity": capacity,
            "x": x, "y": y, "dir": dir_choice, "unlock_after": unlock_after
        })

    random.shuffle(passenger_queue)
    mystery_indices = []
    if difficulty in ["medium", "hard", "expert"]:
        num_mystery = random.randint(1, max(1, len(passenger_queue) // 6))
        mystery_indices = sorted(random.sample(range(len(passenger_queue)), num_mystery))

    return {
        "id": level_id, "difficulty": difficulty, "grid_size": [w, h],
        "dock_slots": DOCK_SLOTS_DEFAULT, "passenger_queue": passenger_queue,
        "mystery_indices": mystery_indices, "buses": buses
    }


def validate_level(level):
    required_keys = ["id", "difficulty", "grid_size", "dock_slots", "passenger_queue", "mystery_indices", "buses"]
    for key in required_keys:
        if key not in level:
            raise ValueError(f"Level {level.get('id')} missing {key}")
    return True

def generate_levels_file(target_total=100, output_path=LEVELS_FILE):
    levels = [generate_level(i) for i in range(1, target_total + 1)]
    for lvl in levels:
        validate_level(lvl)
    data = {"version": 1, "total_levels": target_total, "levels": levels}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated {target_total} levels successfully into {output_path}")

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_levels_file(target)
