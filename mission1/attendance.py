MAX_PLAYERS = 100
DAYS_IN_WEEK = 7
BONUS_THRESHOLD = 10
BONUS_SCORE = 10
WEEKEND_DAYS = [5, 6]
WEDNESDAY_INDEX = 2
GRADE_POLICY = {
    "Gold": 50,
    "Silver": 30,
    "Normal": 0
}
GRADE_LABELS = {
    "Gold": "GOLD",
    "Silver": "SILVER",
    "Normal": "NORMAL"
}
DAY_INFO = {
    "monday": (0, 1),
    "tuesday": (1, 1),
    "wednesday": (2, 3),
    "thursday": (3, 1),
    "friday": (4, 1),
    "saturday": (5, 2),
    "sunday": (6, 2)
}

player_name_to_index = {}
player_count = 0
player_names = [''] * MAX_PLAYERS
week_counts = [[0] * DAYS_IN_WEEK for _ in range(MAX_PLAYERS)]
points = [0] * MAX_PLAYERS
grades = [''] * MAX_PLAYERS


def get_day_index_and_points(weekday):
    return DAY_INFO.get(weekday.lower(), (0, 0))

def process_attendance(player_name, weekday):
    global player_count

    if player_name not in player_name_to_index:
        player_count += 1
        player_name_to_index[player_name] = player_count
        player_names[player_count] = player_name

    player_index = player_name_to_index[player_name]
    day_index, base_point = get_day_index_and_points(weekday)
    week_counts[player_index][day_index] += 1
    points[player_index] += base_point

def process_bonus_points():
    for player_index in range(1, player_count + 1):
        if week_counts[player_index][WEDNESDAY_INDEX] >= BONUS_THRESHOLD:
            points[player_index] += BONUS_SCORE
        if sum(week_counts[player_index][d] for d in WEEKEND_DAYS) >= BONUS_THRESHOLD:
            points[player_index] += BONUS_SCORE

def process_assign_grades():
    for player_index in range(1, player_count + 1):
        for grade_name, threshold in GRADE_POLICY.items():
            if points[player_index] >= threshold:
                grades[player_index] = grade_name
                break

def print_results():
    for player_index in range(1, player_count + 1):
        grade_str = GRADE_LABELS.get(grades[player_index], grades[player_index].upper())
        print(f"NAME : {player_names[player_index]}, POINT : {points[player_index]}, GRADE : {grade_str}")

def check_removed_player(player_index):
    is_normal = grades[player_index] == "Normal"
    has_wednesday = week_counts[player_index][WEDNESDAY_INDEX] > 0
    has_weekend = sum(week_counts[player_index][d] for d in WEEKEND_DAYS) > 0
    return is_normal and not has_wednesday and not has_weekend

def print_removed_player():
    print("\nRemoved player")
    print("==============")
    for player_index in range(1, player_count + 1):
        if check_removed_player(player_index):
            print(player_names[player_index])

def load_attendance_file(filename):
    try:
        with open(filename, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    process_attendance(parts[0], parts[1])
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
        return False
    return True

def main():
    if load_attendance_file("attendance_weekday_500.txt"):
        process_bonus_points()
        process_assign_grades()
        print_results()
        print_removed_player()


if __name__ == "__main__":
    main()
