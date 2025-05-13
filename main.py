import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.conversion.process_tree import converter as pt_converter

# 1. Load and prepare data
df = pd.read_csv(r"C:\Users\Praveen Nath\Desktop\RP14cohort.csv", sep=";")
df.columns = df.columns.str.strip()

# 2. Map columns to PM4Py standard
column_mapping = {
    'encounter_id': 'case:concept:name',
    'type_display': 'concept:name',
    'start_time': 'time:timestamp'
}
df = df.rename(columns=column_mapping)
df['time:timestamp'] = pd.to_datetime(df['time:timestamp'], errors='coerce', utc=True)
df = df.dropna(subset=['time:timestamp'])

# 3. Convert to event log (preserving all attributes)
event_log = log_converter.apply(df)

# 4. Discover process model
process_tree = inductive_miner.apply(event_log)
net, initial_marking, final_marking = pt_converter.apply(process_tree)

# 5. Create ENHANCED visualization with attributes
parameters = {
    pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png",
    # Show all attributes in labels
    "show_attributes": True,
    # Specific attributes to highlight
    "highlighted_attributes": ["observation_display", "procedure_display", "icd_10_display"],
    # Visual styling
    "bgcolor": "white",
    "font_size": "14"
}

# Create visualization with attributes
gviz = pn_visualizer.apply(
    net, 
    initial_marking, 
    final_marking,
    parameters=parameters,
    # Add log to enable attribute visualization
    log=event_log,
    # Show all variants
    variant=pn_visualizer.Variants.WO_DECORATION
)

# Save and show
pn_visualizer.save(gviz, "enhanced_process_model.png")
pn_visualizer.view(gviz)