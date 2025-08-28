# Grid-Stability-Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An interactive Python simulator to explore power grid dynamics. Tune parameters for generators, BESS, and interconnects to visualize real-time impacts on frequency and voltage stability. Analyze key metrics like frequency nadir and recovery time to understand the role of modern grid services in maintaining a stable power system.

![Simulator Interface Screenshot](docs/screenshot.png)
*(**Note:** You should replace this with an actual screenshot of your simulator in action. A GIF would be even better!)*

---

## Table of Contents
- [Key Features](#key-features)
- [Motivation](#motivation)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [How to Use](#how-to-use)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Key Features

- **📊 Interactive Simulation:** Use Jupyter widgets to change system parameters on the fly and immediately see the results.
- **🌐 Multi-Area System:** Models a two-area interconnected power system (e.g., BaWü and a neighboring grid) to show the effects of tie-line support.
- **🔋 Detailed BESS Modeling:** Simulates advanced Battery Energy Storage System (BESS) behaviors, including:
  - Fast frequency response (Damping via Droop & RoCoF).
  - Participation in secondary reserves (aFRR).
  - Configurable operating modes (Standard, Off, etc.).
  - Asymmetric ramp rates to prevent secondary frequency dips.
- **⚙️ Multi-Level Frequency Control:** Includes models for:
  - **Primary Control (FCR):** First-order droop response.
  - **Secondary Control (aFRR):** A full AGC (Automatic Generation Control) controller calculating the Area Control Error (ACE).
  - **Tertiary Control (mFRR):** Simulates the slow handover from aFRR to mFRR.
- **📈 Rich Visualization & Analysis:** Automatically generates a comprehensive set of plots and a detailed analysis of key performance indicators (KPIs), including:
  - Frequency Nadir and Time to Recovery.
  - Power balance and tie-line flows.
  - Contribution of different reserve types.
  - System inertia and Area Control Error (ACE) analysis.

## Motivation

The energy transition introduces new challenges to grid stability. With the decline of synchronous generators (which provide natural inertia) and the rise of inverter-based resources like solar, wind, and batteries, understanding grid dynamics is more crucial than ever.

This simulator was built to provide an intuitive, hands-on tool for students, power system engineers, and researchers to:
1.  **Visualize** complex concepts like inertia, droop control, and ACE.
2.  **Understand** the critical role of BESS in providing stability services.
3.  **Experiment** with different control strategies and grid configurations in a safe, sandboxed environment.

## How It Works

The simulator is built on a fundamental system dynamics model implemented in Python using NumPy.

- **System Model:** The core of the simulation is the swing equation, which models the rotational dynamics of the synchronous machines in each interconnected area. `d(Δf)/dt = (ΔP_gen - ΔP_load) / (2H)`
- **Control Layers:** Each layer of frequency control (FCR, aFRR, mFRR) is modeled as a distinct controller that responds to system deviations (like Δf and ACE) based on its specific rules, delays, and ramp rates.
- **BESS Controller:** The BESS model has a sophisticated controller that can blend fast damping actions with slower aFRR commands, all while managing its State of Charge (SoC).
- **Simulation Engine:** The simulation runs in discrete time steps (e.g., 0.1 seconds), numerically integrating the differential equations to calculate the state of the grid over time.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

You will need Python 3.x and the following libraries installed:
- `numpy`
- `matplotlib`
- `ipywidgets`
- `jupyter` (Jupyter Notebook or JupyterLab)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Grid-Stability-Simulator.git
    cd Grid-Stability-Simulator
    ```

2.  **(Recommended)** Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    A `requirements.txt` file is included for convenience.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch Jupyter:**
    ```bash
    jupyter notebook
    ```
    Or, if you prefer JupyterLab:
    ```bash
    jupyter lab
    ```
    This will open a new tab in your web browser. Navigate to and open the `simulator.ipynb` notebook file.

## How to Use

1.  Open the main simulation notebook (`.ipynb` file).
2.  Run the initial cells to define the classes and functions.
3.  Scroll down to the interactive widget panel.
4.  **Adjust the sliders and dropdowns** to configure your desired scenario (e.g., increase the power loss, reduce the BESS capacity, or change the BESS operating mode).
5.  The simulation and plots will **automatically re-run** each time you change a parameter.
6.  **Analyze the results:**
    - The **top section** displays the time-series plots (frequency, power balance, etc.). The time axis is automatically zoomed to the most relevant period around the event recovery.
    - The **bottom section** provides a detailed analysis, including the final KPIs, a breakdown of reserve contributions, and the ACE plot.

## Roadmap

This project is under active development. Future enhancements include:

-   **[ ] Voltage Stability Module:**
    -   [ ] Implement a local grid model (Thevenin equivalent).
    -   [ ] Add reactive power (Q) control capabilities to the BESS model, effectively making it a BESS+STATCOM.
    -   [ ] Simulate voltage sags/swells and analyze the BESS's corrective response.
-   **[ ] Pre-defined Scenarios:** Add buttons for one-click loading of interesting scenarios (e.g., "Low Inertia Grid," "High Renewables," "Cascading Failure").
-   **[ ] More Advanced Generator Models:** Include more detailed models for thermal power plants, including governor deadbands and generation rate constraints.
-   **[ ] Data Export:** Add functionality to export simulation results (KPIs and time-series data) to CSV or JSON files.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

Please open an issue first to discuss any major changes you would like to make.

## License

Distributed under the MIT License. See `LICENSE` for more information.
