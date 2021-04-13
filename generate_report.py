#
# Writes the HTML report containing the scene image and a interactive volume viewer
#
# Author: Will Tackett 3/4/2020

# from nilearn import plotting
import jinja2
import sys
import os
import glob

prefix = sys.argv[1]
output_dir = sys.argv[2]


def generate_report():
    png_list = glob.glob('/flywheel/v0/*.png')
    png_list.sort()
    thr = []
    for idx, file in enumerate(png_list):
        basename = os.path.basename(file)
        png_list[idx] = basename  # change the list item to be the basename
        thr_item = basename.split("_")[-1].split(".png")[0]  # parse the threshold value from the filename
        thr_item = str(round(float(thr_item), 2))  # round to hundredths
        thr.append(thr_item)
    thr[0] = 'auto'
    main_section = base_template.render(
            subject_id=prefix,
            png_list=png_list,
            thr=thr
    )

    # Produce and write the report to file
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(main_section)


if __name__ == "__main__":

    # Configure Jinja and ready the templates
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath="html")
    )

    # Assemble the templates we'll use
    base_template = env.get_template("report2.html")

    generate_report()
