import numpy as np

# -------------------- AGC (aFRR) --------------------
class AGC_Controller:
    def __init__(self, dt, P_max_discharge, P_max_charge, B_bias, Ki=0.08):
        self.Ki = Ki
        self.dt = dt
        self.P_max_discharge = P_max_discharge
        self.P_max_charge = P_max_charge
        self.B_bias = B_bias
        self.integral_term = 0.0

    def step(self, df, dP_tie):
        ACE = -(self.B_bias * df + dP_tie)
        self.integral_term += self.Ki * ACE * self.dt
        self.integral_term = np.clip(self.integral_term, -self.P_max_charge, self.P_max_discharge)
        return self.integral_term


def update_afrr_mfrr_logic(state: dict, k: int, df: float, P_tie_k: float, agc: AGC_Controller, total_afrr_cap: float, cfg: SimulationConfig):
    """Handles the secondary (aFRR) and tertiary (mFRR) control logic, including the handover."""
    # Get raw aFRR power request from the AGC
    p_afrr_raw = agc.step(df, P_tie_k)
    # Determine the handover state (lambda) between aFRR and mFRR
    P_afrr_now = state['P_k'][k-1] + state['P_f'][k-1] + state['P_g1'][k-1] + state['P_g2'][k-1] if k > 0 else 0
    freq_stable = abs(df) <= cfg.restore_tol_hz
    is_sustained = (abs(agc.integral_term) > cfg.ace_thresh) or (abs(P_afrr_now) / total_afrr_cap > cfg.util_thresh)
    if freq_stable and is_sustained and (state['t'][k] - cfg.t_fault >= cfg.mfrr_delay):
        state['lambda_share'] = min(1.0, state['lambda_share'] + cfg.lambda_rise * cfg.dt)
    else:
        state['lambda_share'] = max(0.0, state['lambda_share'] - cfg.lambda_fall * cfg.dt)
    # Apply handover logic to aFRR and mFRR requests
    p_afrr_req = (1.0 - state['lambda_share']) * p_afrr_raw
    p_mfrr_target = state['lambda_share'] * min(cfg.P_loss, cfg.mfrr_p_max)
    # Ramp the mFRR power and perform bumpless transfer by adjusting AGC integral
    p_mfrr_change = np.clip(p_mfrr_target - state['p_mfrr'], 0.0, cfg.mfrr_ramp * cfg.dt)
    state['p_mfrr'] += p_mfrr_change
    state['P_mfrr'][k] = state['p_mfrr']
    if k > 0:
        agc.integral_term -= (state['P_mfrr'][k] - state['P_mfrr'][k-1])
    return p_afrr_req

def dispatch_conventional_afrr(state: dict, k: int, p_afrr_req: float, cfg: SimulationConfig):
    """Dispatches the remaining aFRR request to slower, conventional power plants."""
    rem_req = p_afrr_req - state['P_k'][k]
    rem_pos = max(0.0, rem_req) # Only handle positive requests (power injection)
    # Dispatch to Pumped Storage Hydro (PSH)
    p_f_target = min(rem_pos, cfg.f_p_max) if state['t'][k] >= cfg.t_fault + cfg.f_delay else 0.0
    state['p_f'] += np.clip(p_f_target - state['p_f'], -cfg.f_ramp * cfg.dt, cfg.f_ramp * cfg.dt)
    state['P_f'][k] = state['p_f']
    rem_pos -= state['p_f']
    # Dispatch to Gas Turbine 1
    p_g1_target = min(rem_pos, cfg.gud1_p_max) if state['t'][k] >= cfg.t_fault + cfg.gud1_delay else 0.0
    state['p_g1'] += np.clip(p_g1_target - state['p_g1'], -cfg.gud1_ramp * cfg.dt, cfg.gud1_ramp * cfg.dt)
    state['P_g1'][k] = state['p_g1']
    rem_pos -= state['p_g1']
    # Dispatch to Gas Turbine 2
    p_g2_target = min(rem_pos, cfg.gud2_p_max) if state['t'][k] >= cfg.t_fault + cfg.gud2_delay else 0.0
    state['p_g2'] += np.clip(p_g2_target - state['p_g2'], -cfg.gud2_ramp * cfg.dt, cfg.gud2_ramp * cfg.dt)
    state['P_g2'][k] = state['p_g2']
