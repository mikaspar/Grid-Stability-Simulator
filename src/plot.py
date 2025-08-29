import numpy as np
import matplotlib.pyplot as plt
from src.sim_config import SimulationConfig

from IPython.display import display, Markdown

def plot_results(r, title_suffix='', plot_end_time=None):
    # Vollständige Zeitreihen aus den Ergebnissen holen
    t_full = r['t']
    
    # End-Index für den Plot basierend auf der gewünschten Endzeit bestimmen
    end_idx = len(t_full)
    if plot_end_time:
        end_idx = np.searchsorted(t_full, plot_end_time, side='right')

    # Alle Zeitreihen auf den gewünschten Plot-Zeitraum zuschneiden
    t = t_full[:end_idx]
    f_bawu = r['f_bawu'][:end_idx]
    f_fr = r['f_fr'][:end_idx]
    P_k = r['P_k'][:end_idx] / 1e6
    P_f = r['P_f'][:end_idx] / 1e6
    P_g1 = r['P_g1'][:end_idx] / 1e6
    P_g2 = r['P_g2'][:end_idx] / 1e6
    P_m = r['P_mfrr'][:end_idx] / 1e6
    P_tot = r['P_total'][:end_idx] / 1e6
    P_tie = r['P_tie'][:end_idx] / 1e6
    P_fcr_bw = r['P_fcr_bw'][:end_idx] / 1e6
    P_fcr_fr = r['P_fcr_fr'][:end_idx] / 1e6
    SoC = r['SoC'][:end_idx]
    bess_share = r['bess_share_history'][:end_idx]
    soc_min, soc_max = r['soc_min'], r['soc_max']

    P_fcr_sum = P_fcr_bw + P_fcr_fr
    P_loss_vec = np.zeros_like(t)
    fault_start_index = np.searchsorted(t, r['cfg'].t_fault, side='left')
    P_loss_vec[fault_start_index:] = r['cfg'].P_loss / 1e6
    
    fig, axs = plt.subplots(7, 1, figsize=(14, 30), sharex=True)
    axs[0].plot(t, f_bawu, label='Frequenz BaWü'); axs[0].plot(t, f_fr, label='Frequenz Kuppelnetz', linestyle='--'); axs[0].axhline(50, c='k', ls=':'); axs[0].set_title('Frequenzverläufe ' + title_suffix)
    axs[1].plot(t, P_loss_vec, 'k--', lw=2, label='Leistungsverlust'); axs[1].stackplot(t, P_fcr_bw, P_tot, -P_tie, labels=['FCR (BaWü)', 'Regelleistung (aFRR+mFRR)', 'Import via Kuppel'], alpha=0.7); axs[1].set_title('Leistungsbilanz (Deckung des Ausfalls)'); axs[1].legend(loc='lower right')
    axs[2].stackplot(t, P_f, P_g1, P_g2, P_m, labels=['PSH', 'GuD 1', 'GuD 2', 'mFRR'], alpha=0.7); axs[2].plot(t, P_k, label='BESS (Gesamt)', c='red', lw=2); axs[2].plot(t, P_tot, label='Summe Regelleistung', c='k', ls='--'); axs[2].set_title('Leistungen der aFRR/mFRR-Quellen')
    axs[3].plot(t, P_fcr_bw, label='FCR BaWü'); axs[3].plot(t, P_fcr_fr, '--', label='FCR FR'); axs[3].plot(t, P_fcr_sum, lw=2, label='FCR Summe'); axs[3].set_title('Primärregelung (FCR)')
    axs[4].plot(t, 100*SoC, label='SoC'); axs[4].axhline(100*soc_min, ls=':', c='r'); axs[4].axhline(100*soc_max, ls=':', c='r'); axs[4].set_title('BESS SoC')
    axs[5].plot(t, 100*bess_share, label='aFRR-Anteil', c='purple'); axs[5].set_title('BESS aFRR-Anteil'); axs[5].set_ylim(-5, 105)
    axs[6].stackplot(t, P_fcr_sum, P_k, (P_f+P_g1+P_g2), P_m, labels=['FCR', 'BESS', 'aFRR (langsam)', 'mFRR'], alpha=0.7); axs[6].set_title('Regler-Ebenen (Summe)')
    for ax in axs: ax.grid(True); ax.legend(); ax.set_ylabel('Leistung [MW]')
    axs[0].set_ylabel('Frequenz [Hz]'); axs[4].set_ylabel('SoC [%]'); axs[5].set_ylabel('Anteil [%]')
    plt.xlabel('Zeit [s]'); plt.tight_layout(); plt.show()

def compute_kpis(r):
    """Berechnet die wesentlichen KPIs aus den Simulationsergebnissen."""
    nadir_idx = int(np.argmin(r['f_bawu']))
    ttr_val = None
    try:
        f_after_nadir = r['f_bawu'][nadir_idx:]
        recovery_relative_idx = np.where(np.abs(f_after_nadir - r['cfg'].F0) <= r['cfg'].restore_tol_hz)[0][0]
        recovery_abs_idx = nadir_idx + recovery_relative_idx
        ttr_val = r['t'][recovery_abs_idx]
        ttr_str = f"{ttr_val - r['cfg'].t_fault:.1f}"
    except IndexError:
        ttr_str = "Nicht wiederhergestellt"
    
    # NEU: Berechnung der künstlichen Trägheit durch BESS (RoCoF-Komponente)
    # Formel: H_bess = (K_RoCoF * F0) / (2 * S_base)
    H_bess_s = (r['cfg'].bess_k_rocof * r['cfg'].F0) / (2 * r['cfg'].S_base)
    
    kpis = {
        'Frequenz-Nadir [Hz]': f"{r['f_bawu'][nadir_idx]:.3f}",
        'Zeitpunkt Nadir [s]': f"{r['t'][nadir_idx]:.1f}",
        'Time to Recovery [s]': ttr_str,
        'Max. Import [MW]': f"{-np.min(r['P_tie']/1e6):.0f}",
        'Künstliche Trägheit (BESS) [s]': f"{H_bess_s:.2f}"  # Neuer KPI
    }
    return kpis, ttr_val


def analyze_and_report_facts(r, kpis):
    """
    Analysiert die Simulationsergebnisse und stellt wesentliche Fakten
    zur Frequenzregelung grafisch und textuell dar.
    """
    # Benötigte Rohdaten aus dem Ergebnis-Dictionary extrahieren
    cfg = r['cfg']
    t = r['t']
    f_bawu = r['f_bawu']
    P_tie_W = r['P_tie']
    P_fcr_bw_W = r['P_fcr_bw']
    P_total_W = r['P_total']
    
    display(Markdown("---"))
    display(Markdown("### Analyse der Simulations-Fakten"))

    # KPI-Box wird als Teil der Analyse angezeigt
    md = "**Zusammenfassende Ergebnisse (KPIs):**  \n" + "\n".join([f"- **{k}:** {v}" for k, v in kpis.items()])
    display(Markdown(md))
    display(Markdown("---"))

    # --- FAKT 1: Effektive Systemträgheit ---
    display(Markdown("**1. Effektive vs. Physikalische Trägheit (Inertia)**"))
    start_idx = np.searchsorted(t, cfg.t_fault, 'right')
    rocof_idx = np.searchsorted(t, cfg.t_fault + 1.0, 'right') # 1s nach Störung
    if rocof_idx > start_idx:
        initial_rocof = (f_bawu[rocof_idx] - f_bawu[start_idx]) / (t[rocof_idx] - t[start_idx])
        H_eff = - (cfg.P_loss * cfg.F0) / (2 * cfg.S_base * initial_rocof) if initial_rocof != 0 else float('inf')
        
        # Werte aus den KPIs holen für die Ausgabe
        H_bess_val_str = kpis.get('Künstliche Trägheit (BESS) [s]', 'N/A')
        
        print(f"Konfigurierte phys. Trägheit (H_sys):     {cfg.H_sys:.2f} s")
        print(f"Künstliche Trägheit (BESS, RoCoF):      + {H_bess_val_str} s")
        print("-------------------------------------------------")
        
        try:
            H_bess_float = float(H_bess_val_str)
            H_sum_inertia = cfg.H_sys + H_bess_float
            print(f"Summe der trägheitsbasierten Stützung:    {H_sum_inertia:.2f} s")
            print(f"Effektive Gesamträgheit (aus RoCoF gemessen): {H_eff:.2f} s\n")
            
            # Verbesserte, präzisere Erklärung
            residual_h = H_eff - H_sum_inertia
            print("Interpretation der Diskrepanz:")
            print(f"-> Die gemessene effektive Trägheit ({H_eff:.2f} s) ist höher als die Summe der physikalischen und künstlichen Trägheit ({H_sum_inertia:.2f} s).")
            print(f"-> Diese Differenz von {residual_h:.2f} s ist keine echte Trägheit. Sie ist der **rechnerische Effekt** der sofort einsetzenden, proportionalen Regelungen (FCR und BESS-Dämpfung).")
            print("-> Obwohl deren Leistung von der Frequenzabweichung (Δf) abhängt, ist ihr Beitrag direkt nach der Störung bereits messbar und verflacht den initialen RoCoF. Dieser Effekt wird bei der Berechnung der 'effektiven Trägheit' fälschlicherweise als zusätzlicher Trägheitsanteil interpretiert.")

        except (ValueError, TypeError):
             print("\n-> HINWEIS: Abweichung der effektiven Trägheit entsteht, da FCR und die BESS-Dämpfung sofort entgegenwirken.")
            
    # --- FAKT 2: Beitrag der Reserven am Frequenz-Nadir ---
    display(Markdown("\n**2. Beitrag der Reserven am Frequenz-Nadir**"))
    nadir_idx = np.argmin(f_bawu)
    p_fcr_nadir = P_fcr_bw_W[nadir_idx]
    p_afrr_nadir = P_total_W[nadir_idx]
    p_import_nadir = -P_tie_W[nadir_idx]
    total_support = p_fcr_nadir + p_afrr_nadir + p_import_nadir
    if total_support > 1e6:
        labels = ['Primärregelung (FCR)', 'Regelleistung (aFRR/mFRR)', 'Import via Kuppelleitung']
        sizes = [p_fcr_nadir, p_afrr_nadir, p_import_nadir]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        ax1.axis('equal'); ax1.set_title(f"Leistungsbeitrag zur Stützung am Nadir ({total_support/1e6:.0f} MW)")
        plt.show()
    else:
        print("Kein signifikanter Leistungs-Support am Nadir.")

    # --- FAKT 3: Visualisierung des Area Control Error (ACE) ---
    display(Markdown("\n**3. Visualisierung des Area Control Error (ACE)**"))
    df = f_bawu - cfg.F0
    ace_W = -(cfg.B_bias * df + P_tie_W)
    fig_ace, ax_ace = plt.subplots(figsize=(14, 5))
    ax_ace.plot(t, ace_W / 1e6, label='ACE')
    ax_ace.axhline(cfg.ace_thresh / 1e6, color='r', linestyle='--', label='mFRR Aktivierungsschwelle')
    ax_ace.axhline(-cfg.ace_thresh / 1e6, color='r', linestyle='--')
    ax_ace.axhline(0, color='k', linestyle=':')
    ax_ace.set_title('Verlauf des Area Control Error (ACE)'); ax_ace.set_xlabel('Zeit [s]'); ax_ace.set_ylabel('ACE [MW]')
    ax_ace.grid(True); ax_ace.legend()
    if r.get('plot_end_time'):
        ax_ace.set_xlim(0, r['plot_end_time'])
    plt.show()    
