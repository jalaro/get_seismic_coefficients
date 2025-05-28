from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def compute_building_period(H, structure_type):
    if structure_type == "RC":
        return 0.07 * (H ** 0.75)
    elif structure_type == "Steel":
        return 0.085 * (H ** 0.75)
    else:
        return 0.05 * (H ** 0.75)

def interpolate(x1, y1, x2, y2, x):
    return y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)

def apply_formula_2_13d(x):
    if x <= 0.3:
        return x, "直接使用原值"
    elif x < 0.8:
        return 0.52 * x + 0.144, "修正為 0.52x + 0.144"
    else:
        return 0.7 * x, "修正為 0.7x"

def calculate_K(I, Sa, Fu, alpha_y):
    return I * (Sa / Fu) / (1.4 * alpha_y)

@app.route("/seismic_kx", methods=["POST"])
def seismic_kx():
    data = request.json

    # 基本輸入
    fault = data["fault_name"]
    r = data["distance_km"]
    location = data["location"]
    direction = data["direction"]
    R = data["R"]
    I = data["I"]
    alpha_y = data["alpha_y"]
    structure_type = data["structure_type"]
    H = data["H"]

    # 使用者未提供 T，則估算
    T = compute_building_period(H, structure_type)

    # 模擬表格查值（實際應查表）
    SSD = 0.55
    SD1D = 0.26
    SSM = 0.83
    SD1M = 0.52

    FaD = 1.0
    FvD = 1.0
    FaM = 1.0
    FvM = 1.0

    SDS = SSD * FaD
    SD1 = SD1D * FvD
    SMS = SSM * FaM
    SM1 = SD1M * FvM

    # Fu 值（公式簡化處理）
    FuD = R * (0.4 + 0.6 * T)
    FuM = R * (0.4 + 0.6 * T)

    # 計算 K 值
    K_min = 0.044
    K_moderate = calculate_K(I, SDS, FuD, alpha_y)

    x = FuM * SMS
    x_m, rule = apply_formula_2_13d(x)
    K_maximum = calculate_K(I, x_m, FuM * FuM, alpha_y)  # 模擬示意
    K_collapse = calculate_K(I, x_m, FuM, alpha_y)

    result = {
        "direction": direction,
        "T_calculated": round(T, 3),
        "K_values": {
            "K_min": round(K_min, 3),
            "K_moderate": round(K_moderate, 3),
            "K_maximum": round(K_maximum, 3),
            "K_collapse_avoiding": round(K_collapse, 3)
        },
        "formula_steps": {
            "T_formula": f"T = {structure_type} => {round(T, 3)} s",
            "FuM_SaM_rule": rule,
            "K_moderate": f"K = {I} * ({round(SDS,3)} / {round(FuD,3)}) / (1.4 * {alpha_y})",
            "K_collapse": f"K = {I} * ({round(x_m,3)} / {round(FuM,3)}) / (1.4 * {alpha_y})"
        }
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
