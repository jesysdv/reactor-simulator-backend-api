import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_cors import CORS
from sympy.parsing.latex import parse_latex
from antlr4 import *


from routes.web import web_blueprint


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(web_blueprint, url_prefix="/api/v1")


@app.route("/")
def index():
    return redirect("https://vuejs-reactor-simulator-webapp.azurewebsites.net/reactor/")


@app.route("/reactores", methods=["OPTIONS"])
def test_options():
    return jsonify({}), 200


@app.route("/reactores", methods=["POST", "OPTIONS"])
def get_data():

    data = request.get_json()

    # obtener los datos enviados desde Vue.js

    # asignar los valores recibidos a las variables correspondientes
    RT = data.get("RT", 0)
    P0 = data.get("P0", 0)
    T0 = data.get("T0", 0)
    yA0 = data.get("yA0", 0)
    yB0 = data.get("yB0", 0)
    yC0 = data.get("yC0", 0)
    yD0 = data.get("yD0", 0)
    a = data.get("a", 0)
    b = data.get("b", 0)
    c = data.get("c", 0)
    d = data.get("d", 0)
    Ea = data.get("Ea", 0)
    A = data.get("A", 0)
    caidaPresion = data.get("caidaPresion", False)
    caidaTemperatura = data.get("caidaTemperatura", False)
    FT0 = data.get("FT0", 0)
    NT0 = data.get("NT0", 0)
    V = data.get("V", 0)
    CA = data.get("CA", "")
    CB = data.get("CB", "")
    CC = data.get("CC", "")
    CD = data.get("CD", "")
    ra = data.get("ra", "")
    ti = data.get("ti", 0)
    tf = data.get("tf", 0)
    dP = data.get("dP", "")
    dT = data.get("dT", "")
    CpA = data.get("CpA", 0)
    CpB = data.get("CpB", 0)
    CpC = data.get("CpC", 0)
    CpD = data.get("CpD", 0)
    HAref = data.get("HAref", 0)
    HBref = data.get("HBref", 0)
    HCref = data.get("HCref", 0)
    HDref = data.get("HDref", 0)
    Tref = data.get("Tref", 0)

    # Solo para CSTR

    X = data.get("X", 0);
    FA = data.get("FA", 0);

    xAxis = np.linspace(ti, tf)
    

    Ratm = 0.08205746

    Rjmol = 8.314472

    global variablesCSTR

    variablesCSTR = [X, FA]

    global variables

    variables = [
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ]

    if RT == 0:  # PFR - Flux
        F0 = f_solver(FT0, yA0, yB0, yC0, yD0)
        F0.append(P0)
        F0.append(T0)
        F = odeint(model_PFR_flux, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                "main_labels": ["Volume (V)", "Concentration (F)"],
                "labels": ["FA", "FB", "FC", "FD", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 1:  # PFR - Conversion
        F0 = [0, P0, T0]
        F = odeint(model_PFR_Conversion, F0, xAxis, rtol=1e-6, atol=1e-6)
        data = [[[x, y] for x, y in zip(xAxis, row)] for row in F.T]
        data = [[[x, y if y is not None and not np.isnan(y) else 0.0] for x, y in row] for row in data]  
        return jsonify(
            {
                "main_labels": ["Volume (V)", "Concentration (F)"],
                "labels": ["X", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 2:  # PBR - Flux
        F0 = f_solver(FT0, yA0, yB0, yC0, yD0)
        F0.append(P0)
        F0.append(T0)
        F = odeint(model_PBR_flux, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                "main_labels": ["Weight (W)", "Concentration (F)"],
                "labels": ["FA", "FB", "FC", "FD", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 3:  # PBR - Conversion
        F0 = [0, P0, T0]
        F = odeint(model_PBR_Conversion, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                "main_labels": ["Weight (W)", "Concentration (F)"],
                "labels": ["X", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 4:  # Batch - Flux
        F0 = f_solver(FT0, yA0, yB0, yC0, yD0)
        F0.append(P0)
        F0.append(T0)
        F = odeint(model_Batch_flux, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                "main_labels": ["Time (t)", "Concentration (F)"],
                "labels": ["NA", "NB", "NC", "ND", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 5:  # Batch - Conversion
        F0 = [0, P0, T0]
        F = odeint(model_Batch_Conversion, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                "main_labels": ["Time (t)", "Concentration (F)"],
                "labels": ["X", "P", "T"],
                "xAxis": xAxis.tolist(),
                "data": [[[x, y] for x, y in zip(xAxis, row)] for row in F.T],
            }
        )
    elif RT == 6:  # CSTR - Flux
        F0 = [0, P0, T0]
        F = odeint(model_CSTR_flux, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                F
            }
        )
    elif RT == 7:  # CSTR - Flux
        F0 = [0, P0, T0]
        F = odeint(model_CSTR_Conversion, F0, xAxis, rtol=1e-6, atol=1e-6)
        return jsonify(
            {
                F
            }
        )
    else:
        return jsonify("Error")


def f_solver(FT0, yA0, yB0, yC0, yD0):

    FA0 = FT0 * yA0
    FB0 = FT0 * yB0
    FC0 = FT0 * yC0
    FD0 = FT0 * yD0

    return [FA0, FB0, FC0, FD0]


def n_solver(NT0, yA0, yB0, yC0, yD0):

    NA0 = NT0 * yA0
    NB0 = NT0 * yB0
    NC0 = NT0 * yC0
    ND0 = NT0 * yD0

    return [NA0, NB0, NC0, ND0]


def model_PFR_flux(F, V):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    FA, FB, FC, FD, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdV = 0

    dTdV = 0

    FT = FA + FB + FC + FD

    yA = FA / FT
    yB = FB / FT
    yC = FC / FT
    yD = FD / FT

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dFAdV = rA
    dFBdV = rB
    dFCdV = rC
    dFDdV = rD

    if caidaPresion == False:
        dPdV = 0  # No Input
        P = P0
    else:
        dPdV = eval(dP)

    if caidaTemperatura == False:
        dTdV = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdV = eval(dT)

    return [dFAdV, dFBdV, dFCdV, dFDdV, dPdV, dTdV]


def model_PFR_Conversion(F, V):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    X, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdV = 0

    dTdV = 0

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dXdV = -rA / FA0

    if caidaPresion == False:
        dPdV = 0  # No Input
        P = P0
    else:
        dPdV = eval(dP)

    if caidaTemperatura == False:
        dTdV = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdV = eval(dT)

    return [dXdV, dPdV, dTdV]


def model_PBR_flux(F, W):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    FA, FB, FC, FD, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdW = 0

    dTdW = 0

    FT = FA + FB + FC + FD

    yA = FA / FT
    yB = FB / FT
    yC = FC / FT
    yD = FD / FT

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    dFAdW = rA = eval(ra)
    dFBdW = rB = rA * (b / a)
    dFCdW = rC = rA * (c / a)
    dFDdW = rD = rA * (d / a)

    if caidaPresion == False:
        dPdW = 0  # No Input
        P = P0
    else:
        dPdW = eval(dP)

    if caidaTemperatura == False:
        dTdW = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdW = eval(dT)

    return [dFAdW, dFBdW, dFCdW, dFDdW, dPdW, dTdW]


def model_PBR_Conversion(F, W):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    X, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdW = 0

    dTdW = 0

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dXdW = -rA / FA0

    if caidaPresion == False:
        dPdW = 0  # No Input
        P = P0
    else:
        dPdW = eval(dP)

    if caidaTemperatura == False:
        dTdW = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdW = eval(dT)

    return [dXdW, dPdW, dTdW]


def model_Batch_flux(F, time):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    NA, NB, NC, ND, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    NA0, NB0, NC0, ND0 = n_solver(NT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdtime = 0

    dTdtime = 0

    NT = NA + NB + NC + ND

    yA = NA / NT
    yB = NB / NT
    yC = NC / NT
    yD = ND / NT

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dNAdt = -rA * V
    dNBdt = -rB * V
    dNCdt = -rC * V
    dNDdt = -rD * V

    if caidaPresion == False:
        dPdtime = 0  # No Input
        P = P0
    else:
        dPdtime = eval(dP)

    if caidaTemperatura == False:
        dTdtime = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdtime = eval(dT)

    return [dNAdt, dNBdt, dNCdt, dNDdt, dPdtime, dTdtime]


def model_Batch_Conversion(F, time):

    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    X, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    NA0, NB0, NC0, ND0 = n_solver(NT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdtime = 0

    dTdtime = 0

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dXdtime = (-rA * V) / NA0

    if caidaPresion == False:
        dPdtime = 0  # No Input
        P = P0
    else:
        dPdtime = eval(dP)

    if caidaTemperatura == False:
        dTdtime = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdtime = eval(dT)

    return [dXdtime, dPdtime, dTdtime]


def model_CSTR_flux(F, V):
    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    (X, FA) = variablesCSTR

    FA, FB, FC, FD, P, T = F

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdV = 0

    dTdV = 0

    if caidaPresion == False:
        dPdV = 0  # No Input
        P = P0
    else:
        dPdV = eval(dP)

    if caidaTemperatura == False:
        dTdV = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdV = eval(dT)

    FT = FA + FB + FC + FD

    yA = FA / FT
    yB = FB / FT
    yC = FC / FT
    yD = FD / FT

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    dFAdV = rA = eval(ra)
    dFBdV = rB = rA * (b / a)
    dFCdV = rC = rA * (c / a)
    dFDdV = rD = rA * (d / a)

    V=FA0-FA/-rA

    return V


def model_CSTR_Conversion(F, V):
    (
        P0,
        T0,
        yA0,
        yB0,
        yC0,
        yD0,
        a,
        b,
        c,
        d,
        Ea,
        A,
        Ratm,
        Rjmol,
        caidaPresion,
        caidaTemperatura,
        FT0,
        NT0,
        V,
        CA,
        CB,
        CC,
        CD,
        ra,
        dP,
        dT,
        CpA,
        CpB,
        CpC,
        CpD,
        HAref,
        HBref,
        HCref,
        HDref,
        Tref,
    ) = variables

    (X, FA) = variablesCSTR

    yl0 = 1 - (yA0 + yB0 + yC0 + yD0)

    thetaA = yA0 / yA0
    thetaB = yB0 / yA0
    thetaC = yC0 / yA0
    thetaD = yD0 / yA0

    CT0 = P0 / (Ratm * T0)
    CA0 = (P0 * yA0) / (Ratm * T0)
    CB0 = CT0 * yB0
    CC0 = CT0 * yC0
    CD0 = CT0 * yD0

    FA0, FB0, FC0, FD0 = f_solver(FT0, yA0, yB0, yC0, yD0)

    K = A * np.exp(-Ea / (T0 * Rjmol))

    dPdV = 0

    dTdV = 0

    CA = np.abs(eval(CA))
    CB = np.abs(eval(CB))
    CC = np.abs(eval(CC))
    CD = np.abs(eval(CD))

    PA = CA
    PB = CB
    PC = CC
    PD = CD

    rA = eval(ra)
    rB = rA * (b / a)
    rC = rA * (c / a)
    rD = rA * (d / a)

    dXdV = -rA / FA0

    if caidaPresion == False:
        dPdV = 0  # No Input
        P = P0
    else:
        dPdV = eval(dP)

    if caidaTemperatura == False:
        dTdV = 0  # No Input
        T = T0
    else:
        deltaCP = (CpA*a + CpB*b + CpC*c + CpD*d)
        deltaHref = (HAref*a + HBref*b + HCref*c + HDref*d)
        deltaHrx = deltaHref + deltaCP * (T - Tref)
        HA = HAref + (CpA * (T - Tref))
        HB = HBref + (CpB * (T - Tref))
        HC = HCref + (CpC * (T - Tref))
        HD = HDref + (CpD * (T - Tref))
        dTdV = eval(dT)

    V = (FA0 * X)/-rA

    return V

if __name__ == "__main__":
    app.run(debug=True)
