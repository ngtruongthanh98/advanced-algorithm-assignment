import subprocess
import argparse
import os

ap = argparse.ArgumentParser()

ap.add_argument("-st", "--start_test",  type=int, default=1,
	help="input the source environment. Eg:production or staging")
ap.add_argument("-et", "--end_test", type=int, default=60,
	help="input the target environment. Eg:production or staging")
ap.add_argument("-if", "--input_folder", type=str, default="input",
	help="input the target environment. Eg:production or staging")
ap.add_argument("-olf", "--output_log_folder", type=str, default="cplex-result",
	help="input the target environment. Eg:production or staging")
ap.add_argument("-off", "--output_fig_folder", type=str, default="cplex-fig",
	help="input the target environment. Eg:production or staging")

args = vars(ap.parse_args())
start_test = args["start_test"]
end_test = args["end_test"]
input_folder = args["input_folder"]
output_log_folder = args["output_log_folder"]
output_fig_folder = args["output_fig_folder"]

os.makedirs(output_log_folder, exist_ok=True)
os.makedirs(output_fig_folder, exist_ok=True)

def run_command(command):
    subprocess.run(command.split()) # stop when error

for i in range(start_test, end_test+1):
    command = f"""
    python3 run_cplex.py 
        -in {input_folder}/input-{i:02d}.txt 
        -ol {output_log_folder}/result-{i:02d}.txt 
        -of {output_fig_folder}/fig-{i:02d}.png
    """
    run_command(command)

# python3 run_cplex.py -in input.txt -ol output.txt -of output.png