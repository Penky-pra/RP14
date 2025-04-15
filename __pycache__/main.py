import pm4py
log = pm4py.read_xes(r"C:\\Users\\Praveen Nath\\Desktop\\2019encounter.xes.gz")
#log = pm4py.read_xes(r"C:\\Users\\Praveen Nath\\Desktop\\encounternew.xes")
dataframe = pm4py.convert_to_dataframe(log)
dfg, start_activities, end_activities = pm4py.discover_dfg(
    dataframe,
    case_id_key='case:concept:name',
    activity_key='concept:name',
    timestamp_key='time:timestamp'
)
#dfg = pm4py.discover_dfg_typed(log, case_id_key='case:concept:name', activity_key='concept:name',timestamp_key='time:timestamp',)

#This module is to view BPMN model
#import pm4py.objects.bpmn.importer as bpmn_importer
#print(dir(bpmn_importer))
#from pm4py.objects.bpmn.importer import importer as bpmn_importer
#from pm4py.objects.simulation.exporter import factory as sim_exporter
#from pm4py.objects.log.exporter.xes import factory as xes_exporter

#Load the BPMN model
#bpmn_model = pm4py.read_bpmn(r"C:\Users\Praveen Nath\Desktop\diagram2.bpmn")
#from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
#gviz = bpmn_visualizer.apply(bpmn_model)
#bpmn_visualizer.view(gviz)

# import a Petri net from a file
#net, im, fm = pm4py.read_pnml("tests/input_data/running-example.pnml")
#bpmn_graph = pm4py.convert_to_bpmn(net, im, fm)

#log_skeleton = pm4py.discover_log_skeleton(dataframe, noise_threshold=0.1, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
#net, im, fm = pm4py.discover_petri_net_alpha(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')

#This markup module need to be used with XML files for as PNML uses XML syntax, making it both human-readable and machine-readable. It allows Petri net tools to easily exchange models
#net, im, fm = pm4py.read_pnml('model.pnml')
#sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
#import pyemd
#print("pyemd is installed successfully!")
#language_log = pm4py.get_stochastic_language(log)
#print(language_log)
#net, im, fm = pm4py.read_pnml (r"C:/Users/Praveen Nath/Desktop/csvdaat/encounter.xml")
#language_model = pm4py.get_stochastic_language(net, im, fm)
#print(language_model)
#emd_distance = pm4py.compute_emd(language_log, language_model)
#print(emd_distance)

#Solves the marking equation of a Petri net. The marking equation is solved as an ILP problem. An optional transition-based cost function to minimize can be provided as well
#net, im, fm = pm4py.read_pnml (r"C:/Users/Praveen Nath/Desktop/csvdaat/encounter.xml")
#heuristic = pm4py.solve_marking_equation(net, im, fm)

print("test")