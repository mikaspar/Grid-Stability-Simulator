# -------------------- Konfiguration --------------------
class SimulationConfig:
    def __init__(self, **kwargs):
        # System
        self.S_base, self.H_sys, self.D_sys, self.F0 = 60e9, 3.5, 1.0, 50.0
        self.S_base_fr, self.H_sys_fr, self.D_sys_fr = 60e9, 4.0, 1.2
        self.T12 = kwargs.get('T12', 2000e6)
        # Störung
        self.P_loss, self.t_fault = kwargs.get('P_loss', 3_000e6), 1.0
        # aFRR-Ressourcen
        self.k_p_max, self.k_delay, self.k_ramp = kwargs.get('k_p_max', 250e6), 0.1, 1200e6
        self.f_p_max, self.f_delay, self.f_ramp = kwargs.get('f_p_max', 600e6), 10.0, 12e6
        self.gud1_p_max, self.gud1_delay, self.gud1_ramp = kwargs.get('gud1_p_max', 1_500e6), 20.0, 0.5e6
        self.gud2_p_max, self.gud2_delay, self.gud2_ramp = kwargs.get('gud2_p_max', 1_000e6), 25.0, 0.5e6
        # mFRR
        self.mfrr_p_max, self.mfrr_delay, self.mfrr_ramp = 1_500e6, kwargs.get('mfrr_delay', 300.0), 2e6
        self.restore_tol_hz = 0.02
        # AGC-Bias
        self.B_bias = 1500e6 / 0.1
        # FCR (Droop)
        self.fcr_bw_max, self.fcr_fr_max = 800e6, 1200e6
        self.fcr_full_activation_df, self.fcr_tau = 0.2, 12.0
        # BESS Dämpfung & SoC
        self.bess_k_damp, self.bess_k_rocof, self.bess_deadband = 6e9, 1e9, 0.005
        self.bess_headroom = kwargs.get('bess_headroom', 0.85)
        self.bess_E_MWh, self.bess_eff = 800.0, 0.97
        self.df_close_hz, self.bess_trim_cap, self.share_trim_max = 0.05, 100e6, 0.4
        self.df_trim_in, self.df_trim_out = 0.05, 0.07
        self.bess_min_assist_sec = kwargs.get('bess_min_assist_sec', 60.0)
        self.bess_ramp_out_mw_per_sec = kwargs.get('bess_ramp_out_mw_per_sec', 1.0)
        # Betriebsmodus für BESS
        self.bess_mode = kwargs.get('bess_mode', 'afrr_and_damping')
        # Handover aFRR→mFRR (λ)
        self.lambda_rise, self.lambda_fall = 1/300.0, 1/120.0
        self.ace_thresh, self.util_thresh = 400e6, 0.60
        self.tau_ace, self.tau_util = 30.0, 30.0
        # Simulation
        self.T, self.dt = kwargs.get('T', 3000.0), 0.1