from typing import Callable


def input_validator(func: Callable[..., None]) -> Callable[..., None]:
    """
    Декоратор для обработки вводных данных и их валидации.

    Args:
        func (Callable[..., None]): Декорируемая функция.

    Returns:
        Callable[..., None]: Декорированная функция.
    """

    def wrapper() -> None:
        def validate_score(score: tuple[int, int]) -> None:
            """
            Функция для валидации вводимых данных.

            Args:
                score (tuple[int, int]): Счет матча.

            Raises:
                ValueError: Поднимается исключение, если формат счета неверный, числа отрицательные, числа превышают 5.
            """

            if any(x < 0 for x in score):
                raise ValueError('Неверный формат счета. Числа не могут быть отрицательными.')
            if not all(0 <= x <= 5 for x in score):
                raise ValueError('Неверный формат счета. Числа должны быть от 0 до 5.')

        while True:
            try:
                first_score = input('Введите счет первого матча (в формате G1:G2): ').strip()
                goals1, goals2 = map(int, first_score.split(':'))
                validate_score((goals1, goals2))

                second_score = input('Введите счет текущего матча (в формате G1:G2): ').strip()
                curr_goals1, curr_goals2 = map(int, second_score.split(':'))
                validate_score((curr_goals1, curr_goals2))

                location = input(
                    'Введите место проведения текущего матча (1 - домашний матч, 2 - гостевой матч): '
                ).strip()
                if location not in ['1', '2']:
                    raise ValueError('Неверный формат места проведения матча. Введите 1 или 2.')

                break

            except ValueError as e:
                print('Ошибка ввода:', e)

        return func(first_score, second_score, location)

    return wrapper


@input_validator
def winning_goals(first_score: str, second_score: str, location: str) -> int:
    """
    Вычисляет минимальное количество голов, которое нужно забить, чтобы победить без дополнительного времени.

    Args:
        first_score (str): Счет первого матча в формате "G1:G2", где G1 - количество голов, забитых первой командой,
        G2 - количество голов, забитых второй командой.
        second_score (str): Счет текущего матча в аналогичном формате "G1:G2".
        location (str): Место проведения текущего матча. Принимает значение '1', если первую игру прервая команда
        провела домашний матч, и '2', если гостевой матч.

    Returns:
        int: Минимальное количество голов, которое нужно забить первой команде.

    Raises:
        ValueError: поднимается исключение за счёт декоратора input_handler.
    """

    goals1, goals2 = map(int, first_score.split(':'))
    curr_goals1, curr_goals2 = map(int, second_score.split(':'))

    total_goals_team1 = goals1 + curr_goals1
    total_goals_team2 = goals2 + curr_goals2

    goals_to_score = (total_goals_team2 - total_goals_team1 + 1) if location == '2' else \
        (total_goals_team2 - total_goals_team1)

    return max(goals_to_score, 1)
