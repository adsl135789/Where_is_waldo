from customLib import *


# main function
def main(input_folder, dest_path):
    generate_windows(input_folder=input_folder, dest_path=dest_path)

folder = "val"
source_path = f"./labelled_data/{folder}/"
dest_path = f"./datasets/{folder}/"
# generate windows:
main(input_folder=source_path, dest_path=dest_path)  # , test_file_name="14_1696"
#  * setting a test_file_name to a file name will not train and it will test that file name
