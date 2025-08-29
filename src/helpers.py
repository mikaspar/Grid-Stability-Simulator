import numpy as np

def initialize_state(cfg: SimulationConfig, n_steps: int):
    """Initializes and returns a dictionary holding the simulation's state variables."""
    state = {
        't': np.linspace(0, cfg.T, n_steps),
        'f_bawu': np.full(n_steps, cfg.F0), 'f_fr': np.full(n_steps, cfg.F0),
        'P_k': np.zeros(n_steps), 'P_f': np.zeros(n_steps),
        'P_g1': np.zeros(n_steps), 'P_g2': np.zeros(n_steps),
        'P_mfrr': np.zeros(n_steps), 'P_tie': np.zeros(n_steps),
        'P_fcr_bw': np.zeros(n_steps), 'P_fcr_fr': np.zeros(n_steps),
        'P_total': np.zeros(n_steps),
        'bess_share_history': np.zeros(n_steps),
        'SoC': np.zeros(n_steps),
        # Scalar variables representing the current state of power outputs
        'p_k': 0.0, 'p_f': 0.0, 'p_g1': 0.0, 'p_g2': 0.0, 'p_mfrr': 0.0,
        'p_fcr_bw_state': 0.0, 'p_fcr_fr_state': 0.0,
        # Other state variables
        'prev_df': 0.0, 'lambda_share': 0.0, 'bess_share': 1.0
    }
    state['SoC'][0] = 0.50
    state['soc_min'] = 0.5 - cfg.bess_headroom / 2
    state['soc_max'] = 0.5 + cfg.bess_headroom / 2
    return state


def update_grid_frequencies(state: dict, k: int, deltaP: float, df: float, df_fr: float, cfg: SimulationConfig):
    """Updates the grid frequencies of both areas for the next time step using the swing equation."""
    state['P_total'][k] = state['P_k'][k] + state['P_f'][k] + state['P_g1'][k] + state['P_g2'][k] + state['P_mfrr'][k]
    # Frequency dynamics for the main area (BaWü)
    P_net_bawu = -deltaP + state['P_total'][k] + state['P_fcr_bw'][k] - state['P_tie'][k]
    dfdt_bawu = (cfg.F0 / (2 * cfg.H_sys)) * (P_net_bawu / cfg.S_base) - (cfg.D_sys * df) / (2 * cfg.H_sys)
    state['f_bawu'][k+1] = state['f_bawu'][k] + dfdt_bawu * cfg.dt
    # Frequency dynamics for the interconnected area (France)
    P_net_fr = state['P_tie'][k] + state['P_fcr_fr'][k]
    dfdt_fr = (cfg.F0 / (2 * cfg.H_sys_fr)) * (P_net_fr / cfg.S_base_fr) - (cfg.D_sys_fr * df_fr) / (2 * cfg.H_sys_fr)
    state['f_fr'][k+1] = state['f_fr'][k] + dfdt_fr * cfg.dt

def finalize_arrays(state: dict, n_steps: int):
    """Copies the second-to-last value to the last for clean plotting."""
    arrays_to_finalize = [
        'P_k', 'P_f', 'P_g1', 'P_g2', 'P_mfrr', 'P_tie', 'P_fcr_bw',
        'P_fcr_fr', 'P_total', 'bess_share_history', 'SoC'
    ]
    for key in arrays_to_finalize:
        state[key][-1] = state[key][-2]