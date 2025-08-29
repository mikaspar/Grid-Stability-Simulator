import numpy  as np

def update_bess_power_and_soc(state: dict, k: int, df: float, rocof: float, p_afrr_req: float, cfg: SimulationConfig):
    """Calculates the BESS response, including aFRR, damping, ramp rates, and SoC limits."""
    # Determine BESS's share in the aFRR task
    power_slow_sources = (state['P_f'][k-1] + state['P_g1'][k-1] + state['P_g2'][k-1]) if k > 0 else 0.0
    if (state['t'][k] - cfg.t_fault) < cfg.bess_min_assist_sec: share_target = 1.0
    elif abs(df) <= cfg.df_trim_in: share_target = cfg.share_trim_max
    elif power_slow_sources > (3 * cfg.k_p_max): share_target = 0.0
    else: share_target = 1.0
    if share_target < state['bess_share']: state['bess_share'] = max(share_target, state['bess_share'] - (1/30.0)*cfg.dt)
    elif share_target > state['bess_share']: state['bess_share'] = min(share_target, state['bess_share'] + (1/120.0)*cfg.dt)
    state['bess_share_history'][k] = state['bess_share']
    # Calculate different components of BESS power command
    p_bess_damp = -cfg.bess_k_damp * df - cfg.bess_k_rocof * rocof if abs(df) > cfg.bess_deadband else 0.0
    p_bess_afrr = np.clip(p_afrr_req, -cfg.k_p_max, cfg.k_p_max) * state['bess_share']
    if abs(df) <= cfg.df_close_hz: p_bess_afrr = np.clip(p_bess_afrr, -cfg.bess_trim_cap, cfg.bess_trim_cap)
    # Combine components based on selected operation mode
    if cfg.bess_mode == 'afrr_and_damping': p_bess_cmd = p_bess_afrr + p_bess_damp
    elif cfg.bess_mode == 'off': p_bess_cmd = 0.0
    else: p_bess_cmd = p_bess_afrr + (p_bess_damp * state['bess_share']) # Experimental mode
    # Apply SoC constraints
    soc = state['SoC'][k]
    soc_margin_up = max(0.0, state['soc_max'] - soc)
    soc_margin_dn = max(0.0, soc - state['soc_min'])
    cap_chg = cfg.k_p_max * min(1.0, soc_margin_up / (cfg.bess_headroom/2 + 1e-9))
    cap_dis = cfg.k_p_max * min(1.0, soc_margin_dn / (cfg.bess_headroom/2 + 1e-9))
    p_bess_cmd = np.clip(p_bess_cmd, -cap_chg, cap_dis)
    # Apply asymmetric ramp rates
    p_k_target = p_bess_cmd if state['t'][k] >= cfg.t_fault + cfg.k_delay else 0.0
    ramp_up_limit = cfg.k_ramp * cfg.dt
    ramp_down_limit = -cfg.bess_ramp_out_mw_per_sec * 1e6 * cfg.dt
    power_change = p_k_target - state['p_k']
    state['p_k'] += np.clip(power_change, ramp_down_limit, ramp_up_limit)
    state['P_k'][k] = np.clip(state['p_k'], -cap_chg, cap_dis)
    # Update SoC for the next step
    dE = (state['P_k'][k] / 1e6) * (cfg.dt / 3600.0) # Energy in MWh
    efficiency = cfg.bess_eff if dE >= 0 else 1 / cfg.bess_eff
    state['SoC'][k+1] = state['SoC'][k] - dE / (cfg.bess_E_MWh * efficiency)
    state['SoC'][k+1] = np.clip(state['SoC'][k+1], state['soc_min'], state['soc_max'])