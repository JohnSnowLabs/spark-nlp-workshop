import pandas as pd, csv, numpy as np, re
import matplotlib.pyplot as plt

def parse_logfile(path):
    logs = csv.reader(open(path,"r"),delimiter="\t")
    data = []
    avg_data = []
    for row in logs:
        if row and row[0].startswith("Name of the selected graph"):
            graph = row[0].split("/")[-1]
        if row and row[0].startswith("Epoch"):
            current_epoch = int(re.findall(r'\d+', row[0])[0])
        if row and row[0].startswith("Quality on"):
            set_idx = row[0].split(" ")[2]
        if row and row[0][:2] in ["B-","I-"]:
            data.append((current_epoch, set_idx, row[0], row[0].split("-")[-1], *np.array(row[1:]).astype(np.float)))
        if row and row[0][:13]=="Macro-average":
            data_i = [d.split(": ")[-1] for d in row[1].split("\t")[-1].split(", ")]
            avg_data.append((current_epoch, set_idx, row[0], *np.array(data_i).astype(np.float)))
        if row and row[0][:13]=="Micro-average":
            data_i = [d.split(": ")[-1] for d in row[1].split("\t")[-1].split(", ")]
            avg_data.append((current_epoch, set_idx, row[0], *np.array(data_i).astype(np.float)))
    return  (pd.DataFrame(data, columns=["epoch","set","label","entity","tp","fp","fn","prec","rec","f1"]), 
            pd.DataFrame(avg_data, columns=["epoch","set","metric","prec","rec","f1"]), 
            graph)

def aggregate_entities(metrics):
    metrics["entity"] = metrics.label.apply(lambda x: x.split("-")[-1])
    chart_metrics = metrics[["epoch","set","entity","tp","fp","fn"]].groupby(["epoch","entity","set"]).sum()
    chart_metrics["prec"] = chart_metrics.tp / (chart_metrics.tp + chart_metrics.fp)
    chart_metrics["rec"] = chart_metrics.tp / (chart_metrics.tp + chart_metrics.fn)
    chart_metrics["f1"] = 2*chart_metrics.prec*chart_metrics.rec / (chart_metrics.prec + chart_metrics.rec)
    return chart_metrics

def get_charts (log_file, threshold=0.0):

    metrics, avg_metrics, graph = parse_logfile(log_file)

    chart_metrics = aggregate_entities(metrics)
    avg_metrics = avg_metrics.replace({"Macro-average":"macro_avg", "Micro-average":"micro_avg"})

    fig, axs = plt.subplots(3, 2, figsize=(20,20))
    fig.suptitle(graph)
    for j,s in enumerate(["validation","test"]):
        try:
            for i, m in enumerate(["prec","rec","f1"]):
                avg_metrics[m] = avg_metrics[m].astype(np.float)
                cdf = avg_metrics[avg_metrics.set==s].reset_index()[["epoch","metric", m]].pivot(index="epoch",columns="metric",values=m).reset_index().fillna(0)
                axs[i][j].title.set_text(s+" - "+m) 
                cdf.plot(x="epoch", ax=axs[i][j])
        except:
            pass
        
            
    fig, axs = plt.subplots(3, 2, figsize=(20,20))
    fig.suptitle(graph)
    for j,s in enumerate(["validation","test"]):
        try:
            for i, m in enumerate(["prec","rec","f1"]):
                cmr = chart_metrics.reset_index()
                cdf = cmr[(cmr.set==s)&(cmr.f1>threshold)].reset_index()[["epoch","entity", m]].pivot(index="epoch",columns="entity",values=m).reset_index()
                axs[i][j].title.set_text(m) 
                cdf.plot(x="epoch", ax=axs[i][j])
        except:
            pass


def loss_plot(log_path) :
    with open(log_path, "r", encoding="utf-8") as f :
        lines = f.readlines()

    loss = [line.split()[6] for line in lines if line.startswith("Epoch") and line.split()[6] != "size:"]

    
    epoch = []
    losses = []
    for x, y in enumerate(loss, 1):
        epoch.append(x)
        losses.append(float(y))
        
    plt.subplots(1,1, figsize=(8,8))
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.title('Loss Plot')
    plt.plot(epoch[::-1], losses[::-1])
    plt.show()
# how to run

# get_charts("i2b2_ner_logs_combinedData_e8.txt")