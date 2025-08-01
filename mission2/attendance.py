from abc import ABC, abstractmethod


class Constants:
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


class Player:
    def __init__(self, name):
        self.name = name
        self.week_counts = [0] * Constants.DAYS_IN_WEEK
        self.points = 0
        self.grade = "Normal"

    def attend(self, day_index, base_point):
        self.week_counts[day_index] += 1
        self.points += base_point

    def has_wednesday_attendance(self):
        return self.week_counts[Constants.WEDNESDAY_INDEX] > 0

    def has_weekend_attendance(self):
        for day in Constants.WEEKEND_DAYS:
            if self.week_counts[day] > 0:
                return True
        return False

    def sum_weekend(self):
        total = 0
        for day in Constants.WEEKEND_DAYS:
            total += self.week_counts[day]
        return total

    def is_removed(self):
        return (
            self.grade == "Normal"
            and not self.has_wednesday_attendance()
            and not self.has_weekend_attendance()
        )


class PlayerDatabase:
    def __init__(self):
        self.players = {}
        self.player_order = []

    def get_or_create_player(self, name):
        if name not in self.players:
            self.players[name] = Player(name)
            self.player_order.append(name)
        return self.players[name]

    def process_attendance(self, name, weekday):
        player = self.get_or_create_player(name)
        day_index, base_point = Constants.DAY_INFO.get(weekday.lower(), (0, 0))
        player.attend(day_index, base_point)

    def get_all_players(self):
        return [self.players[name] for name in self.player_order]

class BonusBase(ABC):
    @abstractmethod
    def apply(self, player: Player):
        pass

class GradeBase(ABC):
    @abstractmethod
    def assign(self, player: Player):
        pass

class DefaultBonusBase(BonusBase):
    def apply(self, player: Player):
        if player.week_counts[Constants.WEDNESDAY_INDEX] >= Constants.BONUS_THRESHOLD:
            player.points += Constants.BONUS_SCORE
        if player.sum_weekend() >= Constants.BONUS_THRESHOLD:
            player.points += Constants.BONUS_SCORE

class DefaultGradeBase(GradeBase):
    def assign(self, player: Player):
        for grade_name, threshold in Constants.GRADE_POLICY.items():
            if player.points >= threshold:
                player.grade = grade_name
                break

class AttendanceAnalyzer:
    def __init__(self, bonus_Base=None, grade_Base=None):
        self.bonus_Base = bonus_Base or DefaultBonusBase()
        self.grade_Base = grade_Base or DefaultGradeBase()

    def apply_bonus_points(self, players):
        for player in players:
            self.bonus_Base.apply(player)

    def assign_grades(self, players):
        for player in players:
            self.grade_Base.assign(player)


class AttendancePrinter:
    def print_results(self, players):
        for player in players:
            grade_str = Constants.GRADE_LABELS.get(player.grade, player.grade.upper())
            print(f"NAME : {player.name}, POINT : {player.points}, GRADE : {grade_str}")

    def print_removed_players(self, players):
        print("\nRemoved player")
        print("==============")
        for player in players:
            if player.is_removed():
                print(player.name)


class Attendance:
    def __init__(self):
        self.database = PlayerDatabase()
        self.analyzer = AttendanceAnalyzer()
        self.printer = AttendancePrinter()

    def load_file(self, filename):
        try:
            with open(filename, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        self.database.process_attendance(parts[0], parts[1])
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다.")
            return False
        return True

    def run(self, filename="attendance_weekday_500.txt"):
        if not self.load_file(filename):
            return
        players = self.database.get_all_players()
        self.analyzer.apply_bonus_points(players)
        self.analyzer.assign_grades(players)
        self.printer.print_results(players)
        self.printer.print_removed_players(players)


if __name__ == "__main__":
    attendance = Attendance()
    attendance.run()
