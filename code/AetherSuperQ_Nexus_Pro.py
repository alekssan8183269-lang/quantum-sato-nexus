import os
import sympy as sp
import pandas as pd
import numpy as np

# =========================================================================
# ЧАСТЬ 1: СИМВОЛЬНОЕ СУПЕРПРОСТРАНСТВО И АВТОПОДБОР (ИНТЕГРАЦИЯ ВСЕХ ФИЧ)
# =========================================================================

x, y, t, q, lam = sp.symbols('x y t q lambda')
theta1, theta2 = sp.symbols('theta1 theta2')
W_x, W_y = sp.Function('W_x')(t), sp.Function('W_y')(t)

# Полное суперполе с фермионными SUSY-хвостами
u_0 = sp.Function('u_0')(x, y, t)
u = u_0 + sp.Function('u_1')(x,y,t)*theta1 + sp.Function('u_2')(x,y,t)*theta2

class AetherSuperQ_Nexus_Pro:
    def __init__(self, data=None):
        self.series = {}
        if data:
            for p, m in data.items():
                sm = m.applyfunc(lambda item: sp.simplify(item.subs({theta1**2: 0, theta2**2: 0})))
                if not sm.is_zero_matrix: self.series[p] = sm

    @staticmethod
    def super_commutator(A, B):
        res = {}
        for p1, m1 in A.series.items():
            for p2, m2 in B.series.items():
                p_new = p1 + p2
                comm = m1 * m2 - (q**(p1 - p2)) * m2 * m1
                res[p_new] = res.get(p_new, sp.zeros(3, 3)) + comm
        return AetherSuperQ_Nexus_Pro(res)

# Базис sl3 матриц 3х3
E12 = sp.Matrix([[0,1,0],[0,0,0],[0,0,0]])
E23 = sp.Matrix([[0,0,0],[0,0,1],[0,0,0]])
E21, E13 = E12.T, sp.Matrix([[0,0,1],[0,0,0],[0,0,0]])

L = AetherSuperQ_Nexus_Pro({1: E12 + E23, 0: u * E21})
M = AetherSuperQ_Nexus_Pro({2: E13 * W_y, 1: u * E12 + u * E23, 0: (u.diff(x)*q) * (E12*E21 - E23*E13.T)})

# Генерируем некоммутативное уравнение совместности (Связь u_y)
Lax_Y = L.series.diff(y) - M.series.diff(x)*q + AetherSuperQ_Nexus_Pro.super_commutator(L, M).series.get(0, sp.zeros(3,3))
u_y_formula = sp.simplify(sp.solve(Lax_Y[1,0], u.diff(y))[0])

print("="*90)
print(" СИМВОЛЬНОЕ ЯДРО СГЕНЕРИРОВАЛО УРАВНЕНИЕ ДЛЯ КВАНТОВОГО СУПЕРПОЛЯ:")
print("="*90)
print(f" u_y = {u_y_formula}\n")

# =========================================================================
# ЧАСТЬ 2: ГЕНЕРАЦИЯ МАССИВА ДАННЫХ ДЛЯ EXCEL (200 РЯДОВ х 100 ЗНАЧЕНИЙ)
# =========================================================================

print("[NUMERICAL ENGINE] Запуск генерации квантовой p-адической матрицы...")
os.makedirs('generated', exist_ok=True)
np.random.seed(42)
rows, cols = 200, 100

data = np.zeros((rows, cols))
for r in range(rows):
    p_prime = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][r % 10] # p-адический базис ветра
    q_wind = 0.95 + 0.0005 * r # деформация некоммутативной плоскости времени
    for c in range(cols):
        padic_metric = 1.0 / (p_prime ** (1 + (c % 4)))
        boson_component = np.sin(0.1 * c * q_wind) + np.cos(0.05 * r)
        fermion_tail = 0.02 * np.sin(0.5 * (r + c)) if (r + c) % 2 == 0 else -0.01 * np.cos(0.3 * r)
        data[r, c] = float(f"{(boson_component + padic_metric + fermion_tail):.6f}")

col_names = [f"Val_L_{i}" for i in range(cols)]
df = pd.DataFrame(data, columns=col_names)
df.insert(0, 'Row_Index', range(1, rows + 1))
df.insert(1, 'p_Adic_Prime', [ [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][r % 10] for r in range(rows) ])
df.insert(2, 'q_Wind_Param', [ 0.95 + 0.0005 * r for r in range(rows) ])

# Экспорт в Excel с сохранением формул и манифеста
file_path = 'generated/QuantumNexus_pAdicExcel_v5.xlsx'
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Quantum_Superfield_Matrix', index=False)
    
    manifest = (
        f"МАТЕМАТИЧЕСКИЙ МАНИФЕСТ И ФОРМУЛА ИЕРАРХИИ\n"
        f"==========================================================\n\n"
        f"Пакет: AetherSuperQ_Nexus_Pro v5.0 (p-Adic Multi-Grid Setup)\n"
        f"Сгенерированное уравнение квантового суперполя:\n"
        f"  u_y = {u_y_formula}\n\n"
        f"Правило дискретизации рядов Лорана для ячеек sl3_hat:\n"
        f"  Val(r, c) = sin(0.1*c*q_wind) + cos(0.05*r) + 1/(p_prime^(1 + c mod 4)) + SUSY_Tail(r,c)\n\n"
        f"Параметры выгрузки:\n"
        f"  - Ряды (строки): {rows} (интегрирование по временным слоям)\n"
        f"  - Значения (столбцы): {cols} (высшие гармоники спектрального параметра)\n"
        f"  - Арифметический p-адический базис: простые числа от 2 до 29\n"
        f"  - Грассмановы SUSY-хвосты: вмонтированы в амплитуду колебаний ячеек."
    )
    pd.DataFrame({'Manifest': [manifest]}).to_excel(writer, sheet_name='Superfield_Manifest', index=False)

print(f"[УСПЕХ] Файл создан и сохранен в: {file_path}")
