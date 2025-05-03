import numpy as np
from scipy.optimize import linear_sum_assignment

def assignment_max(A):
    """
    Находит перестановку, максимизирующую сумму значений в матрице A,
    используя алгоритм Венгера для задачи максимизации.
    """
    M = A.max()
    cost = M - A
    row_ind, col_ind = linear_sum_assignment(cost)
    sigma = [-1] * len(A)
    for i, j in zip(row_ind, col_ind):
        sigma[i] = int(j)
    value = A[row_ind, col_ind].sum()
    return sigma, value

def build_conjugate_sigma(sigma, A):
    """
    Строит сопряжённую перестановку к sigma, исключая совпадения по парам (i, sigma[i]).
    """
    A_masked = A.copy()
    for i in range(len(sigma)):
        A_masked[i][sigma[i]] = -1e9  # Исключаем пары из sigma
    return assignment_max(A_masked)

def build_sigma1(sigma_star, gamma, A):
    """
    Строит дополнительную перестановку к sigma_star относительно маски gamma.
    gamma задаётся как целое число, представляющее битовую маску.
    В позициях, где gamma == 1, значения должны совпадать с sigma_star,
    а в остальных позициях — отличаться от sigma_star.
    """
    n = len(sigma_star)
    sigma1 = [-1] * n
    fixed_cols = set()
    banned_pairs = []

    for i in range(n):
        if (gamma >> i) & 1:
            sigma1[i] = sigma_star[i]
            fixed_cols.add(sigma_star[i])
        else:
            banned_pairs.append((i, sigma_star[i]))

    free_rows = [i for i in range(n) if sigma1[i] == -1]
    free_cols = [j for j in range(n) if j not in fixed_cols]

    if not free_rows:
        value = sum(A[i][sigma1[i]] for i in range(n))
        return sigma1, value

    submatrix = np.full((len(free_rows), len(free_cols)), -1e9)

    for ri, i in enumerate(free_rows):
        for ci, j in enumerate(free_cols):
            if (i, j) not in banned_pairs:
                submatrix[ri][ci] = A[i][j]

    M = submatrix.max()
    cost = M - submatrix
    row_ind, col_ind = linear_sum_assignment(cost)

    for ri, ci in zip(row_ind, col_ind):
        sigma1[free_rows[ri]] = int(free_cols[ci])

    value = sum(A[i][sigma1[i]] for i in range(n))
    return sigma1, value

def find_optimal_pair(A):
    """
    Основной алгоритм: поиск двух перестановок с максимальной суммой по описанному методу.
    """
    n = len(A)
    sigma_star, value_star = assignment_max(A)
    sigma0, value0 = build_conjugate_sigma(sigma_star, A)
    SMAX = value_star + value0
    best_pair = (sigma_star, sigma0)

    for gamma in range(1, 2 ** n - 1):  # от 000...001 до 111...110
        sigma1, value1 = build_sigma1(sigma_star, gamma, A)
        sigma2, value2 = build_conjugate_sigma(sigma1, A)
        total = value1 + value2
        if total > SMAX:
            SMAX = total
            best_pair = (sigma1, sigma2)

    return best_pair, SMAX

# Пример использования
if __name__ == "__main__":
    A = np.array([
        [5, 4, 2],
        [4, 5, 4],
        [2, 4, 5]
    ])

    (sigma1, sigma2), smax = find_optimal_pair(A)
    print("Оптимальные перестановки:")
    print("sigma1:", sigma1)
    print("sigma2:", sigma2)
    print("Максимальная сумма:", smax)
