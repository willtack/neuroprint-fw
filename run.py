import sys
import os
import logging
from pathlib import PosixPath
import flywheel

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
    ct_image_path = None if ct_image is None else PosixPath(context.get_input_path('cortical_thickness_image'))
    label_image = context.get_input('label_image')
    label_image_path = None if label_image is None else PosixPath(context.get_input_path('label_image'))

    # Configs
    age = config.get('patient_age')


def write_command():

    """Write out command script."""
    with flywheel.GearContext() as context:
        cmd = ['/usr/local/bin/python',
            '/opt/scripts/run.py',
            '--label_index_file {}'.format('/opt/labelset/Schaefer2018_200Parcels_17Networks_order.csv'),
            '--label_image_file {}'.format(label_image_path),
            '--ct_image_file {}'.format(ct_image_path),
            '--patient_age {}'.format(str(age)),
            '--prefix {}'.format(prefix),
            '--output_dir {}'.format(gear_output_dir)
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
    # zip up html stuff
    os.system("zip -r --junk-paths {0}/{1}_report.html.zip {0}/*.html".format(gear_output_dir, prefix))
    return 0


if __name__ == '__main__':
    sys.exit(main())
