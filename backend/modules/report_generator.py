def build_report(insights):
    report = "\n".join(insights)
    with open("analysis_report.txt","w") as f:
        f.write(report)
    return "analysis_report.txt"