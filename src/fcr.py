import numpy as np
from src.sim_config import SimulationConfig

def update_fcr_power(state: dict, k: int, df: float, df_fr: float, cfg: SimulationConfig):
    """Calculates the Primary Control Reserve (FCR) for both areas including a 1st-order delay."""
    kdroop_bw = cfg.fcr_bw_max / cfg.fcr_full_activation_df
    kdroop_fr = cfg.fcr_fr_max / cfg.fcr_full_activation_df
    # FCR for the main area (BaWü)
    p_fcr_bw_target = np.clip(-kdroop_bw * df, -cfg.fcr_bw_max, cfg.fcr_bw_max)
    state['p_fcr_bw_state'] += (cfg.dt / cfg.fcr_tau) * (p_fcr_bw_target - state['p_fcr_bw_state'])
    state['P_fcr_bw'][k] = state['p_fcr_bw_state']
    # FCR for the interconnected area (France)
    p_fcr_fr_target = np.clip(-kdroop_fr * df_fr, -cfg.fcr_fr_max, cfg.fcr_fr_max)
    state['p_fcr_fr_state'] += (cfg.dt / cfg.fcr_tau) * (p_fcr_fr_target - state['p_fcr_fr_state'])
    state['P_fcr_fr'][k] = state['p_fcr_fr_state']