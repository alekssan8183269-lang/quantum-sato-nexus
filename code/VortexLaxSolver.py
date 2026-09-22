import sympy as sp
from typing import Dict

# 1. Инициализация символьного пространства
x = sp.Symbol('x')
t = sp.Symbol('t')
lam = sp.Symbol('lambda')  # Спектральный параметр (основа ряда Лорана)

# Динамические функции: u(x,t) - поле волны, W(t) - наш "ветер" (внешнее поле)
u = sp.Function('u')(x, t)
W = sp.Function('W')(t)

class VortexLaxSolver:
    """
    Пакет для генерации неавтономных солитонных уравнений на основе алгебры sl2_hat.
    Элементы представляют собой ряды Лорана по спектральному параметру lambda,
    где коэффициентами являются матрицы 2x2 (элементы классической алгебры sl2).
    """
    def __init__(self, data: Dict[int, sp.Matrix] = None):
        # Структура данных: { степень_lambda: Матрица_2x2_из_SymPy_выражений }
        self.series = {}
        if data:
            for power, matrix in data.items():
                simp_matrix = sp.simplify(matrix)
                if not simp_matrix.is_zero_matrix:
                    self.series[power] = simp_matrix

    def __add__(self, other):
        all_powers = set(self.series.keys()).union(set(other.series.keys()))
        res_data = {}
        for p in all_powers:
            m1 = self.series.get(p, sp.zeros(2, 2))
            m2 = other.series.get(p, sp.zeros(2, 2))
            res_data[p] = m1 + m2
        return VortexLaxSolver(res_data)

    def __sub__(self, other):
        all_powers = set(self.series.keys()).union(set(other.series.keys()))
        res_data = {}
        for p in all_powers:
            m1 = self.series.get(p, sp.zeros(2, 2))
            m2 = other.series.get(p, sp.zeros(2, 2))
            res_data[p] = m1 - m2
        return VortexLaxSolver(res_data)

    def __mul__(self, coeff):
        res_data = {p: m * coeff for p, m in self.series.items()}
        return VortexLaxSolver(res_data)

    def __rmul__(self, coeff):
        return self.__mul__(coeff)

    def diff_t(self):
        """Дифференцирование всего ряда по времени t"""
        res_data = {}
        for p, m in self.series.items():
            res_data[p] = m.diff(t)
        return VortexLaxSolver(res_data)

    def diff_x(self):
        """Дифференцирование всего ряда по пространству x"""
        res_data = {}
        for p, m in self.series.items():
            res_data[p] = m.diff(x)
        return VortexLaxSolver(res_data)

    @staticmethod
    def commutator(A, B):
        """Вычисление матричного коммутатора [A, B] = A*B - B*A для двух рядов Лорана"""
        res_data = {}
        # Перемножаем элементы рядов: lambda^p1 * lambda^p2 = lambda^(p1+p2)
        for p1, m1 in A.series.items():
            for p2, m2 in B.series.items():
                p_new = p1 + p2
                comm_matrix = m1 * m2 - m2 * m1
                if p_new in res_data:
                    res_data[p_new] += comm_matrix
                else:
                    res_data[p_new] = comm_matrix
        return VortexLaxSolver(res_data)

    def get_explicit_series(self, max_power=2, min_power=-2):
        """Возвращает красивое аналитическое представление ряда для вывода"""
        expr = sp.zeros(2, 2)
        for p in sorted(self.series.keys()):
            if min_power <= p <= max_power:
                expr += self.series[p] * (lam**p)
        return expr

# --- БАЗИС КЛАССИЧЕСКОЙ АЛГЕБРЫ sl2 (Матрицы Паули и сдвига) ---
e = sp.Matrix([[0, 1], [0, 0]])
f = sp.Matrix([[0, 0], [1, 0]])
h = sp.Matrix([[1, 0], [0, -1]])

print("="*80)
print(" СИСТЕМНЫЙ ЗАПУСК ПАКЕТА: VortexLaxSolver v1.0")
print("="*80)

# Шаг 1: Конструируем оператор L (Пространственная часть пары Лакса для КдФ)
# Традиционный анзац КдФ: L = f * lambda^1 + u * e * lambda^0
# Мы добавляем сюда "вибрацию" спектрального параметра через h-компоненту
L = VortexLaxSolver({
    1: f,
    0: u * e
})

# Шаг 2: Конструируем неавтономный оператор M (Временная часть с "ВЕТРОМ" W(t))
# Мы берем классическую структуру КдФ, но домножаем высший член на W(t)
u_x = sp.diff(u, x)
u_xx = sp.diff(u, x, 2)

M = VortexLaxSolver({
    1: W * f + u * e,
    0: (sp.Rational(1, 2) * u_x) * h,
    -1: (sp.Rational(1, 4) * u_xx + sp.Rational(1, 2) * u**2) * e
})

print("\n[РЯДЫ] Исходный оператор L (в базисе sl2_hat):")
sp.pprint(L.get_explicit_series())

print("\n[РЯДЫ] Модифицированный 'ветром' W(t) оператор M:")
sp.pprint(M.get_explicit_series())

# Шаг 3: Генерация неавтономного уравнения через уравнение нулевой кривизны (Пара Лaxca)
# Формула: dL/dt - dM/dx + [L, M] = 0
dL_dt = L.diff_t()
dM_dx = M.diff_x()
comm_LM = VortexLaxSolver.commutator(L, M)

# Финальное уравнение совместности
Lax_Equation = dL_dt - dM_dx + comm_LM

print("\n" + "="*80)
print(" ГЕНЕРАЦИЯ НОВОГО УРАВНЕНИЯ (Результат раскрытия коммутаторов на ПК)")
print("="*80)

# Вытаскиваем матрицу, которая получилась при lambda^0 (именно там сидит динамика u)
if 0 in Lax_Equation.series:
    final_matrix_eq = Lax_Equation.series[0]
    # Нас интересует правый верхний элемент матрицы (компонента при генераторе 'e')
    generated_formula = final_matrix_eq[0, 1]
    
    print("\n[ФОРМУЛА] Полученное дифференциальное уравнение для u(x,t):")
    print(f"  {sp.Symbol('u_t')} = {sp.simplify(sp.solve(generated_formula, sp.diff(u, t))[0])}")
else:
    print("[ОШИБКА] Ряд занулился, проверьте анзац операторов.")

print("\n" + "="*80)
print(" ПОЛНЫЙ МАТРИЧНЫЙ РЯД ОШИБКИ ЛАКСА (Должен быть равен нулю для интегрируемости):")
print("="*80)
for power in sorted(Lax_Equation.series.keys()):
    print(f"\nКоэффициент при lambda^{power}:")
    sp.pprint(Lax_Equation.series[power])
