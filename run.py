import sys
import os
import logging
from pathlib import PosixPath
import flywheel
import glob

print(sys.path)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('heatmap-gear')
logger.info("=======: w-score HeatMap :=======")

with flywheel.GearContext() as context:
    # Setup basic logging
    context.init_logging()
    config = context.config
    analysis_id = context.destination['id']
    gear_output_dir = PosixPath(context.output_dir)
    run_script = gear_output_dir / "heatmap_run.sh"
    output_root = gear_output_dir / analysis_id
    working_dir = PosixPath(str(output_root.resolve()) + "_work")

    # Get relevant container objects
    fw = flywheel.Client(context.get_input('api_key')['key'])
    analysis_container = fw.get(analysis_id)
    project_container = fw.get(analysis_container.parents['project'])
    session_container = fw.get(analysis_container.parent['id'])
    subject_container = fw.get(session_container.parents['subject'])

    # Get subject and session names
    session_label = session_container.label
    subject_label = subject_container.label
    prefix = "sub-{}_ses-{}".format(subject_label, session_label)

    # Inputs
    ct_image = context.get_input('cortical_thickness_image')
    label_image = context.get_input('label_image')
    antsct_output = context.get_input('antsct_output')

    # Decision tree for inputs
    is_ants = False
    if antsct_output:
        logger.info("Using antsct fw output as input.")
        antsct_output_path = PosixPath(context.get_input_path('antsct_output'))
        is_ants = True
    elif ct_image and label_image:
        logger.info("Using individually specified cortical thickness and label images.")
        ct_image_path = PosixPath(context.get_input_path('cortical_thickness_image'))
        label_image_path = PosixPath(context.get_input_path('label_image'))
    else:
        logger.warning("Insufficient inputs.")
        exit(1)

    # if antsct output, pull out ct image and label image from results
    if is_ants:
        # Unzip ants output directory
        os.system("unzip {} -d {}".format(glob.glob("/flywheel/v0/input/antsct_output/*zip")[0], "/flywheel/v0/input"))
        ct_image_path = glob.glob("/flywheel/v0/input/*CorticalThickness.nii.gz")[0]
        label_image_path = glob.glob("/flywheel/v0/input/*Schaefer2018_200Parcels17Networks.nii.gz")[0]
        t1_image_path = glob.glob("/flywheel/v0/input/*ExtractedBrain0N4.nii.gz")[0]

    # Configs
    age = config.get('patient_age')
    sex = config.get('patient_sex')
    wthresholds = config.get('wthresholds')
    
    thr_list = wthresholds.split(' ')
    print(thr_list)
    if len(thr_list) > 3:
        thr_list = thr_list[0:2]  # just pick three if user supplied more than three
    elif 1 <= len(thr_list) < 3:
        thr_list.append(str(thr_list[-1]+1))  # append the last item plus one
    elif len(thr_list) != 3:
        print("Using default thresholds.")
        thr_list = ['0.0', '0.5', '1.0']
    wthresholds = ' '.join(thr_list)

    print("PATHS")
    print(ct_image_path)
    print(label_image_path)


def write_command():

    """Write out command script."""
    with flywheel.GearContext() as context:
        cmd = ["/usr/local/bin/python",
            "/opt/scripts/run.py",
            "--label_index_file {}".format("/opt/labelset/Schaefer2018_200Parcels_17Networks_order.csv"),
            "--label_image_file {}".format(label_image_path),
            "--ct_image_file {}".format(ct_image_path),
            "--t1_image_file {}".format(t1_image_path),
            "--patient_age {}".format(str(age)),
            "--patient_sex {}".format(sex),
            "--thresholds '{}'".format(wthresholds),
            "--prefix {}".format(prefix),
            "--output_dir {}".format(gear_output_dir)
               ]
    logger.info(' '.join(cmd))
    # write command joined by spaces
    with run_script.open('w') as f:
        f.write(' '.join(cmd))

    return run_script.exists()


def main():
    os.system("bash -x /flywheel/v0/docker-env.sh")
    command_ok = write_command()
    if not command_ok:
        logger.warning("Critical error while trying to write run command.")
        return 1
    os.system("chmod +x {0}".format(run_script))
    os.system(run_script)
    # generate_Report.py
    os.system("python generate_report.py {} {}".format(prefix, gear_output_dir))

    # transfer rendered files to output directory
    os.system("cp /flywheel/v0/*.png {}".format(gear_output_dir))

    # zip up html-related files
    html_dir = os.path.join(gear_output_dir, prefix+'_report')
    os.makedirs(html_dir, exist_ok=True)
    os.system("cp /flywheel/v0/output/*.html {0}; cp /flywheel/v0/output/*.png {0}".format(html_dir))
    os.system("rm /flywheel/v0/output/*.html")
    os.chdir(html_dir)  # cd to /flywheel/v0/output/{}_report.html
    os.system("zip -r {0}/{1}_report.html.zip {2}".format(gear_output_dir, prefix, './*'))
    os.system("rm -rf /flywheel/v0/output/*_report")
    os.chdir('/flywheel/v0')
    # remove wscores text file bc redundant with csv
    os.system("rm /flywheel/v0/output/*.txt")

    return 0


if __name__ == '__main__':
    sys.exit(main())
