import pytest
from pathlib import Path
from ..attendance import (
    Player,
    PlayerDatabase,
    AttendanceAnalyzer,
    AttendancePrinter,
    Attendance,
    Constants,
    BonusBase,
    GradeBase,
)


class DummyBonusBase(BonusBase):
    def apply(self, player):
        player.points += 5


class DummyGradeBase(GradeBase):
    def assign(self, player):
        player.grade = "Dummy"


def test_player_attendance_behavior():
    player = Player("Alice")
    player.attend(Constants.WEDNESDAY_INDEX, 3)
    player.attend(5, 2)
    player.attend(6, 2)
    assert player.points == 7
    assert player.week_counts[Constants.WEDNESDAY_INDEX] == 1
    assert player.has_wednesday_attendance()
    assert player.has_weekend_attendance()
    assert player.sum_weekend() == 2


def test_player_removal_condition():
    player = Player("Bob")
    assert player.is_removed()


def test_player_database_register_and_attendance():
    db = PlayerDatabase()
    db.process_attendance("Charlie", "monday")
    db.process_attendance("Charlie", "sunday")
    players = db.get_all_players()
    assert len(players) == 1
    assert players[0].points == 3
    assert players[0].name == "Charlie"


def test_attendance_analyzer_with_default_strategies():
    db = PlayerDatabase()
    for _ in range(10):
        db.process_attendance("Dana", "wednesday")
        db.process_attendance("Dana", "saturday")
    analyzer = AttendanceAnalyzer()
    players = db.get_all_players()
    analyzer.apply_bonus_points(players)
    analyzer.assign_grades(players)
    assert players[0].points >= 50
    assert players[0].grade == "Gold"


def test_attendance_analyzer_with_custom_strategies():
    db = PlayerDatabase()
    db.process_attendance("Eve", "friday")
    players = db.get_all_players()
    analyzer = AttendanceAnalyzer(
        bonus_Base=DummyBonusBase(),
        grade_Base=DummyGradeBase()
    )
    analyzer.apply_bonus_points(players)
    analyzer.assign_grades(players)
    assert players[0].points == 6
    assert players[0].grade == "Dummy"


def test_attendance_printer_outputs(capsys):
    db = PlayerDatabase()
    db.process_attendance("Frank", "monday")
    players = db.get_all_players()
    printer = AttendancePrinter()
    printer.print_results(players)
    printer.print_removed_players(players)
    captured = capsys.readouterr()
    assert "Frank" in captured.out
    assert "Removed player" in captured.out


def test_attendance_load_file_file_not_found(capsys):
    att = Attendance()
    result = att.load_file("non_existent_file.txt")
    captured = capsys.readouterr()
    assert not result
    assert "파일을 찾을 수 없습니다." in captured.out


def test_attendance_run_full(tmp_path: Path, capsys):
    file_content = "\n".join([
        "Grace wednesday"] * 10 + ["Grace saturday"] * 10 + ["John monday"]
    )
    file_path = tmp_path / "input.txt"
    file_path.write_text(file_content, encoding='utf-8')

    att = Attendance()
    att.run(str(file_path))
    captured = capsys.readouterr()

    assert "Grace" in captured.out
    assert "GOLD" in captured.out
    assert "John" in captured.out
    assert "Removed player" in captured.out


def test_attendance_run_skips_on_file_not_found(mocker, capsys):
    attendance = Attendance()
    mocker.patch.object(attendance, 'load_file', return_value=False)
    attendance.run("non_existent_file.txt")
    captured = capsys.readouterr()

    assert "" in captured.out
