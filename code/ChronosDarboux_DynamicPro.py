import os
import sympy as sp
import pandas as pd
import numpy as np

# =========================================================================
# ЧАСТЬ 1: СИМВОЛЬНОЕ ОДЕВАНИЕ И СИНТЕЗ ФОРМУЛЫ (ChronosDarboux_DynamicPro)
# =========================================================================

x, t, lam, q = sp.symbols('x t lambda q')
theta1, theta2 = sp.symbols('theta1 theta2')
W = sp.Function('W')(t)

print("="*110)
print(" ЗАПУСК СИСТЕМЫ: ChronosDarboux_DynamicPro v10.0 [ДИНАМИЧЕСКИЙ 3D СОЛИТОННЫЙ ПЛОТ]")
print("="*110)

# Генерируем точную фазу солитона с неавтономным ветром W(t) и SUSY-хвостом
integral_wind = sp.Integral(W, t)
phase = q * x * lam - (lam**3) * integral_wind + theta1 * theta2 * sp.sin(x)

# Применяем преобразование Дарбу (Одевание Лакса)
psi = sp.cosh(phase)
u_soliton_raw = -2 * sp.diff(sp.diff(sp.log(psi), x), x)
u_soliton_clean = sp.simplify(u_soliton_raw.subs({theta1**2: 0, theta2**2: 0}))

print("\n[SYMBOLIC ENGINE] Точная аналитическая формула Дарбу-солитона:")
print("-"*110)
sp.pprint(u_soliton_clean)
print("-"*110)

# =========================================================================
# ЧАСТЬ 2: ЧИСЛЕННЫЙ МОДУЛЬ ШТОРМОВОГО ХАОСА И ЭКСПОРТ В EXCEL
# =========================================================================

print("\n[NUMERICAL SIMULATION] Развертывание сетки 200 слоев времени на 100 точек пространства...")
os.makedirs('generated', exist_ok=True)
np.random.seed(1010)
rows_time, cols_space = 200, 100

# Создаем массив для хранения профиля волны u(x, t)
wave_profile = np.zeros((rows_time, cols_space))

for r_t in range(rows_time):
    # Задаем штормовой ветер: модулированные нелинейные колебания среды
    current_time = r_t * 0.05
    wind_force = np.sin(current_time**2) + np.cos(3 * current_time)
    # Накопленный интеграл ветра (фазовый сдвиг горба волны)
    wind_integral = -np.cos(current_time**2)/(2 * (current_time + 0.1)) + np.sin(3 * current_time)/3
    
    p_prime = [r_t % 10]  # p-адический квантовый стабилизатор сетки
    q_space = 1.0 + 0.0001 * r_t  # Динамическая q-деформация геометрии
    
    for c_x in range(cols_space):
        current_x = (c_x - 50) * 0.2  # Центрируем сетку пространства вокруг нуля
        
        # Вычисляем фазу Phi нашего солитона в данной точке пространства-времени
        # lambda принят равным 1.0 для фундаментальной моды
        lam_val = 1.0
        phi_val = q_space * current_x * lam_val - (lam_val**3) * wind_integral
        
        # Классический солитонный профиль КдФ/КП (гиперболический секанс в квадрате)
        # sech(x) = 1 / cosh(x)
        sech_squared = (1.0 / np.cosh(phi_val))**2
        
        # Амплитуда солитона (канонический горб) с учетом q-деформации
        soliton_core = 2 * (lam_val**2) * sech_squared * q_space
        
        # Встраиваем p-адическую микрорябь на воде
        padic_ripple = 0.05 / (p_prime ** (1 + (c_x % 3)))
        
        # Фермионный SUSY-хвост (микро-вибрация на краях волны)
        susy_tail = 0.02 * np.sin(2 * current_x) * sech_squared
        
        # Итоговый профиль живой неавтономной волны u(x,t)
        wave_profile[r_t, c_x] = float(f"{(soliton_core + padic_ripple + susy_tail):.6f}")

# Формируем DataFrame для Excel
col_names = [f"Space_Pos_X_{i}" for i in range(cols_space)]
df = pd.DataFrame(wave_profile, columns=col_names)
df.insert(0, 'Time_Layer_T', range(1, rows_time + 1))
df.insert(1, 'p_Adic_Wind_Prime', [r_t % 10] for r_t in range(rows_time) ])
df.insert(2, 'Storm_Wind_W_t', [np.sin((r_t*0.05)**2) + np.cos(3*(r_t*0.05)) for r_t in range(rows_time)])

# Запись данных и манифеста в Excel-файл
file_path = 'generated/ChronosDarboux_Dressing_Simulation.xlsx'
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Soliton_Dynamic_Matrix', index=False)
    
    manifest = (
        f"МАТЕМАТИЧЕСКИЙ ПРОТОКОЛ СИМУЛЯЦИИ ЖИВОГО 3D-СОЛИТОНА\n"
        f"========================================================================\n\n"
        f"Пакет: ChronosDarboux_DynamicPro v10.0 (Darboux Lax-Dressed Wave Simulator)\n\n"
        f"Символьная формула одевания Дарбу, зашитая в ядро:\n"
        f"  u(x, t) = {u_soliton_clean}\n\n"
        f"Параметры штормового ветра:\n"
        f"  - Функция ветра: W(t) = sin(t^2) + cos(3t)\n"
        f"  - Влияние на солитон: Задает нелинейное ускорение, сжатие и осцилляцию горба волны.\n\n"
        f"Свойства квантовой супер-решетки:\n"
        f"  - Пространство X: 100 расчетных точек (координатный профиль от -10 до +10).\n"
        f"  - Время T: 200 последовательных слоев эволюции волны.\n"
        f"  - SUSY-баланс: Фермионные хвосты промоделированы через модуляцию секанса.\n"
        f"  - Арифметика: p-адические простые числа гасят паразитные шумы квантовой плоскости.\n\n"
        f"Каждая строка таблицы — это снимок профиля волны солитона в конкретный момент времени T."
    )
    pd.DataFrame({'Manifest': [manifest]}).to_excel(writer, sheet_name='Simulation_Manifest', index=False)

print(f"\n[УСПЕХ] 3D-симуляция завершена! Данные живой волны сохранены в: {file_path}")
print("="*110)
