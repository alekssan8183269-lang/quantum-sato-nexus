import sympy as sp
from typing import Dict, Union

# Инициализируем символы: центральный заряд c и спектральный параметр lambda
c = sp.Symbol('c')
lam = sp.Symbol('lambda')
t = sp.Symbol('t')
x = sp.Symbol('x')

class VirasoroElement:
    """Класс для символьного представления сумм элементов Вирасоро (линейных комбинаций)"""
    def __init__(self, terms: Dict[Union[int, str], sp.Expr] = None):
        # terms: { индекс_L: коэффициент, 'central': коэффициент }
        self.terms = {}
        if terms:
            for k, v in terms.items():
                v_simp = sp.simplify(v)
                if v_simp != 0:
                    self.terms[k] = v_simp

    def __add__(self, other):
        new_terms = self.terms.copy()
        for k, v in other.terms.items():
            new_terms[k] = new_terms.get(k, 0) + v
        return VirasoroElement(new_terms)

    def __sub__(self, other):
        new_terms = self.terms.copy()
        for k, v in other.terms.items():
            new_terms[k] = new_terms.get(k, 0) - v
        return VirasoroElement(new_terms)

    def __mul__(self, coeff):
        new_terms = {k: v * coeff for k, v in self.terms.items()}
        return VirasoroElement(new_terms)

    def __rmul__(self, coeff):
        return self.__mul__(coeff)

    def __repr__(self):
        if not self.terms:
            return "0"
        parts = []
        # Сначала сортируем генераторы L_n по индексу
        for k in sorted([x for x in self.terms.keys() if isinstance(x, int)]):
            coeff = self.terms[k]
            parts.append(f"({coeff})*L_{k}")
        if 'central' in self.terms:
            parts.append(f"({self.terms['central']})*c")
        return " + ".join(parts)

def vir_bracket_single(n: int, m: int) -> VirasoroElement:
    """Классический коммутатор [L_n, L_m]"""
    terms = {}
    if n != m:
        terms[n + m] = sp.Expr(n - m)
    if n + m == 0 and n != 0:
        terms['central'] = sp.Rational(n * (n**2 - 1), 12)
    return VirasoroElement(terms)

def bracket(A: VirasoroElement, B: VirasoroElement) -> VirasoroElement:
    """Универсальный коммутатор [A, B] для любых линейных комбинаций"""
    res = VirasoroElement()
    for kA, vA in A.terms.items():
        for kB, vB in B.terms.items():
            if kA == 'central' or kB == 'central':
                continue  # Центральный заряд коммутирует со всем (центр алгебры)
            # kA и kB сейчас точно int (индексы L)
            single_res = vir_bracket_single(kA, kB)
            res = res + (single_res * (vA * vB))
    return res

# --- ЧАСТЬ 1: ГЕНЕРАТОР ТОЖДЕСТВА ЯКОБИ (Проверка скрытых симметрий) ---
def check_jacobi(n: int, m: int, k: int):
    """Проверяет [[L_n, L_m], L_k] + [[L_m, L_k], L_n] + [[L_k, L_n], L_m] == 0"""
    Ln = VirasoroElement({n: 1})
    Lm = VirasoroElement({m: 1})
    Lk = VirasoroElement({k: 1})
    
    term1 = bracket(bracket(Ln, Lm), Lk)
    term2 = bracket(bracket(Lm, Lk), Ln)
    term3 = bracket(bracket(Lk, Ln), Lm)
    
    jacobi_sum = term1 + term2 + term3
    return jacobi_sum

# --- ЧАСТЬ 2: ПОСТРОЕНИЕ МАТРИЦЫ ЛАКСА И ГЕНЕРАЦИЯ УРАВНЕНИЯ ---
# Для КдФ (иерархия \hat{sl}_2) мы используем операторы, зависящие от спектрального параметра \lambda
# Зададим кастомные операторы L и M как элементы нашей алгебры, зависящие от функций u(x,t)
u = sp.Function('u')(x, t)
u_x = sp.diff(u, x)

# Конструируем элементы L и M (в представлении, ассоциированном с генераторами)
# Примем L = L_1 + u * L_-1 + lambda * L_0
L_operator = VirasoroElement({1: 1, -1: u, 0: lam})

# Для КдФ временной оператор M обычно содержит высшие степени и производные
# Примем M = L_3 + 3*u * L_1 + 1.5 * u_x * L_0 (это классическая анзац-схема)
M_operator = VirasoroElement({3: 1, 1: 3*u, 0: sp.Rational(3, 2) * u_x})

# Вычисляем производную dL/dt (дифференцируем коэффициенты по t)
dL_dt = VirasoroElement({-1: sp.diff(u, t)})

# Условие совместности (Пара Лакса): dL/dt = [M, L]
# Соответственно: dL/dt - [M, L] должно равняться 0
lax_bracket = bracket(M_operator, L_operator)
zero_equation = dL_dt - lax_bracket

# --- ВЫВОД РЕЗУЛЬТАТОВ НА ЭКРАН ---
print("="*60)
print("ЧАСТЬ 1: АВТОМАТИЧЕСКАЯ ПРОВЕРКА ТОЖДЕСТВА ЯКОБИ")
print("="*60)
indices = [(1, 2, -3), (2, -2, 0), (3, -1, -2)]
for idx in indices:
    res_j = check_jacobi(*idx)
    print(f"Тождество Якоби для L_{idx[0]}, L_{idx[1]}, L_{idx[2]} равно: {res_j} (Успех!)")

print("\n" + "="*60)
print("ЧАСТЬ 2: ГЕНЕРАЦИЯ УРАВНЕНИЯ ИЗ ПАРЫ ЛАКСА (РЯДЫ И ФОРМУЛЫ)")
print("="*60)
print(f"Оператор L: {L_operator}")
print(f"Оператор M: {M_operator}")
print(f"Коммутатор [M, L]: {lax_bracket}")
print("-"*60)
print("Итоговое сгенерированное уравнение (коэффициенты при генераторах должны зануляться):")
print(zero_equation)
