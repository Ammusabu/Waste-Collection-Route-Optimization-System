import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd
from datetime import datetime

# All 10 Punjab cities with their bins
cities_bins = {
    'Ludhiana': [f'Ludhiana_Bin_{i}' for i in range(1, 21)],
    'Amritsar': [f'Amritsar_Bin_{i}' for i in range(1, 21)],
    'Jalandhar': [f'Jalandhar_Bin_{i}' for i in range(1, 21)],
    'Patiala': [f'Patiala_Bin_{i}' for i in range(1, 21)],
    'Bathinda': [f'Bathinda_Bin_{i}' for i in range(1, 21)],
    'Mohali': [f'Mohali_Bin_{i}' for i in range(1, 21)],
    'Firozpur': [f'Firozpur_Bin_{i}' for i in range(1, 21)],
    'Hoshiarpur': [f'Hoshiarpur_Bin_{i}' for i in range(1, 21)],
    'Moga': [f'Moga_Bin_{i}' for i in range(1, 21)],
    'Pathankot': [f'Pathankot_Bin_{i}' for i in range(1, 21)]
}

# Create reporting database
reports_db = pd.DataFrame(columns=['city', 'bin', 'issue', 'reported_at', 'status'])

# Widgets
city_dropdown = widgets.Dropdown(
    options=list(cities_bins.keys()),
    description='Your City:',
    style={'description_width': '100px'}
)

bin_dropdown = widgets.Dropdown(description='Bin Number:')

def update_bins(change):
    bin_dropdown.options = cities_bins[change['new']]
city_dropdown.observe(update_bins, names='value')

issue_dropdown = widgets.Dropdown(
    options=['Overflowing', 'Damaged', 'Bad Odor', 'Not Collected', 'Animal Access'],
    description='Issue Type:'
)

submit_btn = widgets.Button(
    description='Report Problem',
    button_style='danger',
    icon='exclamation'
)

output = widgets.Output()

# Reporting function
def submit_report(b):
    new_report = {
        'city': city_dropdown.value,
        'bin': bin_dropdown.value,
        'issue': issue_dropdown.value,
        'reported_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'status': 'Reported'
    }

    global reports_db
    reports_db = pd.concat([reports_db, pd.DataFrame([new_report])], ignore_index=True)

    with output:
        clear_output()
        print("🗑️ Waste Problem Reported Successfully!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📍 City: {new_report['city']}")
        print(f"🆔 Bin: {new_report['bin']}")
        print(f"⚠️ Issue: {new_report['issue']}")
        print(f"⏰ Reported at: {new_report['reported_at']}")
        print("\nThank you for helping keep Punjab clean!")
        print("Municipal team will address this shortly.")

        # Show recent reports
        print("\nRecent Reports in Your Area:")
        recent = reports_db[reports_db['city'] == city_dropdown.value].tail(3)
        if not recent.empty:
            display(recent[['bin', 'issue', 'reported_at']])
        else:
            print("No other recent reports")

submit_btn.on_click(submit_report)

# Initial setup
update_bins({'new': city_dropdown.value})

# Display interface
display(widgets.VBox([
    widgets.HTML("<h2 style='color:#006400'>Punjab Waste Reporting System</h2>"),
    widgets.HTML("<i>Report overflowing or damaged waste bins in your area</i>"),
    widgets.HBox([city_dropdown, bin_dropdown]),
    issue_dropdown,
    submit_btn,
    output
]))
