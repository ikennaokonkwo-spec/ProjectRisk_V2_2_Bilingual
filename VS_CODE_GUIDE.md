# Project Risk Analysis V2 — VS Code Guide

## Windows: simplest route

1. Extract this ZIP to a normal folder, for example:
   `C:\ProjectRisk_V2_VSCode`

2. Open **Visual Studio Code**.

3. Select **File → Open Folder** and open the extracted `ProjectRisk_V2_VSCode` folder.

4. Open the VS Code integrated terminal:
   **Terminal → New Terminal**

5. Run:
   ```powershell
   .\setup_windows.bat
   ```

6. When installation finishes, select the Python interpreter if VS Code asks:
   `.venv\Scripts\python.exe`

7. Start the application with either:
   ```powershell
   .\run_app_windows.bat
   ```
   or:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app2_2.py
   ```

8. Streamlit will display a local address, normally `http://localhost:8501`.
   Open it in the browser if it does not open automatically.

## Run from the VS Code menu

After setup, press **Ctrl+Shift+B** to run the default task:
`Run Project Risk Analysis V2`.

For debugging, open **Run and Debug** and choose:
`Streamlit: Project Risk Analysis V2`.

## Run verification tests

From the terminal:
```powershell
.\.venv\Scripts\python.exe run_tests.py
```

Expected final message:
`ALL V2.2 TESTS PASSED`

## Application input

The application already includes:
`project_risk_template_v2_2.xlsx`

You can download the template from inside the Streamlit interface, populate it, upload it, validate it, and run the analysis.

## Main project structure

- `app2_2.py` — Streamlit interface and workflow
- `core/validation.py` — input validation
- `core/distributions.py` — stochastic distributions
- `core/network.py` — CPM/network calculations
- `core/simulation.py` — Monte Carlo simulation
- `core/risk_analysis.py` — project/risk/criticality analysis
- `core/risk_portrait.py` — cumulative Risk Portrait
- `core/treatment.py` — treatment and re-simulation
- `data_io/input_reader.py` — Excel reading
- `data_io/model_adapter.py` — workbook-to-model conversion
- `data_io/export_results.py` — downloadable results package
- `tests/` — computational and integration tests

Do not run `app2_2.py` using the ordinary Python Run button as if it were a console script.
The application is a Streamlit application and should be started with:
`python -m streamlit run app2_2.py`
or the included VS Code task/batch file.
