from sympy import Symbol, Integer, Expr

class VirasoroGenerator:
    """Представление генератора L_n алгебры Вирасоро"""
    def __init__(self, index: int):
        self.index = index

    def __repr__(self):
        return f"L_{self.index}"

# Центральный заряд (константа алгебры)
c = Symbol('c')

def bracket(A: VirasoroGenerator, B: VirasoroGenerator):
    """
    Вычисляет коммутатор [L_n, L_m] по формуле Вирасоро:
    [L_n, L_m] = (n - m)*L_{n+m} + (c/12) * n * (n^2 - 1) * delta_{n+m, 0}
    Возвращает словарь, где ключи - генераторы или константы, а значения - коэффициенты.
    """
    n = A.index
    m = B.index
    
    result = {}
    
    # Первая (классическая) часть: (n - m) * L_{n+m}
    if n != m:
        result[VirasoroGenerator(n + m)] = n - m
        
    # Вторая (квантовая/центральная) часть, работает только если n + m == 0
    if n + m == 0 and n != 0:
        # (c / 12) * n * (n^2 - 1)
        central_term = (c / 12) * n * (n**2 - 1)
        result['central'] = central_term
        
    return result

# --- ПРОВЕРКА МАСШТАБА НА ПК ---
# Давай посчитаем коммутатор [L_2, L_-2]
L2 = VirasoroGenerator(2)
L_2 = VirasoroGenerator(-2)

res = bracket(L2, L_2)
print("Результат коммутации [L_2, L_-2]:")
for key, coeff in res.items():
    print(f"  Коэффициент: {coeff} при элементе: {key}")
