#
# Writes the HTML report containing the scene image and a interactive volume viewer
#
# Author: Will Tackett 3/4/2020

# from nilearn import plotting
import jinja2
import sys
import os
import glob

# working_dir = os.getcwd()
# output_dir = os.path.join(working_dir, "output")
# inter_dir = os.path.join(output_dir, "intermediates")

prefix = sys.argv[1]
output_dir = sys.argv[2]


def generate_report():
    png_list = glob.glob('/flywheel/v0/output/*.png')
    png_list.sort()
    thr = []
    for idx, file in enumerate(png_list):
        basename = os.path.basename(file)
        png_list[idx] = basename  # change the list item to be the basename
        thr_item = basename.split("_")[-1].split(".")[0]  # parse the threshold value from the filename
        if len(thr_item) > 1:
            thr_item = thr_item[0] + '.' + thr_item[1:]
        else:
            thr_item = thr_item[0] + '.' + '0'
        thr.append(thr_item)
    # title = "Neurodegeneration Heat Map"
    main_section = base_template.render(
            subject_id=prefix,
            png_list=png_list,
            thr=thr,
    )

    # Produce and write the report to file
    with open(os.path.join(output_dir, prefix + "_report.html"), "w") as f:
        f.write(main_section)


if __name__ == "__main__":

    # Configure Jinja and ready the templates
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath="templates")
    )

    # Assemble the templates we'll use
    base_template = env.get_template("report2.html")

    generate_report()
