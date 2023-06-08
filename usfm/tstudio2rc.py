import sys
import os
import re
import tempfile
import zipfile
import shutil
import yaml
from obs.ResourceContainer import RC
import usfm.text2USFM as converter_script
from usfm.usfm_verses import verseCounts

book_dir_pattern = r'(.*)(\/\d{1,3})'
# source: txt2USFM-RC.py
def makeUsfmFilename(bookSlug):
    bookId = bookSlug.upper()

    if len(verseCounts) > 0:
        num = verseCounts[bookId]['usfm_number']
        filename = num + '-' + bookId + '.usfm'
    else:
        pathComponents = os.path.split(os.getcwd())   # old method
        filename = pathComponents[-1] + ".usfm"
    return filename

# constructs the manifest based on the manifest.json in project directory
def buildManifest(dir):
    rc = RC(directory=dir)
    manifest = rc.as_dict()
    manifest['dublin_core']['creator'] = 'BTT-Writer'
    projectSlug = rc.project().identifier
    project_path = "./" + makeUsfmFilename(projectSlug)
    anthology = 'ot' if verseCounts[projectSlug.upper()]['sort'] < 40 else 'nt'

    for p in manifest['projects']:
        if p['identifier'] == projectSlug:
            p['path'] = project_path      
            p['sort'] = verseCounts[projectSlug.upper()]["sort"]
            p['versification'] = 'ufw'
            p['categories'] = [str.format("bible-{}", anthology)]

    return manifest

# unzip project and returns the extracted path
def extract_tstudio(file, destination_dir):
    with zipfile.ZipFile(file, 'r') as zip:
        zip.extractall(destination_dir)

    project_directory = prepare_project_dir(destination_dir)
    print("Project at: ", project_directory)
    return project_directory

def prepare_project_dir(dir):
    root_dir = None
    
    for root, directories, files in os.walk(dir):
        # Deletes .git folder
        if '.git' in directories:
            git_dir_path = os.path.join(root, '.git')
            shutil.rmtree(git_dir_path)
            directories.remove('.git')  # Skip further traversal of the .git directory

        # Returns the path to the resource container root
        for directory_name in directories:
            dir = os.path.join(root, directory_name)
            dir = os.path.normpath(dir).replace("\\", "/")
            match = re.search(book_dir_pattern, dir)
            if match:
                root_dir = match.group(1)
                break

    return root_dir

def clear_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_directory(file_path)
            os.rmdir(file_path)

def convert(input_file, output_dir):
    # input_file = r"E:\miscs\writer\aaa_eph_text_reg.tstudio"
    # output_dir = r"E:\Projects\tstudio2rc\out"
    clear_directory(output_dir)
    temp_dir = tempfile.mkdtemp()

    rc_convert_dir = os.path.join(output_dir, "rc_dir")
    output_file = os.path.join(output_dir, "RC")
    manifest_file = os.path.join(rc_convert_dir, "manifest.yaml")
    os.makedirs(rc_convert_dir)

    source_dir = extract_tstudio(input_file, temp_dir)
    converter_script.source_dir = source_dir
    converter_script.target_dir = rc_convert_dir
    converter_script.convertFolder(source_dir)

    # write manifest.yaml
    manifest = buildManifest(source_dir)
    with open(manifest_file, 'w') as file:
        yaml.dump(manifest, file)

    shutil.make_archive(output_file, 'zip', rc_convert_dir)
    # clear_directory(temp_dir) # race-condition error: deleting while opened
    
    output_file_name = os.path.splitext(os.path.basename(input_file))[0] + ".orature"
    orature_file = os.path.join(os.path.dirname(rc_convert_dir), output_file_name)

    os.rename(output_file + ".zip", orature_file)


def convertDir(input_dir, output_dir):
    clear_directory(output_dir)
    temp_dir = tempfile.mkdtemp()

    rc_convert_dir = os.path.join(output_dir, "rc_dir")
    output_file = os.path.join(output_dir, "RC")
    manifest_file = os.path.join(rc_convert_dir, "manifest.yaml")
    os.makedirs(rc_convert_dir)

    converter_script.source_dir = input_dir
    converter_script.target_dir = rc_convert_dir
    converter_script.convertFolder(input_dir)

    # write manifest.yaml
    manifest = buildManifest(input_dir)
    with open(manifest_file, 'w') as file:
        yaml.dump(manifest, file)

    shutil.make_archive(output_file, 'zip', rc_convert_dir)
    # clear_directory(temp_dir) # race-condition error: deleting while opened
    
    output_file_name = os.path.basename(input_dir) + ".orature"
    orature_file = os.path.join(os.path.dirname(rc_convert_dir), output_file_name)

    os.rename(output_file + ".zip", orature_file)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py [tstudio_file_path] [output_directory]")
#         exit()

#     input_path = sys.argv[1]
#     output_dir = sys.argv[2]

#     if os.path.isdir(input_path):
#         convertDir(input_path, output_dir)
#     else:
#         convert(input_path, output_dir)
    
#     print("Done!")
