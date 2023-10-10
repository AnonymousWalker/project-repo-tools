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

class TstudioToRC:

    def __init__(self) -> None:
        self.book_dir_pattern = r'(.*)(\/\d{1,3})'

    # source: txt2USFM-RC.py
    def makeUsfmFilename(self, bookSlug):
        bookId = bookSlug.upper()

        if len(verseCounts) > 0:
            num = verseCounts[bookId]['usfm_number']
            filename = num + '-' + bookId + '.usfm'
        else:
            pathComponents = os.path.split(os.getcwd())   # old method
            filename = pathComponents[-1] + ".usfm"
        return filename

    # constructs the manifest based on the manifest.json in project directory
    def buildManifest(self, dir):
        rc = RC(directory=dir)
        manifest = rc.as_dict()
        manifest['dublin_core']['creator'] = 'BTT-Writer'
        projectSlug = rc.project().identifier
        project_path = "./" + self.makeUsfmFilename(projectSlug)
        anthology = 'ot' if verseCounts[projectSlug.upper()]['sort'] < 40 else 'nt'

        for p in manifest['projects']:
            if p['identifier'] == projectSlug:
                p['path'] = project_path      
                p['sort'] = verseCounts[projectSlug.upper()]["sort"]
                p['versification'] = 'ufw'
                p['categories'] = [str.format("bible-{}", anthology)]

        return manifest

    # unzip project and returns the extracted path
    def extract_tstudio(self, file, destination_dir):
        with zipfile.ZipFile(file, 'r') as zip:
            zip.extractall(destination_dir)

        project_directory = self.prepare_project_dir(destination_dir)
        return project_directory

    def prepare_project_dir(self, dir):
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
                match = re.search(self.book_dir_pattern, dir)
                if match:
                    root_dir = match.group(1)
                    break

        return root_dir

    def clear_directory(self, directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                self.clear_directory(file_path)
                os.rmdir(file_path)

    def convert(self, input_file, output_dir, manifest=None):
        temp_dir = tempfile.mkdtemp()

        file_name_no_ext = os.path.splitext(os.path.basename(input_file))[0]
        rc_convert_dir = os.path.join(output_dir, file_name_no_ext)
        output_file = os.path.join(output_dir, "RC")
        manifest_file = os.path.join(rc_convert_dir, "manifest.yaml")
        os.makedirs(rc_convert_dir)

        source_dir = self.extract_tstudio(input_file, temp_dir)
        converter_script.source_dir = source_dir
        converter_script.target_dir = rc_convert_dir
        converter_script.convertFolder(source_dir)

        # manifest.yaml
        if manifest == None:
            manifest = self.buildManifest(source_dir)
        with open(manifest_file, 'w') as file:
            yaml.dump(manifest, file)

        shutil.make_archive(output_file, 'zip', rc_convert_dir)
        # clear_directory(temp_dir) # race-condition error: deleting while opened
        
        output_file_name = file_name_no_ext + ".orature"
        orature_file = os.path.join(os.path.dirname(rc_convert_dir), output_file_name)

        os.rename(output_file + ".zip", orature_file)


    def convertDir(self, input_dir, output_dir, manifest=None):
        rc_convert_dir = os.path.join(output_dir, os.path.basename(input_dir))
        output_file = os.path.join(output_dir, "RC")
        manifest_file = os.path.join(rc_convert_dir, "manifest.yaml")
        os.makedirs(rc_convert_dir)

        converter_script.source_dir = input_dir
        converter_script.target_dir = rc_convert_dir
        converter_script.convertFolder(input_dir)

        # manifest.yaml
        if manifest == None or manifest == '':
            manifest = self.buildManifest(input_dir)
        with open(manifest_file, 'w') as file:
            yaml.dump(manifest, file)

        shutil.make_archive(output_file, 'zip', rc_convert_dir)
        # clear_directory(temp_dir) # race-condition error: deleting while opened
        
        output_file_name = os.path.basename(input_dir) + ".orature"
        orature_file = os.path.join(os.path.dirname(rc_convert_dir), output_file_name)

        os.rename(output_file + ".zip", orature_file)

    def previewManifest(self, input_file):
        temp_dir = tempfile.mkdtemp()
        source_dir = self.extract_tstudio(input_file, temp_dir)
        manifest = self.buildManifest(source_dir)
        return yaml.dump(manifest, default_flow_style=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py [tstudio_file_path] [output_directory]")
        exit()

    input_path = sys.argv[1]
    output_dir = sys.argv[2]

    converter = TstudioToRC()

    if os.path.isdir(input_path):
        converter.convertDir(input_path, output_dir)
    else:
        converter.convert(input_path, output_dir)
    
    print("Done!")
